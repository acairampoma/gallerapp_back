# 📋 API Endpoints para Suscripciones - Sistema Completo
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.plan_catalogo import PlanCatalogo
from app.models.suscripcion import Suscripcion
from app.models.user import User
from app.schemas.suscripcion import (
    SuscripcionResponse, 
    SuscripcionUpdate,
    PlanCatalogoResponse,
    EstadoLimites,
    ValidacionLimite,
    ValidacionLimiteRequest,
    UpgradeRequest,
    EstadisticasSuscripcion
)
from app.services.limite_service import LimiteService, validar_limite_recurso, obtener_limites_usuario

# Configurar logger
logger = logging.getLogger("galloapp.suscripciones")
router = APIRouter(prefix="/suscripciones", tags=["📋 Suscripciones"])

# ========================================
# ENDPOINTS DE SUSCRIPCIÓN ACTUAL
# ========================================

@router.get("/actual", response_model=Dict[str, Any])
async def obtener_suscripcion_actual(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    📋 Obtener suscripción actual del usuario
    
    Retorna la suscripción activa con todos los detalles,
    límites, estado de vencimiento y pagos pendientes.
    """
    try:
        suscripcion = db.query(Suscripcion).filter(
            and_(
                Suscripcion.user_id == current_user_id,
                Suscripcion.status == 'active'
            )
        ).first()
        
        if not suscripcion:
            # Si no tiene suscripción, crear una gratuita automáticamente
            logger.info(f"Creando suscripción gratuita automática para usuario {current_user_id}")
            suscripcion = await _crear_suscripcion_gratuita(current_user_id, db)
        
        # Convertir a dict y calcular campos adicionales
        suscripcion_dict = suscripcion.__dict__.copy()
        
        # Remover campos internos de SQLAlchemy
        suscripcion_dict.pop('_sa_instance_state', None)
        
        # Calcular campos adicionales
        suscripcion_dict['dias_restantes'] = _calcular_dias_restantes(suscripcion.fecha_fin)
        suscripcion_dict['esta_activa'] = suscripcion.status == 'active' and (
            not suscripcion.fecha_fin or suscripcion.fecha_fin >= date.today()
        )
        suscripcion_dict['es_premium'] = suscripcion.precio > 0
        
        # 🔄 VERIFICAR PAGOS PENDIENTES
        from app.models.pago_pendiente import PagoPendiente
        pago_pendiente = db.query(PagoPendiente).filter(
            and_(
                PagoPendiente.user_id == current_user_id,
                PagoPendiente.estado.in_(['pendiente', 'verificando'])
            )
        ).order_by(desc(PagoPendiente.created_at)).first()
        
        if pago_pendiente:
            suscripcion_dict['pago_pendiente'] = {
                'id': pago_pendiente.id,
                'plan_codigo': pago_pendiente.plan_codigo,
                'monto': float(pago_pendiente.monto),
                'estado': pago_pendiente.estado,
                'fecha_pago': pago_pendiente.fecha_pago_usuario.isoformat() if pago_pendiente.fecha_pago_usuario else None,
                'created_at': pago_pendiente.created_at.isoformat()
            }
        else:
            suscripcion_dict['pago_pendiente'] = None
        
        return suscripcion_dict
        
    except Exception as e:
        logger.error(f"Error obteniendo suscripción actual para usuario {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener suscripción"
        )

@router.get("/limites", response_model=EstadoLimites)
async def obtener_limites_actuales(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    ⚡ Obtener límites y uso actual del usuario
    
    Retorna el estado completo de límites por recurso,
    incluyendo gallos, topes, peleas y vacunas.
    """
    try:
        estado_limites = obtener_limites_usuario(db, current_user_id)
        return estado_limites
        
    except Exception as e:
        logger.error(f"Error obteniendo límites para usuario {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener límites"
        )

@router.post("/validar-limite", response_model=ValidacionLimite)
async def validar_limite_recurso_endpoint(
    request: ValidacionLimiteRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🔍 Validar si el usuario puede crear un recurso
    
    Valida límites antes de crear gallos, topes, peleas o vacunas.
    Útil para mostrar mensajes de error o popups de upgrade.
    """
    try:
        validacion = validar_limite_recurso(
            db=db,
            user_id=current_user_id,
            recurso_tipo=request.recurso_tipo,
            gallo_id=request.gallo_id
        )
        
        return validacion
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error validando límite para usuario {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al validar límite"
        )

# ========================================
# ENDPOINTS DE PLANES
# ========================================

@router.get("/planes", response_model=List[PlanCatalogoResponse])
async def obtener_planes_disponibles(
    incluir_gratuito: bool = Query(False, description="Incluir plan gratuito en la lista"),
    db: Session = Depends(get_db)
):
    """
    📋 Obtener catálogo de planes disponibles
    
    Lista todos los planes de suscripción activos,
    ordenados por precio y con información completa.
    """
    try:
        query = db.query(PlanCatalogo).filter(PlanCatalogo.activo == True)
        
        if not incluir_gratuito:
            query = query.filter(PlanCatalogo.codigo != 'gratuito')
        
        planes = query.order_by(PlanCatalogo.orden.asc()).all()
        return planes
        
    except Exception as e:
        logger.error(f"Error obteniendo planes disponibles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener planes"
        )

@router.get("/planes/{plan_codigo}", response_model=PlanCatalogoResponse)
async def obtener_plan_detalle(
    plan_codigo: str,
    db: Session = Depends(get_db)
):
    """📋 Obtener detalles de un plan específico"""
    try:
        plan = db.query(PlanCatalogo).filter(
            and_(
                PlanCatalogo.codigo == plan_codigo,
                PlanCatalogo.activo == True
            )
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan '{plan_codigo}' no encontrado"
            )
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo plan {plan_codigo}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener plan"
        )

# ========================================
# ENDPOINTS DE UPGRADE
# ========================================

@router.post("/upgrade", response_model=Dict[str, Any])
async def solicitar_upgrade_plan(
    request: UpgradeRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🚀 Solicitar upgrade a plan premium
    
    Inicia el proceso de upgrade generando un pago pendiente.
    El usuario debe completar el pago para activar el plan.
    """
    try:
        # Verificar que el plan existe
        plan = db.query(PlanCatalogo).filter(
            and_(
                PlanCatalogo.codigo == request.plan_codigo,
                PlanCatalogo.activo == True
            )
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan '{request.plan_codigo}' no encontrado"
            )
        
        # Verificar suscripción actual
        suscripcion_actual = db.query(Suscripcion).filter(
            and_(
                Suscripcion.user_id == current_user_id,
                Suscripcion.status == 'active'
            )
        ).first()
        
        if not suscripcion_actual:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se encontró suscripción activa"
            )
        
        # Verificar que no sea un downgrade
        planes_orden = {'gratuito': 0, 'basico': 1, 'premium': 2, 'profesional': 3}
        orden_actual = planes_orden.get(suscripcion_actual.plan_type, 0)
        orden_nuevo = planes_orden.get(request.plan_codigo, 0)
        
        if orden_nuevo <= orden_actual:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede hacer downgrade. Contacta soporte para cambiar a un plan menor."
            )
        
        # Crear pago pendiente (se manejará en el endpoint de pagos)
        return {
            "mensaje": "Upgrade solicitado correctamente",
            "plan_destino": plan.nombre,
            "monto": float(plan.precio),
            "siguiente_paso": "generar_qr_pago",
            "plan_codigo": request.plan_codigo
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando upgrade para usuario {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar upgrade"
        )

# ========================================
# ENDPOINTS ADMINISTRATIVOS
# ========================================

@router.put("/admin/{user_id}/activar-plan")
async def activar_plan_usuario(
    user_id: int,
    plan_codigo: str,
    duracion_dias: Optional[int] = 30,
    admin_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    👑 Activar plan para un usuario (solo admins)
    
    Permite a los administradores activar planes manualmente
    tras verificar pagos.
    """
    try:
        # Verificar que el usuario actual es admin
        admin = db.query(User).filter(User.id == admin_user_id).first()
        if not admin or not admin.es_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden activar planes"
            )
        
        # Verificar que el plan existe
        plan = db.query(PlanCatalogo).filter(
            and_(
                PlanCatalogo.codigo == plan_codigo,
                PlanCatalogo.activo == True
            )
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan '{plan_codigo}' no encontrado"
            )
        
        # Actualizar suscripción del usuario
        suscripcion = db.query(Suscripcion).filter(
            and_(
                Suscripcion.user_id == user_id,
                Suscripcion.status == 'active'
            )
        ).first()
        
        if not suscripcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no tiene suscripción activa"
            )
        
        # Actualizar con los datos del nuevo plan
        fecha_inicio = date.today()
        fecha_fin = fecha_inicio + timedelta(days=duracion_dias)
        
        suscripcion.plan_type = plan.codigo
        suscripcion.plan_name = plan.nombre
        suscripcion.precio = plan.precio
        suscripcion.fecha_inicio = fecha_inicio
        suscripcion.fecha_fin = fecha_fin
        suscripcion.gallos_maximo = plan.gallos_maximo
        suscripcion.topes_por_gallo = plan.topes_por_gallo
        suscripcion.peleas_por_gallo = plan.peleas_por_gallo
        suscripcion.vacunas_por_gallo = plan.vacunas_por_gallo
        # marketplace_publicaciones_max se obtiene via JOIN con planes_catalogo
        suscripcion.updated_at = datetime.utcnow()
        
        # Actualizar estado premium del usuario si es necesario
        if plan.es_premium:
            usuario = db.query(User).filter(User.id == user_id).first()
            if usuario:
                usuario.is_premium = True
        
        db.commit()
        
        logger.info(f"Admin {admin_user_id} activó plan {plan_codigo} para usuario {user_id}")
        
        return {
            "mensaje": "Plan activado exitosamente",
            "usuario_id": user_id,
            "plan_activado": plan.nombre,
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "activado_por": admin_user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error activando plan para usuario {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al activar plan"
        )

@router.get("/admin/estadisticas", response_model=EstadisticasSuscripcion)
async def obtener_estadisticas_suscripciones(
    admin_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📊 Estadísticas de suscripciones (solo admins)"""
    try:
        # Verificar admin
        admin = db.query(User).filter(User.id == admin_user_id).first()
        if not admin or not admin.es_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden ver estadísticas"
            )
        
        # Calcular estadísticas
        total_usuarios = db.query(func.count(User.id)).scalar() or 0
        usuarios_premium = db.query(func.count(User.id)).filter(User.is_premium == True).scalar() or 0
        usuarios_gratuitos = total_usuarios - usuarios_premium
        
        # Ingresos del mes actual
        inicio_mes = date.today().replace(day=1)
        ingresos_mes = db.query(func.sum(Suscripcion.precio)).filter(
            and_(
                Suscripcion.created_at >= inicio_mes,
                Suscripcion.precio > 0
            )
        ).scalar() or 0
        
        # Distribución por planes
        distribucion = db.query(
            Suscripcion.plan_type,
            func.count(Suscripcion.id)
        ).filter(
            Suscripcion.status == 'active'
        ).group_by(
            Suscripcion.plan_type
        ).all()
        
        distribucion_planes = {plan: count for plan, count in distribucion}
        
        # Conversion rate
        conversion_rate = (usuarios_premium / total_usuarios * 100) if total_usuarios > 0 else 0
        
        return EstadisticasSuscripcion(
            total_usuarios=total_usuarios,
            usuarios_gratuitos=usuarios_gratuitos,
            usuarios_premium=usuarios_premium,
            ingresos_mes_actual=ingresos_mes,
            ingresos_mes_anterior=0,  # TODO: calcular mes anterior
            conversion_rate=round(conversion_rate, 2),
            distribucion_planes=distribucion_planes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener estadísticas"
        )

# ========================================
# FUNCIONES AUXILIARES
# ========================================

async def _crear_suscripcion_gratuita(user_id: int, db: Session):
    """Crea una suscripción gratuita automáticamente"""
    try:
        # Obtener plan gratuito
        plan_gratuito = db.query(PlanCatalogo).filter(
            PlanCatalogo.codigo == 'gratuito'
        ).first()
        
        if not plan_gratuito:
            raise ValueError("Plan gratuito no configurado")
        
        # Crear suscripción
        nueva_suscripcion = Suscripcion(
            user_id=user_id,
            plan_type=plan_gratuito.codigo,
            plan_name=plan_gratuito.nombre,
            precio=plan_gratuito.precio,
            status='active',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=365),  # 1 año de plan gratuito
            gallos_maximo=plan_gratuito.gallos_maximo,
            topes_por_gallo=plan_gratuito.topes_por_gallo,
            peleas_por_gallo=plan_gratuito.peleas_por_gallo,
            vacunas_por_gallo=plan_gratuito.vacunas_por_gallo,
        )
        
        db.add(nueva_suscripcion)
        db.commit()
        db.refresh(nueva_suscripcion)
        
        logger.info(f"Suscripción gratuita creada para usuario {user_id}")
        return nueva_suscripcion
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creando suscripción gratuita para usuario {user_id}: {e}")
        raise

def _calcular_dias_restantes(fecha_fin: Optional[date]) -> Optional[int]:
    """Calcula días restantes hasta el vencimiento"""
    if not fecha_fin:
        return None
    
    delta = fecha_fin - date.today()
    return max(0, delta.days)