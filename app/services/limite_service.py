# ⚡ Servicio de Validación de Límites - Sistema Suscripciones
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Optional, Tuple, List
from datetime import datetime, date
import logging

from app.models.user import User
from app.models.gallo_simple import Gallo
from app.models.tope import Tope  
from app.models.pelea import Pelea
from app.models.vacuna import Vacuna
from app.models.suscripcion import Suscripcion  # Movido aquí desde línea 31
from app.schemas.suscripcion import EstadoLimites, LimiteRecurso, ValidacionLimite, RecursoTipo
from app.database import get_db

logger = logging.getLogger(__name__)

def crear_limite_recurso_completo(recurso_tipo, limite, usado):
    """Crea LimiteRecurso con todos los campos calculados"""
    disponible = max(0, limite - usado)
    porcentaje_uso = round((usado / limite) * 100, 2) if limite > 0 else 0.0
    
    return LimiteRecurso(
        tipo=recurso_tipo,
        limite=limite,
        usado=usado,
        disponible=disponible,
        porcentaje_uso=porcentaje_uso
    )

class LimiteService:
    """Servicio para validación y gestión de límites de suscripción"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================
    # OBTENER SUSCRIPCIÓN ACTIVA
    # ========================================
    
    def obtener_suscripcion_activa(self, user_id: int) -> Optional[Dict]:
        """Obtiene la suscripción activa del usuario"""
        try:
            
            suscripcion = self.db.query(Suscripcion).filter(
                and_(
                    Suscripcion.user_id == user_id,
                    Suscripcion.status == 'active'
                )
            ).first()
            
            if not suscripcion:
                logger.warning(f"Usuario {user_id} no tiene suscripción activa")
                return None
                
            return {
                'id': suscripcion.id,
                'plan_type': suscripcion.plan_type,
                'plan_name': suscripcion.plan_name,
                'gallos_maximo': suscripcion.gallos_maximo,
                'topes_por_gallo': suscripcion.topes_por_gallo,
                'peleas_por_gallo': suscripcion.peleas_por_gallo,
                'vacunas_por_gallo': suscripcion.vacunas_por_gallo,
                'fecha_fin': suscripcion.fecha_fin
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo suscripción para user {user_id}: {e}")
            return None
    
    # ========================================
    # CONTADORES DE USO ACTUAL
    # ========================================
    
    def contar_gallos(self, user_id: int) -> int:
        """Cuenta los gallos actuales del usuario"""
        try:
            count = self.db.query(func.count(Gallo.id)).filter(
                Gallo.user_id == user_id
            ).scalar() or 0
            
            logger.debug(f"Usuario {user_id} tiene {count} gallos")
            return count
            
        except Exception as e:
            logger.error(f"Error contando gallos para user {user_id}: {e}")
            return 0
    
    def contar_topes(self, user_id: int, gallo_id: Optional[int] = None) -> int:
        """Cuenta los topes del usuario o de un gallo específico"""
        try:
            query = self.db.query(func.count(Tope.id)).filter(Tope.user_id == user_id)
            
            if gallo_id:
                query = query.filter(Tope.gallo_id == gallo_id)
            
            count = query.scalar() or 0
            logger.debug(f"Usuario {user_id}, gallo {gallo_id}: {count} topes")
            return count
            
        except Exception as e:
            logger.error(f"Error contando topes para user {user_id}, gallo {gallo_id}: {e}")
            return 0
    
    def contar_peleas(self, user_id: int, gallo_id: Optional[int] = None) -> int:
        """Cuenta las peleas del usuario o de un gallo específico"""
        try:
            query = self.db.query(func.count(Pelea.id)).filter(Pelea.user_id == user_id)
            
            if gallo_id:
                query = query.filter(Pelea.gallo_id == gallo_id)
            
            count = query.scalar() or 0
            logger.debug(f"Usuario {user_id}, gallo {gallo_id}: {count} peleas")
            return count
            
        except Exception as e:
            logger.error(f"Error contando peleas para user {user_id}, gallo {gallo_id}: {e}")
            return 0
    
    def contar_vacunas(self, user_id: int, gallo_id: Optional[int] = None) -> int:
        """Cuenta las vacunas del usuario o de un gallo específico"""
        try:
            # Las vacunas no tienen user_id, se relacionan a través del gallo
            if gallo_id:
                # Contar vacunas específicas de un gallo
                query = self.db.query(func.count(Vacuna.id)).filter(Vacuna.gallo_id == gallo_id)
            else:
                # Contar todas las vacunas del usuario (a través de sus gallos)
                query = self.db.query(func.count(Vacuna.id)).join(
                    Gallo, Vacuna.gallo_id == Gallo.id
                ).filter(Gallo.user_id == user_id)
            
            count = query.scalar() or 0
            logger.debug(f"Usuario {user_id}, gallo {gallo_id}: {count} vacunas")
            return count
            
        except Exception as e:
            logger.error(f"Error contando vacunas para user {user_id}, gallo {gallo_id}: {e}")
            return 0
    
    # ========================================
    # VALIDACIÓN DE LÍMITES
    # ========================================
    
    def validar_limite_gallos(self, user_id: int) -> ValidacionLimite:
        """Valida si el usuario puede crear más gallos"""
        suscripcion = self.obtener_suscripcion_activa(user_id)
        if not suscripcion:
            return ValidacionLimite(
                puede_crear=False,
                recurso_tipo=RecursoTipo.GALLOS,
                limite_actual=0,
                cantidad_usada=0,
                mensaje_error="Sin suscripción activa",
                upgrade_disponible=True
            )
        
        gallos_actuales = self.contar_gallos(user_id)
        limite = suscripcion['gallos_maximo']
        
        puede_crear = gallos_actuales < limite
        
        return ValidacionLimite(
            puede_crear=puede_crear,
            recurso_tipo=RecursoTipo.GALLOS,
            limite_actual=limite,
            cantidad_usada=gallos_actuales,
            mensaje_error=None if puede_crear else f"Límite de gallos alcanzado ({gallos_actuales}/{limite})",
            plan_recomendado="premium" if suscripcion['plan_type'] == 'gratuito' else "profesional"
        )
    
    def validar_limite_por_gallo(self, user_id: int, gallo_id: int, recurso_tipo: RecursoTipo) -> ValidacionLimite:
        """Valida límites por gallo (topes, peleas, vacunas)"""
        suscripcion = self.obtener_suscripcion_activa(user_id)
        if not suscripcion:
            return ValidacionLimite(
                puede_crear=False,
                recurso_tipo=recurso_tipo,
                limite_actual=0,
                cantidad_usada=0,
                gallo_id=gallo_id,
                mensaje_error="Sin suscripción activa"
            )
        
        # Verificar que el gallo pertenece al usuario
        gallo = self.db.query(Gallo).filter(
            and_(Gallo.id == gallo_id, Gallo.user_id == user_id)
        ).first()
        
        if not gallo:
            return ValidacionLimite(
                puede_crear=False,
                recurso_tipo=recurso_tipo,
                limite_actual=0,
                cantidad_usada=0,
                gallo_id=gallo_id,
                mensaje_error="Gallo no encontrado o no autorizado"
            )
        
        # Obtener contador y límite según el tipo
        if recurso_tipo == RecursoTipo.TOPES:
            count_actual = self.contar_topes(user_id, gallo_id)
            limite = suscripcion['topes_por_gallo']
        elif recurso_tipo == RecursoTipo.PELEAS:
            count_actual = self.contar_peleas(user_id, gallo_id)
            limite = suscripcion['peleas_por_gallo']
        elif recurso_tipo == RecursoTipo.VACUNAS:
            count_actual = self.contar_vacunas(user_id, gallo_id)
            limite = suscripcion['vacunas_por_gallo']
        else:
            return ValidacionLimite(
                puede_crear=False,
                recurso_tipo=recurso_tipo,
                limite_actual=0,
                cantidad_usada=0,
                gallo_id=gallo_id,
                mensaje_error="Tipo de recurso no válido"
            )
        
        puede_crear = count_actual < limite
        
        return ValidacionLimite(
            puede_crear=puede_crear,
            recurso_tipo=recurso_tipo,
            limite_actual=limite,
            cantidad_usada=count_actual,
            gallo_id=gallo_id,
            mensaje_error=None if puede_crear else f"Límite de {recurso_tipo.value} alcanzado para este gallo ({count_actual}/{limite})",
            plan_recomendado="premium" if suscripcion['plan_type'] == 'gratuito' else "profesional"
        )
    
    # ========================================
    # ESTADO COMPLETO DE LÍMITES
    # ========================================
    
    def obtener_estado_limites(self, user_id: int) -> EstadoLimites:
        """Obtiene el estado completo de límites del usuario"""
        suscripcion = self.obtener_suscripcion_activa(user_id)
        
        if not suscripcion:
            return EstadoLimites(
                user_id=user_id,
                plan_actual="sin_plan",
                suscripcion_activa=False,
                fecha_vencimiento=None,
                gallos=crear_limite_recurso_completo(RecursoTipo.GALLOS, 0, 0),
                tiene_limites_superados=True,
                recursos_en_limite=["sin_suscripcion"]
            )
        
        # Contador de gallos
        gallos_count = self.contar_gallos(user_id)
        gallos_limite = crear_limite_recurso_completo(
            RecursoTipo.GALLOS,
            suscripcion['gallos_maximo'],
            gallos_count
        )
        
        # Obtener gallos del usuario para límites individuales
        gallos = self.db.query(Gallo).filter(Gallo.user_id == user_id).all()
        
        topes_por_gallo = {}
        peleas_por_gallo = {}
        vacunas_por_gallo = {}
        recursos_en_limite = []
        
        for gallo in gallos:
            # Topes
            topes_count = self.contar_topes(user_id, gallo.id)
            topes_por_gallo[gallo.id] = crear_limite_recurso_completo(
                RecursoTipo.TOPES,
                suscripcion['topes_por_gallo'],
                topes_count
            )
            if topes_count >= suscripcion['topes_por_gallo']:
                recursos_en_limite.append(f"topes_gallo_{gallo.id}")
            
            # Peleas
            peleas_count = self.contar_peleas(user_id, gallo.id)
            peleas_por_gallo[gallo.id] = crear_limite_recurso_completo(
                RecursoTipo.PELEAS,
                suscripcion['peleas_por_gallo'],
                peleas_count
            )
            if peleas_count >= suscripcion['peleas_por_gallo']:
                recursos_en_limite.append(f"peleas_gallo_{gallo.id}")
            
            # Vacunas
            vacunas_count = self.contar_vacunas(user_id, gallo.id)
            vacunas_por_gallo[gallo.id] = crear_limite_recurso_completo(
                RecursoTipo.VACUNAS,
                suscripcion['vacunas_por_gallo'],
                vacunas_count
            )
            if vacunas_count >= suscripcion['vacunas_por_gallo']:
                recursos_en_limite.append(f"vacunas_gallo_{gallo.id}")
        
        # Verificar límite general de gallos
        if gallos_count >= suscripcion['gallos_maximo']:
            recursos_en_limite.append("gallos")
        
        return EstadoLimites(
            user_id=user_id,
            plan_actual=suscripcion['plan_type'],
            suscripcion_activa=True,
            fecha_vencimiento=suscripcion['fecha_fin'],
            gallos=gallos_limite,
            topes=topes_por_gallo if topes_por_gallo else None,
            peleas=peleas_por_gallo if peleas_por_gallo else None,
            vacunas=vacunas_por_gallo if vacunas_por_gallo else None,
            tiene_limites_superados=len(recursos_en_limite) > 0,
            recursos_en_limite=recursos_en_limite
        )
    
    # ========================================
    # UTILIDADES
    # ========================================
    
    def obtener_plan_recomendado(self, plan_actual: str) -> str:
        """Obtiene el plan recomendado para upgrade"""
        if plan_actual == 'gratuito':
            return 'premium'  # Saltar básico, ir directo a premium
        elif plan_actual == 'basico':
            return 'premium'
        elif plan_actual == 'premium':
            return 'profesional'
        else:
            return 'profesional'
    
    def es_plan_premium(self, plan_type: str) -> bool:
        """Verifica si es un plan de pago"""
        return plan_type in ['basico', 'premium', 'profesional']
    
    def dias_hasta_vencimiento(self, fecha_fin: Optional[date]) -> Optional[int]:
        """Calcula días hasta el vencimiento"""
        if not fecha_fin:
            return None
        
        delta = fecha_fin - date.today()
        return delta.days

# ========================================
# FUNCIONES HELPER PARA ENDPOINTS
# ========================================

def validar_limite_recurso(
    db: Session, 
    user_id: int, 
    recurso_tipo: RecursoTipo, 
    gallo_id: Optional[int] = None
) -> ValidacionLimite:
    """Helper function para validar límites en endpoints"""
    service = LimiteService(db)
    
    if recurso_tipo == RecursoTipo.GALLOS:
        return service.validar_limite_gallos(user_id)
    else:
        if not gallo_id:
            raise ValueError("gallo_id es requerido para este tipo de recurso")
        return service.validar_limite_por_gallo(user_id, gallo_id, recurso_tipo)

def obtener_limites_usuario(db: Session, user_id: int) -> EstadoLimites:
    """Helper function para obtener límites completos"""
    service = LimiteService(db)
    return service.obtener_estado_limites(user_id)