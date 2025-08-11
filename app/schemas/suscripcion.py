# 📋 Schemas Pydantic para Suscripciones - Validaciones Completas
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List
from datetime import datetime, date
from enum import Enum
from decimal import Decimal

# ========================================
# ENUMS
# ========================================

class PlanTipo(str, Enum):
    """Tipos de plan disponibles"""
    GRATUITO = "gratuito"
    BASICO = "basico"
    PREMIUM = "premium"
    PROFESIONAL = "profesional"

class EstadoSuscripcion(str, Enum):
    """Estados de suscripción"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"

class RecursoTipo(str, Enum):
    """Tipos de recursos con límites"""
    GALLOS = "gallos"
    TOPES = "topes"
    PELEAS = "peleas" 
    VACUNAS = "vacunas"

# ========================================
# SCHEMAS BASE
# ========================================

class SuscripcionBase(BaseModel):
    """Schema base para suscripciones"""
    plan_type: str = Field(..., description="Tipo de plan")
    plan_name: str = Field(..., description="Nombre del plan")
    precio: Decimal = Field(..., ge=0, description="Precio del plan")
    
    # Límites
    gallos_maximo: int = Field(..., ge=1, le=999, description="Máximo de gallos permitidos")
    topes_por_gallo: int = Field(..., ge=1, le=999, description="Topes por gallo")
    peleas_por_gallo: int = Field(..., ge=1, le=999, description="Peleas por gallo")
    vacunas_por_gallo: int = Field(..., ge=1, le=999, description="Vacunas por gallo")

class SuscripcionCreate(SuscripcionBase):
    """Schema para crear suscripción"""
    user_id: int = Field(..., gt=0, description="ID del usuario")
    fecha_inicio: date = Field(default_factory=date.today, description="Fecha de inicio")
    fecha_fin: Optional[date] = Field(None, description="Fecha de finalización")
    
    @validator('fecha_fin')
    def validar_fecha_fin(cls, v, values):
        if v and 'fecha_inicio' in values and v <= values['fecha_inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

class SuscripcionUpdate(BaseModel):
    """Schema para actualizar suscripción"""
    plan_type: Optional[str] = None
    plan_name: Optional[str] = None
    precio: Optional[Decimal] = Field(None, ge=0)
    status: Optional[EstadoSuscripcion] = None
    fecha_fin: Optional[date] = None
    
    # Límites actualizables
    gallos_maximo: Optional[int] = Field(None, ge=1, le=999)
    topes_por_gallo: Optional[int] = Field(None, ge=1, le=999) 
    peleas_por_gallo: Optional[int] = Field(None, ge=1, le=999)
    vacunas_por_gallo: Optional[int] = Field(None, ge=1, le=999)

class SuscripcionResponse(SuscripcionBase):
    """Schema de respuesta para suscripción"""
    id: int
    user_id: int
    status: str
    fecha_inicio: date
    fecha_fin: Optional[date]
    created_at: datetime
    updated_at: datetime
    
    # Campos calculados
    dias_restantes: Optional[int] = None
    esta_activa: bool = Field(default=True)
    es_premium: bool = Field(default=False)
    
    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: float,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

# ========================================
# SCHEMAS DE PLANES
# ========================================

class PlanCatalogoResponse(BaseModel):
    """Schema de respuesta para plan del catálogo"""
    id: int
    codigo: str
    nombre: str
    precio: Decimal
    duracion_dias: int
    
    # Límites
    gallos_maximo: int
    topes_por_gallo: int
    peleas_por_gallo: int
    vacunas_por_gallo: int
    
    # Características
    soporte_premium: bool
    respaldo_nube: bool
    estadisticas_avanzadas: bool
    videos_ilimitados: bool
    
    # UI
    destacado: bool
    activo: bool
    orden: int
    
    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: float
        }

# ========================================
# SCHEMAS DE LÍMITES Y USO
# ========================================

class LimiteRecurso(BaseModel):
    """Schema para límites de un recurso"""
    tipo: RecursoTipo
    limite: int = Field(..., ge=0, description="Límite máximo")
    usado: int = Field(..., ge=0, description="Cantidad usada")
    disponible: Optional[int] = Field(None, ge=0, description="Cantidad disponible")
    porcentaje_uso: Optional[float] = Field(None, ge=0, le=100, description="Porcentaje de uso")
    
    @validator('disponible', always=True)
    def calcular_disponible(cls, v, values):
        if v is None and 'limite' in values and 'usado' in values:
            return max(0, values['limite'] - values['usado'])
        return v if v is not None else 0
    
    @validator('porcentaje_uso', always=True) 
    def calcular_porcentaje(cls, v, values):
        if v is None and 'limite' in values and 'usado' in values and values['limite'] > 0:
            return round((values['usado'] / values['limite']) * 100, 2)
        return v if v is not None else 0.0

class EstadoLimites(BaseModel):
    """Schema para estado completo de límites"""
    user_id: int
    plan_actual: str
    suscripcion_activa: bool
    fecha_vencimiento: Optional[date]
    
    # Límites por recurso
    gallos: LimiteRecurso
    topes: Optional[Dict[int, LimiteRecurso]] = None  # Por gallo_id
    peleas: Optional[Dict[int, LimiteRecurso]] = None  # Por gallo_id
    vacunas: Optional[Dict[int, LimiteRecurso]] = None  # Por gallo_id
    
    # Estado general
    tiene_limites_superados: bool = False
    recursos_en_limite: List[str] = []
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }

# ========================================
# SCHEMAS DE UPGRADE
# ========================================

class UpgradeRequest(BaseModel):
    """Schema para solicitar upgrade de plan"""
    plan_codigo: PlanTipo = Field(..., description="Código del plan destino")
    metodo_pago: str = Field(default="yape", description="Método de pago")
    
    @validator('plan_codigo')
    def validar_plan(cls, v):
        if v == PlanTipo.GRATUITO:
            raise ValueError('No se puede hacer upgrade al plan gratuito')
        return v

class UpgradeResponse(BaseModel):
    """Schema de respuesta para upgrade"""
    pago_id: int
    qr_data: str
    qr_url: str
    monto: Decimal
    plan_nombre: str
    instrucciones: List[str]
    
    class Config:
        json_encoders = {
            Decimal: float
        }

# ========================================
# SCHEMAS DE VALIDACIÓN
# ========================================

class ValidacionLimite(BaseModel):
    """Schema para validación de límites"""
    puede_crear: bool
    recurso_tipo: RecursoTipo
    limite_actual: int
    cantidad_usada: int
    gallo_id: Optional[int] = None
    
    # Si no puede crear
    mensaje_error: Optional[str] = None
    plan_recomendado: Optional[str] = None
    upgrade_disponible: bool = True

class ValidacionLimiteRequest(BaseModel):
    """Schema para request de validación"""
    recurso_tipo: RecursoTipo
    gallo_id: Optional[int] = Field(None, description="ID del gallo (para topes/peleas/vacunas)")
    
    @validator('gallo_id')
    def validar_gallo_requerido(cls, v, values):
        if 'recurso_tipo' in values:
            tipos_requieren_gallo = [RecursoTipo.TOPES, RecursoTipo.PELEAS, RecursoTipo.VACUNAS]
            if values['recurso_tipo'] in tipos_requieren_gallo and v is None:
                raise ValueError(f'gallo_id es requerido para {values["recurso_tipo"]}')
        return v

# ========================================
# SCHEMAS DE ESTADÍSTICAS
# ========================================

class EstadisticasSuscripcion(BaseModel):
    """Schema para estadísticas de suscripciones"""
    total_usuarios: int
    usuarios_gratuitos: int
    usuarios_premium: int
    ingresos_mes_actual: Decimal
    ingresos_mes_anterior: Decimal
    conversion_rate: float  # % de gratuitos que se vuelven premium
    
    # Distribución por plan
    distribucion_planes: Dict[str, int]
    
    # Métricas de tiempo
    promedio_dias_hasta_upgrade: Optional[float] = None
    tasa_renovacion: float = 0.0
    
    class Config:
        json_encoders = {
            Decimal: float
        }