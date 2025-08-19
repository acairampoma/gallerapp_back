# 💳 API Endpoints para Pagos - Sistema QR Yape
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import base64
import cloudinary.uploader

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.pago_pendiente import PagoPendiente, EstadoPago
from app.models.plan_catalogo import PlanCatalogo
from app.models.notificacion_admin import NotificacionAdmin
from app.schemas.pago import (
    QRYapeRequest, 
    QRYapeResponse,
    ConfirmarPagoRequest,
    ConfirmarPagoResponse,
    PagoResponse,
    EstadisticasPagos
)
from app.services.qr_service import generar_qr_pago, validar_monto_yape, obtener_instrucciones_pago
from app.services.fcm_suscripciones_service import FCMNotificationService

# Configurar logger
logger = logging.getLogger("galloapp.pagos")
router = APIRouter(prefix="/pagos", tags=["💳 Pagos"])

# ========================================
# ENDPOINTS DE GENERACIÓN QR
# ========================================

@router.post("/generar-qr", response_model=QRYapeResponse)
async def generar_qr_yape(
    request: QRYapeRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    📱 Generar código QR para pago con Yape
    
    Crea un código QR personalizado para que el usuario
    pueda pagar con Yape y activar su plan premium.
    """
    try:
        # Verificar que el plan existe y es de pago
        plan = db.query(PlanCatalogo).filter(
            and_(
                PlanCatalogo.codigo == request.plan_codigo,
                PlanCatalogo.activo == True,
                PlanCatalogo.precio > 0
            )
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan '{request.plan_codigo}' no encontrado o es gratuito"
            )
        
        # Validar monto para Yape
        if not validar_monto_yape(plan.precio):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Monto S/.{plan.precio} fuera del rango permitido por Yape (S/.1 - S/.500)"
            )
        
        # Verificar si ya existe un pago pendiente reciente
        pago_existente = db.query(PagoPendiente).filter(
            and_(
                PagoPendiente.user_id == current_user_id,
                PagoPendiente.plan_codigo == request.plan_codigo,
                PagoPendiente.estado.in_([EstadoPago.PENDIENTE, EstadoPago.VERIFICANDO]),
                PagoPendiente.created_at >= datetime.utcnow() - timedelta(hours=2)
            )
        ).first()
        
        if pago_existente:
            # Retornar el QR existente si aún es válido
            return QRYapeResponse(
                pago_id=pago_existente.id,
                qr_data=pago_existente.qr_data,
                qr_url=pago_existente.qr_url,
                monto=pago_existente.monto,
                plan_nombre=plan.nombre,
                instrucciones=obtener_instrucciones_pago()
            )
        
        # Generar nuevo QR y pago
        referencia, qr_data, qr_url = await generar_qr_pago(
            user_id=current_user_id,
            plan_codigo=request.plan_codigo,
            monto=plan.precio
        )
        
        # Crear registro de pago pendiente
        nuevo_pago = PagoPendiente(
            user_id=current_user_id,
            plan_codigo=request.plan_codigo,
            monto=plan.precio,
            qr_data=qr_data,
            qr_url=qr_url,
            estado=EstadoPago.PENDIENTE
        )
        
        db.add(nuevo_pago)
        db.commit()
        db.refresh(nuevo_pago)
        
        logger.info(f"QR Yape generado para usuario {current_user_id}, plan {request.plan_codigo}, pago_id {nuevo_pago.id}")
        
        return QRYapeResponse(
            pago_id=nuevo_pago.id,
            qr_data=qr_data,
            qr_url=qr_url,
            monto=plan.precio,
            plan_nombre=plan.nombre,
            instrucciones=obtener_instrucciones_pago()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando QR Yape para usuario {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al generar código QR"
        )

# ========================================
# ENDPOINTS DE CONFIRMACIÓN
# ========================================

@router.post("/confirmar", response_model=ConfirmarPagoResponse)
async def confirmar_pago_realizado(
    request: ConfirmarPagoRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    ✅ Confirmar que el pago fue realizado
    
    El usuario confirma que completó el pago en Yape
    y opcionalmente sube el comprobante para verificación.
    """
    try:
        # Buscar el pago
        pago = db.query(PagoPendiente).filter(
            and_(
                PagoPendiente.id == request.pago_id,
                PagoPendiente.user_id == current_user_id
            )
        ).first()
        
        if not pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado"
            )
        
        if not pago.puede_verificar:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El pago ya está {pago.estado}"
            )
        
        # Subir comprobante si se proporciona
        comprobante_subido = False
        if request.comprobante_base64:
            try:
                # Decodificar y subir a Cloudinary
                comprobante_bytes = base64.b64decode(request.comprobante_base64)
                
                upload_result = cloudinary.uploader.upload(
                    comprobante_bytes,
                    folder=f"galloapp/pagos/comprobantes/user_{current_user_id}",
                    public_id=f"comprobante_pago_{pago.id}_{int(datetime.now().timestamp())}",
                    resource_type="image",
                    tags=["comprobante", "pago", f"user_{current_user_id}"]
                )
                
                pago.comprobante_url = upload_result.get('secure_url')
                comprobante_subido = True
                logger.info(f"Comprobante subido para pago {pago.id}")
                
            except Exception as e:
                logger.warning(f"Error subiendo comprobante para pago {pago.id}: {e}")
                # Continuar sin comprobante
        
        # Actualizar estado del pago
        pago.marcar_como_verificando()
        pago.fecha_pago_usuario = datetime.utcnow()
        
        if request.referencia_yape:
            pago.referencia_yape = request.referencia_yape
        
        # Crear notificaciones para administradores
        await _notificar_admins_nuevo_pago(pago.id, current_user_id, db)
        
        # 🔔 ENVIAR NOTIFICACIÓN FCM A ADMINS SOBRE NUEVA SUSCRIPCIÓN
        try:
            logger.info("🔔 === INICIANDO PROCESO DE NOTIFICACIÓN FCM ====")
            from app.models.user import User
            usuario = db.query(User).filter(User.id == current_user_id).first()
            user_email = usuario.email if usuario else f"Usuario {current_user_id}"
            logger.info(f"📧 Usuario encontrado: {user_email}")
            
            plan = db.query(PlanCatalogo).filter(
                PlanCatalogo.codigo == pago.plan_codigo
            ).first()
            plan_nombre = plan.nombre if plan else pago.plan_codigo.title()
            logger.info(f"📋 Plan encontrado: {plan_nombre}")
            
            logger.info("🚀 Llamando a FCMNotificationService...")
            await FCMNotificationService.notificar_nueva_suscripcion_a_admins(
                db=db,
                usuario_email=user_email,
                plan_nombre=plan_nombre
            )
            logger.info(f"✅ Notificación FCM enviada a admins sobre nueva suscripción de {user_email}")
        except Exception as e:
            logger.error(f"⚠️ Error enviando notificación FCM a admins: {e}")
            logger.error(f"🔍 Stack trace completo: {e.__class__.__name__}: {str(e)}")
            import traceback
            logger.error(f"📊 Traceback: {traceback.format_exc()}")
            # No fallar la confirmación por esto
        
        db.commit()
        
        logger.info(f"Pago {pago.id} confirmado por usuario {current_user_id}")
        
        return ConfirmarPagoResponse(
            pago_id=pago.id,
            estado=pago.estado,
            mensaje="Pago confirmado. Está siendo verificado por nuestros administradores.",
            comprobante_subido=comprobante_subido
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error confirmando pago {request.pago_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al confirmar pago"
        )

@router.post("/{pago_id}/subir-comprobante")
async def subir_comprobante_pago(
    pago_id: int,
    comprobante: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📸 Subir comprobante de pago (imagen)"""
    try:
        # Validar archivo
        if not comprobante.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser una imagen"
            )
        
        if comprobante.size > 5 * 1024 * 1024:  # 5MB máximo
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo es muy grande (máx. 5MB)"
            )
        
        # Buscar el pago
        pago = db.query(PagoPendiente).filter(
            and_(
                PagoPendiente.id == pago_id,
                PagoPendiente.user_id == current_user_id
            )
        ).first()
        
        if not pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado"
            )
        
        # Leer y subir archivo
        content = await comprobante.read()
        
        upload_result = cloudinary.uploader.upload(
            content,
            folder=f"galloapp/pagos/comprobantes/user_{current_user_id}",
            public_id=f"comprobante_pago_{pago_id}_{int(datetime.now().timestamp())}",
            resource_type="image",
            tags=["comprobante", "pago", f"user_{current_user_id}"]
        )
        
        # Actualizar pago
        pago.comprobante_url = upload_result.get('secure_url')
        db.commit()
        
        logger.info(f"Comprobante subido para pago {pago_id}")
        
        return {
            "mensaje": "Comprobante subido exitosamente",
            "comprobante_url": pago.comprobante_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo comprobante para pago {pago_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al subir comprobante"
        )

# ========================================
# ENDPOINTS DE CONSULTA
# ========================================

@router.get("/mis-pagos", response_model=List[PagoResponse])
async def obtener_mis_pagos(
    estado: Optional[str] = None,
    limit: int = 20,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Obtener historial de pagos del usuario"""
    try:
        query = db.query(PagoPendiente).filter(
            PagoPendiente.user_id == current_user_id
        )
        
        if estado:
            query = query.filter(PagoPendiente.estado == estado)
        
        pagos = query.order_by(desc(PagoPendiente.created_at)).limit(limit).all()
        return pagos
        
    except Exception as e:
        logger.error(f"Error obteniendo pagos para usuario {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener pagos"
        )

@router.get("/{pago_id}", response_model=PagoResponse)
async def obtener_detalle_pago(
    pago_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🔍 Obtener detalles de un pago específico"""
    try:
        pago = db.query(PagoPendiente).filter(
            and_(
                PagoPendiente.id == pago_id,
                PagoPendiente.user_id == current_user_id
            )
        ).first()
        
        if not pago:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado"
            )
        
        return pago
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo pago {pago_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener pago"
        )

# ========================================
# ENDPOINTS ADMINISTRATIVOS
# ========================================

@router.get("/admin/estadisticas", response_model=EstadisticasPagos)
async def obtener_estadisticas_pagos(
    admin_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📊 Estadísticas de pagos (solo admins)"""
    try:
        # Verificar admin
        from app.models.user import User
        admin = db.query(User).filter(User.id == admin_user_id).first()
        if not admin or not admin.es_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden ver estadísticas"
            )
        
        # Contar por estado
        total_pagos = db.query(func.count(PagoPendiente.id)).scalar() or 0
        pagos_pendientes = db.query(func.count(PagoPendiente.id)).filter(
            PagoPendiente.estado == EstadoPago.PENDIENTE
        ).scalar() or 0
        pagos_verificando = db.query(func.count(PagoPendiente.id)).filter(
            PagoPendiente.estado == EstadoPago.VERIFICANDO
        ).scalar() or 0
        pagos_aprobados = db.query(func.count(PagoPendiente.id)).filter(
            PagoPendiente.estado == EstadoPago.APROBADO
        ).scalar() or 0
        pagos_rechazados = db.query(func.count(PagoPendiente.id)).filter(
            PagoPendiente.estado == EstadoPago.RECHAZADO
        ).scalar() or 0
        
        # Montos
        monto_pendiente = db.query(func.sum(PagoPendiente.monto)).filter(
            PagoPendiente.estado.in_([EstadoPago.PENDIENTE, EstadoPago.VERIFICANDO])
        ).scalar() or 0
        
        monto_aprobado = db.query(func.sum(PagoPendiente.monto)).filter(
            PagoPendiente.estado == EstadoPago.APROBADO
        ).scalar() or 0
        
        # Ingresos del mes
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ingresos_mes = db.query(func.sum(PagoPendiente.monto)).filter(
            and_(
                PagoPendiente.estado == EstadoPago.APROBADO,
                PagoPendiente.fecha_verificacion >= inicio_mes
            )
        ).scalar() or 0
        
        # Distribución por plan
        distribucion = db.query(
            PagoPendiente.plan_codigo,
            func.count(PagoPendiente.id)
        ).group_by(PagoPendiente.plan_codigo).all()
        
        distribucion_por_plan = {plan: count for plan, count in distribucion}
        
        return EstadisticasPagos(
            total_pagos=total_pagos,
            pagos_pendientes=pagos_pendientes + pagos_verificando,
            pagos_aprobados=pagos_aprobados,
            pagos_rechazados=pagos_rechazados,
            monto_total_pendiente=monto_pendiente,
            monto_total_aprobado=monto_aprobado,
            ingresos_mes_actual=ingresos_mes,
            tiempo_promedio_verificacion_horas=24.0,  # TODO: calcular real
            pagos_vencidos=0,  # TODO: calcular
            distribucion_por_plan=distribucion_por_plan,
            distribucion_metodos={"yape": total_pagos}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de pagos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener estadísticas"
        )

# ========================================
# FUNCIONES AUXILIARES
# ========================================

async def _notificar_admins_nuevo_pago(pago_id: int, user_id: int, db: Session):
    """Crea notificaciones para todos los administradores"""
    try:
        from app.models.user import User
        
        # Obtener email del usuario
        usuario = db.query(User).filter(User.id == user_id).first()
        user_email = usuario.email if usuario else f"Usuario {user_id}"
        
        # Obtener admins que reciben notificaciones
        admins = db.query(User).filter(
            and_(
                User.es_admin == True,
                User.recibe_notificaciones_admin == True
            )
        ).all()
        
        # Crear notificación para cada admin
        for admin in admins:
            notificacion = NotificacionAdmin.crear_notificacion_pago(
                admin_id=admin.id,
                pago_id=pago_id,
                user_email=user_email
            )
            db.add(notificacion)
        
        logger.info(f"Notificaciones creadas para {len(admins)} admins sobre pago {pago_id}")
        
    except Exception as e:
        logger.error(f"Error creando notificaciones para pago {pago_id}: {e}")
        # No fallar el proceso principal por errores de notificación

async def _enviar_push_admins_nuevo_pago(pago, db: Session):
    """🔔 FIREBASE: Envía notificaciones push a admins sobre nuevo pago"""
    try:
        from app.models.user import User
        from app.models.plan_catalogo import PlanCatalogo
        from app.models.fcm_token import FCMToken
        
        logger.info(f"🔔 Iniciando notificación Firebase para pago {pago.id}")
        
        # Obtener datos del usuario
        usuario = db.query(User).filter(User.id == pago.user_id).first()
        user_email = usuario.email if usuario else f"Usuario {pago.user_id}"
        user_name = getattr(usuario, 'nombre_completo', user_email)
        
        # Obtener datos del plan  
        plan = db.query(PlanCatalogo).filter(
            PlanCatalogo.codigo == pago.plan_codigo
        ).first()
        plan_nombre = plan.nombre if plan else pago.plan_codigo.title()
        
        # Obtener tokens FCM de todos los administradores
        admin_tokens_query = db.query(FCMToken).join(User).filter(
            User.es_admin == True,
            FCMToken.is_active == True
        ).all()
        
        admin_tokens = [token.fcm_token for token in admin_tokens_query]
        logger.info(f"🔔 Encontrados {len(admin_tokens)} tokens de admin")
        
        if not admin_tokens:
            logger.warning("⚠️ No se encontraron tokens FCM de administradores")
            return
        
        # Importar Firebase service de forma lazy
        try:
            from app.api.v1.notifications import get_firebase_service
            firebase = get_firebase_service()
            
            # Enviar notificación usando endpoint interno
            result = await firebase.notify_admin_new_subscription(
                admin_tokens=admin_tokens,
                user_name=user_name,
                user_email=user_email,
                plan_name=plan_nombre,
                amount=float(pago.monto)
            )
            
            logger.info(f"🔔 FIREBASE: Notificación enviada a {result.get('success_count', 0)} admins para pago {pago.id}")
            
        except Exception as firebase_error:
            logger.error(f"❌ Error Firebase para pago {pago.id}: {firebase_error}")
        
    except Exception as e:
        logger.error(f"❌ Error enviando push notifications para pago {pago.id}: {e}")
        # No fallar el proceso principal