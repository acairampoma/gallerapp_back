# 💳 Schemas Pydantic para Pagos - Sistema Yape
from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from decimal import Decimal

# ========================================
# ENUMS
# ========================================

class EstadoPago(str, Enum):
    """Estados de pago"""
    PENDIENTE = "pendiente"
    VERIFICANDO = "verificando"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"

class MetodoPago(str, Enum):
    """Métodos de pago soportados"""
    YAPE = "yape"
    PLIN = "plin"
    TRANSFERENCIA = "transferencia"

class AccionAdmin(str, Enum):
    """Acciones que puede realizar un admin"""
    APROBAR = "aprobar"
    RECHAZAR = "rechazar"
    SOLICITAR_INFO = "solicitar_info"

# ========================================
# SCHEMAS BASE
# ========================================

class PagoBase(BaseModel):
    """Schema base para pagos"""
    plan_codigo: str = Field(..., min_length=3, max_length=20, description="Código del plan")
    monto: Decimal = Field(..., gt=0, le=1000, description="Monto a pagar en soles")
    metodo_pago: MetodoPago = Field(default=MetodoPago.YAPE, description="Método de pago")
    
    @validator('monto')
    def validar_monto(cls, v):
        if v <= 0:
            raise ValueError('El monto debe ser mayor a 0')
        if v > 1000:
            raise ValueError('El monto máximo es S/. 1000')
        return round(v, 2)

class PagoCreate(PagoBase):
    """Schema para crear pago"""
    referencia_yape: Optional[str] = Field(None, max_length=100, description="Número de operación Yape")
    
class PagoUpdate(BaseModel):
    """Schema para actualizar pago"""
    referencia_yape: Optional[str] = Field(None, max_length=100)
    comprobante_url: Optional[HttpUrl] = Field(None, description="URL del comprobante")
    estado: Optional[EstadoPago] = None

class PagoResponse(PagoBase):
    """Schema de respuesta para pago"""
    id: int
    user_id: int
    estado: EstadoPago
    qr_data: Optional[str] = None
    qr_url: Optional[HttpUrl] = None
    comprobante_url: Optional[HttpUrl] = None
    referencia_yape: Optional[str] = None
    
    # Fechas
    fecha_pago_usuario: Optional[datetime] = None
    fecha_verificacion: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Verificación admin
    verificado_por: Optional[int] = None
    notas_admin: Optional[str] = None
    
    # Datos adicionales
    intentos: int = 0
    
    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: float,
            datetime: lambda v: v.isoformat()
        }

# ========================================
# SCHEMAS DE QR YAPE
# ========================================

class QRYapeRequest(BaseModel):
    """Schema para generar QR Yape"""
    plan_codigo: str = Field(..., description="Código del plan")
    
    @validator('plan_codigo')
    def validar_plan_codigo(cls, v):
        planes_validos = ['basico', 'premium', 'profesional']
        if v.lower() not in planes_validos:
            raise ValueError(f'Plan debe ser uno de: {", ".join(planes_validos)}')
        return v.lower()

class QRYapeResponse(BaseModel):
    """Schema de respuesta para QR Yape"""
    pago_id: int
    qr_data: str = Field(..., description="Datos del QR en formato texto")
    qr_url: HttpUrl = Field(..., description="URL de imagen QR en Cloudinary")
    monto: Decimal
    plan_nombre: str
    
    # Instrucciones paso a paso
    instrucciones: List[str] = [
        "1. Abre tu app Yape",
        "2. Escanea este código QR",
        "3. Confirma el pago por el monto exacto",
        "4. Toma captura del comprobante",
        "5. Sube la captura en la siguiente pantalla"
    ]
    
    # Info adicional
    tiempo_expiracion_minutos: int = 30
    numero_contacto: str = "+51 999 999 999"
    
    class Config:
        json_encoders = {
            Decimal: float
        }

# ========================================
# SCHEMAS DE CONFIRMACIÓN
# ========================================

class ConfirmarPagoRequest(BaseModel):
    """Schema para confirmar pago realizado"""
    pago_id: int = Field(..., gt=0, description="ID del pago")
    referencia_yape: Optional[str] = Field(None, max_length=100, description="Número de operación")
    comprobante_base64: Optional[str] = Field(None, description="Imagen en base64")
    
    @validator('comprobante_base64')
    def validar_comprobante(cls, v):
        if v and len(v) > 5_000_000:  # ~5MB en base64
            raise ValueError('El comprobante es muy grande (máx. 5MB)')
        return v

class ConfirmarPagoResponse(BaseModel):
    """Schema de respuesta para confirmación"""
    pago_id: int
    estado: EstadoPago
    mensaje: str
    comprobante_subido: bool = False
    tiempo_verificacion_estimado: str = "2-24 horas"
    
    # Siguiente paso
    siguiente_accion: str = "Esperar verificación del administrador"
    contacto_soporte: str = "soporte@galloapp.com"

# ========================================
# SCHEMAS DE ADMINISTRACIÓN
# ========================================

class PagoPendienteAdmin(PagoResponse):
    """Schema extendido para admins"""
    usuario_email: str
    usuario_nombre: Optional[str] = None
    plan_nombre_completo: str
    
    # Datos técnicos
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Análisis
    tiempo_transcurrido_horas: float
    es_sospechoso: bool = False
    razon_sospecha: Optional[str] = None
    
    class Config:
        orm_mode = True

class AccionAdminRequest(BaseModel):
    """Schema para acciones de admin"""
    accion: AccionAdmin = Field(..., description="Acción a realizar")
    notas: Optional[str] = Field(None, max_length=500, description="Notas del administrador")
    
    @validator('notas')
    def validar_notas_rechazar(cls, v, values):
        if 'accion' in values and values['accion'] == AccionAdmin.RECHAZAR and not v:
            raise ValueError('Las notas son obligatorias al rechazar un pago')
        return v

class AccionAdminResponse(BaseModel):
    """Schema de respuesta para acción de admin"""
    pago_id: int
    accion_realizada: AccionAdmin
    estado_anterior: EstadoPago
    estado_nuevo: EstadoPago
    admin_id: int
    notas: Optional[str] = None
    fecha_accion: datetime
    notificacion_enviada: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# ========================================
# SCHEMAS DE ESTADÍSTICAS
# ========================================

class EstadisticasPagos(BaseModel):
    """Schema para estadísticas de pagos"""
    total_pagos: int
    pagos_pendientes: int
    pagos_aprobados: int
    pagos_rechazados: int
    
    # Montos
    monto_total_pendiente: Decimal
    monto_total_aprobado: Decimal
    ingresos_mes_actual: Decimal
    
    # Tiempos
    tiempo_promedio_verificacion_horas: float
    pagos_vencidos: int  # Más de 48 horas pendientes
    
    # Distribución por plan
    distribucion_por_plan: Dict[str, int]
    
    # Métodos de pago
    distribucion_metodos: Dict[str, int]
    
    class Config:
        json_encoders = {
            Decimal: float
        }

class DashboardAdmin(BaseModel):
    """Schema para dashboard de administrador"""
    # Resumen rápido
    pagos_requieren_atencion: int
    notificaciones_no_leidas: int
    usuarios_nuevos_hoy: int
    ingresos_hoy: Decimal
    
    # Alertas
    alertas_urgentes: List[str] = []
    
    # Gráficos
    pagos_ultimos_7_dias: List[Dict[str, Any]]
    conversion_por_dia: List[Dict[str, Any]]
    
    class Config:
        json_encoders = {
            Decimal: float
        }

# ========================================
# SCHEMAS DE WEBHOOK
# ========================================

class WebhookYape(BaseModel):
    """Schema para webhook de Yape (si está disponible)"""
    transaction_id: str
    amount: Decimal
    currency: str = "PEN"
    status: str
    reference: Optional[str] = None
    timestamp: datetime
    
    # Validación
    signature: str  # Para verificar autenticidad
    
    class Config:
        json_encoders = {
            Decimal: float,
            datetime: lambda v: v.isoformat()
        }