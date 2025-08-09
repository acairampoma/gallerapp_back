# 🛡️ Middleware de Validación de Límites - Sistema Suscripciones
from functools import wraps
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional, Callable, Any
import logging

from app.database import get_db
from app.core.security import get_current_user_id
from app.services.limite_service import validar_limite_recurso
from app.schemas.suscripcion import RecursoTipo

logger = logging.getLogger(__name__)

class LimiteMiddleware:
    """Middleware para validar límites antes de crear recursos"""
    
    @staticmethod
    def validar_limite(recurso_tipo: RecursoTipo, gallo_id_param: Optional[str] = None):
        """
        Decorator para validar límites antes de ejecutar endpoint
        
        Args:
            recurso_tipo: Tipo de recurso a validar (GALLOS, TOPES, PELEAS, VACUNAS)
            gallo_id_param: Nombre del parámetro que contiene el gallo_id (opcional)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    # Obtener dependencias
                    current_user_id = None
                    db = None
                    gallo_id = None
                    
                    # Extraer user_id y db de los kwargs (inyectados por FastAPI)
                    for key, value in kwargs.items():
                        if key == 'current_user_id' and isinstance(value, int):
                            current_user_id = value
                        elif key == 'db' and hasattr(value, 'query'):
                            db = value
                        elif gallo_id_param and key == gallo_id_param:
                            gallo_id = value
                    
                    # Validar que tenemos las dependencias necesarias
                    if not current_user_id:
                        logger.error("current_user_id no encontrado en middleware de límites")
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Usuario no autenticado"
                        )
                    
                    if not db:
                        logger.error("db session no encontrada en middleware de límites")
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error interno: sesión de base de datos no disponible"
                        )
                    
                    # Si es un recurso por gallo, necesitamos gallo_id
                    if recurso_tipo in [RecursoTipo.TOPES, RecursoTipo.PELEAS, RecursoTipo.VACUNAS]:
                        if not gallo_id:
                            # Intentar obtener gallo_id del request body
                            if args and hasattr(args[0], 'gallo_id'):
                                gallo_id = args[0].gallo_id
                            else:
                                raise HTTPException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="gallo_id es requerido para este recurso"
                                )
                    
                    # Validar límite
                    validacion = validar_limite_recurso(
                        db=db,
                        user_id=current_user_id,
                        recurso_tipo=recurso_tipo,
                        gallo_id=gallo_id
                    )
                    
                    # Si no puede crear, devolver error con información para upgrade
                    if not validacion.puede_crear:
                        error_response = {
                            "detail": validacion.mensaje_error,
                            "limite_info": {
                                "recurso_tipo": validacion.recurso_tipo.value,
                                "limite_actual": validacion.limite_actual,
                                "cantidad_usada": validacion.cantidad_usada,
                                "plan_recomendado": validacion.plan_recomendado,
                                "upgrade_disponible": validacion.upgrade_disponible
                            },
                            "accion_requerida": "upgrade_plan"
                        }
                        
                        raise HTTPException(
                            status_code=status.HTTP_402_PAYMENT_REQUIRED,  # 402 = Payment Required
                            detail=error_response
                        )
                    
                    # Si puede crear, continuar con la función original
                    logger.info(f"Validación de límite pasada para user {current_user_id}, recurso {recurso_tipo.value}")
                    return await func(*args, **kwargs) if func.__code__.co_flags & 0x0080 else func(*args, **kwargs)
                    
                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"Error en middleware de límites: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error interno validando límites"
                    )
            
            return wrapper
        return decorator

# ========================================
# DECORADORES ESPECÍFICOS POR RECURSO
# ========================================

def validar_limite_gallos(func: Callable) -> Callable:
    """Decorator específico para validar límite de gallos"""
    return LimiteMiddleware.validar_limite(RecursoTipo.GALLOS)(func)

def validar_limite_topes(gallo_id_param: str = "gallo_id"):
    """Decorator específico para validar límite de topes"""
    def decorator(func: Callable) -> Callable:
        return LimiteMiddleware.validar_limite(RecursoTipo.TOPES, gallo_id_param)(func)
    return decorator

def validar_limite_peleas(gallo_id_param: str = "gallo_id"):
    """Decorator específico para validar límite de peleas"""
    def decorator(func: Callable) -> Callable:
        return LimiteMiddleware.validar_limite(RecursoTipo.PELEAS, gallo_id_param)(func)
    return decorator

def validar_limite_vacunas(gallo_id_param: str = "gallo_id"):
    """Decorator específico para validar límite de vacunas"""
    def decorator(func: Callable) -> Callable:
        return LimiteMiddleware.validar_limite(RecursoTipo.VACUNAS, gallo_id_param)(func)
    return decorator

# ========================================
# FUNCIONES DE UTILIDAD
# ========================================

async def verificar_limite_antes_crear(
    user_id: int,
    recurso_tipo: RecursoTipo,
    gallo_id: Optional[int],
    db: Session
) -> None:
    """
    Función helper para verificar límites manualmente en endpoints
    
    Raises:
        HTTPException: Si el límite es superado
    """
    validacion = validar_limite_recurso(
        db=db,
        user_id=user_id,
        recurso_tipo=recurso_tipo,
        gallo_id=gallo_id
    )
    
    if not validacion.puede_crear:
        error_response = {
            "detail": validacion.mensaje_error,
            "limite_info": {
                "recurso_tipo": validacion.recurso_tipo.value,
                "limite_actual": validacion.limite_actual,
                "cantidad_usada": validacion.cantidad_usada,
                "plan_recomendado": validacion.plan_recomendado,
                "upgrade_disponible": validacion.upgrade_disponible
            },
            "accion_requerida": "upgrade_plan"
        }
        
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=error_response
        )

def crear_respuesta_limite_superado(validacion: Any) -> dict:
    """Crea respuesta estandarizada cuando se supera un límite"""
    return {
        "success": False,
        "mensaje": "Límite de suscripción alcanzado",
        "limite_info": {
            "recurso_tipo": validacion.recurso_tipo.value,
            "limite_actual": validacion.limite_actual,
            "cantidad_usada": validacion.cantidad_usada,
            "mensaje_error": validacion.mensaje_error,
            "plan_recomendado": validacion.plan_recomendado,
            "upgrade_disponible": validacion.upgrade_disponible
        },
        "acciones_disponibles": {
            "ver_planes": "/api/v1/suscripciones/planes",
            "solicitar_upgrade": "/api/v1/suscripciones/upgrade",
            "generar_qr_pago": "/api/v1/pagos/generar-qr"
        }
    }