# 💳 API Endpoints para Mercado Pago
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import Dict, Any
from datetime import datetime, date, timedelta
import logging
import json

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.suscripcion import Suscripcion
from app.models.plan_catalogo import PlanCatalogo
from app.models.user import User
from app.services.mercadopago_service import mercadopago_service

logger = logging.getLogger("galloapp.mercadopago")
router = APIRouter(prefix="/mercadopago", tags=["💳 Mercado Pago"])

# ========================================
# ENDPOINTS DE PAGO
# ========================================

@router.post("/crear-preferencia")
async def crear_preferencia_pago(
    plan_codigo: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    📱 Crear preferencia de pago en Mercado Pago
    
    Genera un link de pago para que el usuario complete
    la transacción en el checkout de Mercado Pago.
    """
    try:
        # Obtener usuario
        usuario = db.query(User).filter(User.id == current_user_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Obtener plan
        plan = db.query(PlanCatalogo).filter(
            and_(
                PlanCatalogo.codigo == plan_codigo.lower(),
                PlanCatalogo.activo == True,
                PlanCatalogo.precio > 0
            )
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan '{plan_codigo}' no encontrado o no disponible"
            )
        
        # Verificar si ya tiene suscripción activa de este plan
        suscripcion_activa = db.query(Suscripcion).filter(
            and_(
                Suscripcion.user_id == current_user_id,
                Suscripcion.plan_type == plan_codigo.lower(),
                Suscripcion.status == "active"
            )
        ).first()
        
        if suscripcion_activa and suscripcion_activa.esta_activa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya tienes una suscripción activa del plan {plan.nombre}"
            )
        
        # Crear preferencia en Mercado Pago
        resultado = mercadopago_service.crear_preferencia_pago(
            user_id=current_user_id,
            plan_codigo=plan.codigo,
            plan_nombre=plan.nombre,
            monto=float(plan.precio),
            user_email=usuario.email,
            user_nombre=usuario.profile.nombre_completo if usuario.profile else "Usuario"
        )
        
        if not resultado.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creando preferencia: {resultado.get('error')}"
            )
        
        # Crear suscripción pendiente
        nueva_suscripcion = Suscripcion(
            user_id=current_user_id,
            plan_type=plan.codigo,
            plan_name=plan.nombre,
            precio=plan.precio,
            status="pending",  # Pendiente hasta que se confirme el pago
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=plan.duracion_dias) if plan.duracion_dias else None,
            gallos_maximo=plan.gallos_maximo,
            topes_por_gallo=plan.topes_por_gallo,
            peleas_por_gallo=plan.peleas_por_gallo,
            vacunas_por_gallo=plan.vacunas_por_gallo,
            preference_id=resultado["preference_id"],
            external_reference=resultado["referencia"],
            payment_status="pending"
        )
        
        db.add(nueva_suscripcion)
        db.commit()
        db.refresh(nueva_suscripcion)
        
        logger.info(f"✅ Preferencia creada para usuario {current_user_id}, plan {plan.codigo}")
        
        return {
            "success": True,
            "preference_id": resultado["preference_id"],
            "init_point": resultado["init_point"],
            "suscripcion_id": nueva_suscripcion.id,
            "plan": {
                "codigo": plan.codigo,
                "nombre": plan.nombre,
                "precio": float(plan.precio),
                "duracion_dias": plan.duracion_dias
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creando preferencia: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear preferencia de pago"
        )

# ========================================
# WEBHOOK DE MERCADO PAGO
# ========================================

@router.post("/webhook")
async def webhook_mercadopago(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    🔔 Webhook de Mercado Pago
    
    Recibe notificaciones de pagos aprobados, rechazados, etc.
    Este endpoint es llamado automáticamente por Mercado Pago.
    """
    try:
        # Obtener datos del webhook
        body = await request.json()
        headers = dict(request.headers)
        
        logger.info(f"📬 Webhook recibido de Mercado Pago: {body}")
        
        # Validar firma del webhook (seguridad)
        x_signature = headers.get("x-signature")
        x_request_id = headers.get("x-request-id")
        
        if x_signature and x_request_id:
            data_id = body.get("data", {}).get("id") or body.get("id")
            
            if not mercadopago_service.validar_firma_webhook(x_signature, x_request_id, str(data_id)):
                logger.error("❌ Firma del webhook inválida - Posible intento de fraude")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Firma del webhook inválida"
                )
        
        # Procesar webhook
        resultado = mercadopago_service.procesar_webhook(body)
        
        if not resultado.get("success"):
            logger.error(f"❌ Error procesando webhook: {resultado.get('error')}")
            return {"status": "error", "message": resultado.get("error")}
        
        # Si es un pago aprobado, activar suscripción
        if resultado.get("debe_activar_suscripcion"):
            payment_id = resultado["payment_id"]
            external_reference = resultado.get("external_reference")
            
            # Buscar suscripción por preference_id o external_reference
            suscripcion = db.query(Suscripcion).filter(
                Suscripcion.external_reference == external_reference
            ).first()
            
            if not suscripcion:
                logger.warning(f"⚠️ Suscripción no encontrada para referencia: {external_reference}")
                return {"status": "ok", "message": "Suscripción no encontrada"}
            
            # Actualizar suscripción
            suscripcion.status = "active"
            suscripcion.payment_id = payment_id
            suscripcion.payment_status = resultado["status"]
            suscripcion.payment_status_detail = resultado.get("status_detail")
            suscripcion.payment_method = resultado.get("metodo_pago")
            suscripcion.transaction_amount = resultado.get("monto")
            suscripcion.fecha_pago = datetime.fromisoformat(resultado["fecha_aprobacion"]) if resultado.get("fecha_aprobacion") else datetime.now()
            suscripcion.mercadopago_data = json.dumps(resultado)
            
            # Desactivar otras suscripciones del mismo usuario
            db.query(Suscripcion).filter(
                and_(
                    Suscripcion.user_id == suscripcion.user_id,
                    Suscripcion.id != suscripcion.id,
                    Suscripcion.status == "active"
                )
            ).update({"status": "inactive"})
            
            db.commit()
            
            logger.info(f"✅ Suscripción {suscripcion.id} activada para usuario {suscripcion.user_id}")
            
            # TODO: Enviar notificación al usuario
            # TODO: Enviar email de confirmación
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"❌ Error en webhook: {e}")
        return {"status": "error", "message": str(e)}

# ========================================
# ENDPOINTS DE CONSULTA
# ========================================

@router.get("/estado-pago/{payment_id}")
async def consultar_estado_pago(
    payment_id: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🔍 Consultar estado de un pago
    
    Permite al usuario verificar el estado de su pago
    directamente desde Mercado Pago.
    """
    try:
        # Verificar que el pago pertenece al usuario
        suscripcion = db.query(Suscripcion).filter(
            and_(
                Suscripcion.payment_id == payment_id,
                Suscripcion.user_id == current_user_id
            )
        ).first()
        
        if not suscripcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado"
            )
        
        # Consultar estado en Mercado Pago
        payment_info = mercadopago_service.obtener_pago(payment_id)
        
        if not payment_info:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error consultando estado del pago"
            )
        
        return {
            "success": True,
            "payment_id": payment_id,
            "status": payment_info["status"],
            "status_detail": payment_info["status_detail"],
            "monto": payment_info["transaction_amount"],
            "metodo_pago": payment_info["payment_method_id"],
            "fecha_creacion": payment_info["date_created"],
            "fecha_aprobacion": payment_info.get("date_approved"),
            "suscripcion": {
                "id": suscripcion.id,
                "plan": suscripcion.plan_name,
                "status": suscripcion.status,
                "fecha_inicio": suscripcion.fecha_inicio.isoformat(),
                "fecha_fin": suscripcion.fecha_fin.isoformat() if suscripcion.fecha_fin else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error consultando estado de pago: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al consultar estado del pago"
        )

@router.get("/mi-suscripcion")
async def obtener_mi_suscripcion(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    📋 Obtener suscripción activa del usuario
    """
    try:
        suscripcion = db.query(Suscripcion).filter(
            and_(
                Suscripcion.user_id == current_user_id,
                Suscripcion.status == "active"
            )
        ).order_by(desc(Suscripcion.created_at)).first()
        
        if not suscripcion:
            return {
                "success": True,
                "tiene_suscripcion": False,
                "plan": "gratuito"
            }
        
        return {
            "success": True,
            "tiene_suscripcion": True,
            "suscripcion": {
                "id": suscripcion.id,
                "plan_type": suscripcion.plan_type,
                "plan_name": suscripcion.plan_name,
                "precio": float(suscripcion.precio),
                "status": suscripcion.status,
                "fecha_inicio": suscripcion.fecha_inicio.isoformat(),
                "fecha_fin": suscripcion.fecha_fin.isoformat() if suscripcion.fecha_fin else None,
                "dias_restantes": suscripcion.dias_restantes,
                "payment_method": suscripcion.payment_method,
                "limites": {
                    "gallos_maximo": suscripcion.gallos_maximo,
                    "topes_por_gallo": suscripcion.topes_por_gallo,
                    "peleas_por_gallo": suscripcion.peleas_por_gallo,
                    "vacunas_por_gallo": suscripcion.vacunas_por_gallo
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo suscripción: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener suscripción"
        )
