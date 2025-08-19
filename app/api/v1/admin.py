# 👑 API Endpoints para Panel Administrativo - Sistema Completo
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
import logging

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.user import User
from app.models.pago_pendiente import PagoPendiente, EstadoPago
from app.models.notificacion_admin import NotificacionAdmin, TipoNotificacion, PrioridadNotificacion
from app.models.plan_catalogo import PlanCatalogo
from app.models.suscripcion import Suscripcion
from app.schemas.pago import (
    PagoPendienteAdmin, 
    AccionAdminRequest, 
    AccionAdminResponse,
    DashboardAdmin
)
from app.services.fcm_suscripciones_service import FCMNotificationService

# Configurar logger
logger = logging.getLogger("galloapp.admin")
router = APIRouter(prefix="/admin", tags=["👑 Administración"])

# ========================================
# MIDDLEWARE DE VERIFICACIÓN ADMIN
# ========================================

async def verificar_admin(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> User:
    """Middleware para verificar que el usuario es administrador"""
    admin = db.query(User).filter(User.id == current_user_id).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if not admin.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    
    return admin

# ========================================
# DASHBOARD PRINCIPAL
# ========================================

@router.get("/dashboard", response_model=DashboardAdmin)
async def obtener_dashboard_admin(
    admin: User = Depends(verificar_admin),
    db: Session = Depends(get_db)
):
    """
    📊 Dashboard principal para administradores
    
    Muestra resumen de pagos pendientes, notificaciones,
    usuarios nuevos e ingresos del día.
    """
    try:
        # Pagos que requieren atención
        pagos_requieren_atencion = db.query(func.count(PagoPendiente.id)).filter(
            PagoPendiente.estado.in_([EstadoPago.PENDIENTE, EstadoPago.VERIFICANDO])
        ).scalar() or 0
        
        # Notificaciones no leídas del admin
        notificaciones_no_leidas = db.query(func.count(NotificacionAdmin.id)).filter(
            and_(
                NotificacionAdmin.admin_id == admin.id,
                NotificacionAdmin.leido == False
            )
        ).scalar() or 0
        
        # Usuarios nuevos hoy
        hoy = date.today()
        usuarios_nuevos_hoy = db.query(func.count(User.id)).filter(
            func.date(User.created_at) == hoy
        ).scalar() or 0
        
        # Ingresos de hoy
        ingresos_hoy = db.query(func.sum(PagoPendiente.monto)).filter(
            and_(
                PagoPendiente.estado == EstadoPago.APROBADO,
                func.date(PagoPendiente.fecha_verificacion) == hoy
            )
        ).scalar() or 0
        
        # Alertas urgentes
        alertas_urgentes = []
        
        # Pagos vencidos (más de 48 horas)
        hace_48h = datetime.utcnow() - timedelta(hours=48)
        pagos_vencidos = db.query(func.count(PagoPendiente.id)).filter(
            and_(
                PagoPendiente.estado == EstadoPago.VERIFICANDO,
                PagoPendiente.created_at < hace_48h
            )
        ).scalar() or 0
        
        if pagos_vencidos > 0:
            alertas_urgentes.append(f"⚠️ {pagos_vencidos} pagos llevan más de 48 horas sin verificar")
        
        if pagos_requieren_atencion > 10:
            alertas_urgentes.append(f"🚨 {pagos_requieren_atencion} pagos pendientes de verificación")
        
        # Datos para gráficos - últimos 7 días
        pagos_ultimos_7_dias = []
        for i in range(7):
            fecha = date.today() - timedelta(days=i)
            pagos_dia = db.query(func.count(PagoPendiente.id)).filter(
                func.date(PagoPendiente.created_at) == fecha
            ).scalar() or 0
            
            pagos_ultimos_7_dias.append({
                "fecha": fecha.isoformat(),
                "cantidad": pagos_dia
            })
        
        return DashboardAdmin(
            pagos_requieren_atencion=pagos_requieren_atencion,
            notificaciones_no_leidas=notificaciones_no_leidas,
            usuarios_nuevos_hoy=usuarios_nuevos_hoy,
            ingresos_hoy=ingresos_hoy,
            alertas_urgentes=alertas_urgentes,
            pagos_ultimos_7_dias=pagos_ultimos_7_dias,
            conversion_por_dia=[]  # TODO: implementar si se necesita
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo dashboard para admin {admin.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener dashboard"
        )

# ========================================
# GESTIÓN DE PAGOS
# ========================================

@router.get("/pagos/pendientes", response_model=List[PagoPendienteAdmin])
async def obtener_pagos_pendientes(
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    limit: int = Query(50, le=100, description="Límite de resultados"),
    skip: int = Query(0, ge=0, description="Saltar resultados"),
    admin: User = Depends(verificar_admin),
    db: Session = Depends(get_db)
):
    """
    💰 Obtener lista de pagos pendientes de verificación
    
    Lista todos los pagos que requieren atención de administradores,
    con información completa del usuario y plan.
    """
    try:
        query = db.query(PagoPendiente).options(
            joinedload(PagoPendiente.usuario)
        )
        
        # Filtros
        if estado:
            query = query.filter(PagoPendiente.estado == estado)
        else:
            # Por defecto, mostrar solo pendientes y en verificación
            query = query.filter(
                PagoPendiente.estado.in_([EstadoPago.PENDIENTE, EstadoPago.VERIFICANDO])
            )
        
        # Ordenar por prioridad: verificando primero, luego por fecha
        pagos = query.order_by(
            PagoPendiente.estado.desc(),  # verificando antes que pendiente
            PagoPendiente.created_at.asc()  # más antiguos primero
        ).offset(skip).limit(limit).all()
        
        # Convertir a schema con información adicional
        pagos_admin = []
        for pago in pagos:
            # Calcular tiempo transcurrido
            tiempo_transcurrido = datetime.utcnow() - pago.created_at
            tiempo_horas = tiempo_transcurrido.total_seconds() / 3600
            
            # Determinar si es sospechoso
            es_sospechoso = False
            razon_sospecha = None
            
            if pago.intentos > 3:
                es_sospechoso = True
                razon_sospecha = "Múltiples intentos de pago"
            elif tiempo_horas > 72:
                es_sospechoso = True
                razon_sospecha = "Pago muy antiguo"
            
            # Obtener plan
            plan = db.query(PlanCatalogo).filter(
                PlanCatalogo.codigo == pago.plan_codigo
            ).first()
            
            pago_admin = PagoPendienteAdmin(
                **pago.to_dict(),
                usuario_email=pago.usuario.email if pago.usuario else f"Usuario {pago.user_id}",
                plan_nombre_completo=plan.nombre if plan else pago.plan_codigo.title(),
                tiempo_transcurrido_horas=round(tiempo_horas, 1),
                es_sospechoso=es_sospechoso,
                razon_sospecha=razon_sospecha
            )
            pagos_admin.append(pago_admin)
        
        return pagos_admin
        
    except Exception as e:
        logger.error(f"Error obteniendo pagos pendientes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener pagos pendientes"
        )

@router.post("/pagos/{pago_id}/aprobar", response_model=AccionAdminResponse)
async def aprobar_pago(
    pago_id: int,
    request: AccionAdminRequest,
    admin: User = Depends(verificar_admin),
    db: Session = Depends(get_db)
):
    """
    ✅ Aprobar un pago y activar plan del usuario
    
    Aprueba el pago, actualiza la suscripción del usuario
    y envía notificación de activación.
    """
    try:
        # Buscar el pago
        pago = db.query(PagoPendiente).options(
            joinedload(PagoPendiente.usuario)
        ).filter(PagoPendiente.id == pago_id).first()
        
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
        
        estado_anterior = pago.estado
        
        # Aprobar el pago
        pago.aprobar_pago(admin.id, request.notas)
        
        # Activar plan del usuario
        await _activar_plan_usuario(pago.user_id, pago.plan_codigo, db)
        
        # 🔔 ENVIAR NOTIFICACIÓN FCM AL USUARIO
        try:
            plan = db.query(PlanCatalogo).filter(
                PlanCatalogo.codigo == pago.plan_codigo
            ).first()
            plan_nombre = plan.nombre if plan else pago.plan_codigo.title()
            
            await FCMNotificationService.notificar_suscripcion_aprobada_a_usuario(
                db=db, 
                user_id=pago.user_id, 
                plan_nombre=plan_nombre
            )
            logger.info(f"✅ Notificación FCM enviada a usuario {pago.user_id}")
        except Exception as e:
            logger.error(f"⚠️ Error enviando notificación FCM: {e}")
            # No fallar la aprobación por esto
        
        db.commit()
        
        logger.info(f"Admin {admin.id} aprobó pago {pago_id} para usuario {pago.user_id}")
        
        return AccionAdminResponse(
            pago_id=pago.id,
            accion_realizada=request.accion,
            estado_anterior=estado_anterior,
            estado_nuevo=EstadoPago.APROBADO,
            admin_id=admin.id,
            notas=request.notas,
            fecha_accion=datetime.utcnow(),
            notificacion_enviada=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error aprobando pago {pago_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al aprobar pago"
        )

@router.post("/pagos/{pago_id}/rechazar", response_model=AccionAdminResponse)
async def rechazar_pago(
    pago_id: int,
    request: AccionAdminRequest,
    admin: User = Depends(verificar_admin),
    db: Session = Depends(get_db)
):
    """❌ Rechazar un pago con motivo"""
    try:
        # Validar que se proporcionen notas para rechazo
        if not request.notas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las notas son obligatorias al rechazar un pago"
            )
        
        pago = db.query(PagoPendiente).filter(
            PagoPendiente.id == pago_id
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
        
        estado_anterior = pago.estado
        
        # Rechazar el pago
        pago.rechazar_pago(admin.id, request.notas)
        
        # 🔔 ENVIAR NOTIFICACIÓN FCM AL USUARIO
        try:
            plan = db.query(PlanCatalogo).filter(
                PlanCatalogo.codigo == pago.plan_codigo
            ).first()
            plan_nombre = plan.nombre if plan else pago.plan_codigo.title()
            
            await FCMNotificationService.notificar_suscripcion_rechazada_a_usuario(
                db=db, 
                user_id=pago.user_id, 
                plan_nombre=plan_nombre,
                motivo=request.notas
            )
            logger.info(f"✅ Notificación FCM de rechazo enviada a usuario {pago.user_id}")
        except Exception as e:
            logger.error(f"⚠️ Error enviando notificación FCM de rechazo: {e}")
            # No fallar el rechazo por esto
        
        db.commit()
        
        logger.info(f"Admin {admin.id} rechazó pago {pago_id}: {request.notas}")
        
        return AccionAdminResponse(
            pago_id=pago.id,
            accion_realizada=request.accion,
            estado_anterior=estado_anterior,
            estado_nuevo=EstadoPago.RECHAZADO,
            admin_id=admin.id,
            notas=request.notas,
            fecha_accion=datetime.utcnow(),
            notificacion_enviada=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error rechazando pago {pago_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al rechazar pago"
        )

# ========================================
# GESTIÓN DE NOTIFICACIONES
# ========================================

@router.get("/notificaciones", response_model=List[Dict[str, Any]])
async def obtener_notificaciones_admin(
    leidas: Optional[bool] = Query(None, description="Filtrar por estado de lectura"),
    limit: int = Query(20, le=100),
    admin: User = Depends(verificar_admin),
    db: Session = Depends(get_db)
):
    """🔔 Obtener notificaciones del administrador"""
    try:
        query = db.query(NotificacionAdmin).filter(
            NotificacionAdmin.admin_id == admin.id
        )
        
        if leidas is not None:
            query = query.filter(NotificacionAdmin.leido == leidas)
        
        notificaciones = query.order_by(
            desc(NotificacionAdmin.prioridad),
            desc(NotificacionAdmin.created_at)
        ).limit(limit).all()
        
        return [notif.to_dict() for notif in notificaciones]
        
    except Exception as e:
        logger.error(f"Error obteniendo notificaciones para admin {admin.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener notificaciones"
        )

@router.put("/notificaciones/{notif_id}/marcar-leida")
async def marcar_notificacion_leida(
    notif_id: int,
    admin: User = Depends(verificar_admin),
    db: Session = Depends(get_db)
):
    """✅ Marcar notificación como leída"""
    try:
        notificacion = db.query(NotificacionAdmin).filter(
            and_(
                NotificacionAdmin.id == notif_id,
                NotificacionAdmin.admin_id == admin.id
            )
        ).first()
        
        if not notificacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificación no encontrada"
            )
        
        notificacion.marcar_como_leido()
        db.commit()
        
        return {"mensaje": "Notificación marcada como leída"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error marcando notificación {notif_id} como leída: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al marcar notificación"
        )

# ========================================
# GESTIÓN DE USUARIOS
# ========================================

@router.get("/usuarios")
async def obtener_usuarios_admin(
    buscar: Optional[str] = Query(None, description="Buscar por email"),
    solo_premium: bool = Query(False, description="Solo usuarios premium"),
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0),
    admin: User = Depends(verificar_admin),
    db: Session = Depends(get_db)
):
    """👥 Obtener lista de usuarios para administración"""
    try:
        query = db.query(User).filter(User.id != admin.id)  # Excluir al admin actual
        
        if buscar:
            query = query.filter(User.email.ilike(f"%{buscar}%"))
        
        if solo_premium:
            query = query.filter(User.is_premium == True)
        
        usuarios = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
        
        resultado = []
        for usuario in usuarios:
            # Obtener suscripción actual
            suscripcion = db.query(Suscripcion).filter(
                and_(
                    Suscripcion.user_id == usuario.id,
                    Suscripcion.status == 'active'
                )
            ).first()
            
            usuario_info = {
                "id": usuario.id,
                "email": usuario.email,
                "is_active": usuario.is_active,
                "is_premium": usuario.is_premium,
                "created_at": usuario.created_at.isoformat() if usuario.created_at else None,
                "last_login": usuario.last_login.isoformat() if usuario.last_login else None,
                "suscripcion": {
                    "plan": suscripcion.plan_name if suscripcion else "Sin plan",
                    "fecha_fin": suscripcion.fecha_fin.isoformat() if suscripcion and suscripcion.fecha_fin else None
                } if suscripcion else None
            }
            resultado.append(usuario_info)
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener usuarios"
        )

# ========================================
# FUNCIONES AUXILIARES
# ========================================

async def _activar_plan_usuario(user_id: int, plan_codigo: str, db: Session):
    """Activa el plan premium para un usuario tras aprobar el pago"""
    try:
        # Obtener el plan
        plan = db.query(PlanCatalogo).filter(
            PlanCatalogo.codigo == plan_codigo
        ).first()
        
        if not plan:
            raise ValueError(f"Plan {plan_codigo} no encontrado")
        
        # Obtener suscripción actual del usuario
        suscripcion = db.query(Suscripcion).filter(
            and_(
                Suscripcion.user_id == user_id,
                Suscripcion.status == 'active'
            )
        ).first()
        
        if not suscripcion:
            raise ValueError(f"Usuario {user_id} no tiene suscripción activa")
        
        # Actualizar suscripción
        fecha_inicio = date.today()
        fecha_fin = fecha_inicio + timedelta(days=plan.duracion_dias)
        
        suscripcion.plan_type = plan.codigo
        suscripcion.plan_name = plan.nombre
        suscripcion.precio = plan.precio
        suscripcion.fecha_inicio = fecha_inicio
        suscripcion.fecha_fin = fecha_fin
        suscripcion.gallos_maximo = plan.gallos_maximo
        suscripcion.topes_por_gallo = plan.topes_por_gallo
        suscripcion.peleas_por_gallo = plan.peleas_por_gallo
        suscripcion.vacunas_por_gallo = plan.vacunas_por_gallo
        suscripcion.updated_at = datetime.utcnow()
        
        # Actualizar usuario a premium
        if plan.es_premium:
            usuario = db.query(User).filter(User.id == user_id).first()
            if usuario:
                usuario.is_premium = True
        
        logger.info(f"Plan {plan_codigo} activado para usuario {user_id}")
        
    except Exception as e:
        logger.error(f"Error activando plan para usuario {user_id}: {e}")
        raise