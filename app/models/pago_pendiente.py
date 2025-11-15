# 💳 Modelo de Pagos Pendientes - Sistema Yape
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
from enum import Enum

class EstadoPago(str, Enum):
    """Estados posibles de un pago"""
    PENDIENTE = "pendiente"
    VERIFICANDO = "verificando" 
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"

class MetodoPago(str, Enum):
    """Métodos de pago soportados"""
    YAPE = "yape"
    PLIN = "plin"
    TRANSFERENCIA = "transferencia"

class PagoPendiente(Base):
    """Pagos pendientes de verificación manual"""
    __tablename__ = "pagos_pendientes"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_codigo = Column(String(20), nullable=False)
    
    # Datos del pago
    monto = Column(DECIMAL(8, 2), nullable=False)
    metodo_pago = Column(String(20), default=MetodoPago.YAPE)
    referencia_yape = Column(String(100))  # Número de operación Yape
    
    # QR y comprobantes
    qr_data = Column(Text)  # Data del QR generado
    qr_url = Column(Text)   # URL imagen QR en ImageKit
    comprobante_url = Column(Text)  # Screenshot del pago
    comprobante_file_id = Column(String(255))  # ImageKit file_id para eliminar comprobante
    
    # Estados y verificación
    estado = Column(String(20), default=EstadoPago.PENDIENTE, index=True)
    fecha_pago_usuario = Column(DateTime)  # Cuando user dice que pagó
    fecha_verificacion = Column(DateTime)  # Cuando admin verifica
    verificado_por = Column(Integer, ForeignKey("users.id"))
    notas_admin = Column(Text)  # Comentarios del admin
    
    # Seguridad y tracking
    intentos = Column(Integer, default=0)  # Intentos de verificación
    ip_address = Column(String(45))  # IP del usuario
    user_agent = Column(Text)  # Browser info
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    usuario = relationship("User", foreign_keys=[user_id])
    verificador = relationship("User", foreign_keys=[verificado_por])
    
    def __repr__(self):
        return f"<PagoPendiente(id={self.id}, user_id={self.user_id}, monto={self.monto}, estado='{self.estado}')>"
    
    @property
    def esta_pendiente(self):
        """Verifica si el pago está pendiente"""
        return self.estado == EstadoPago.PENDIENTE
    
    @property
    def esta_verificando(self):
        """Verifica si el pago está en verificación"""
        return self.estado == EstadoPago.VERIFICANDO
    
    @property
    def esta_aprobado(self):
        """Verifica si el pago fue aprobado"""
        return self.estado == EstadoPago.APROBADO
    
    @property
    def esta_rechazado(self):
        """Verifica si el pago fue rechazado"""
        return self.estado == EstadoPago.RECHAZADO
    
    @property
    def puede_verificar(self):
        """Verifica si el pago puede ser verificado"""
        return self.estado in [EstadoPago.PENDIENTE, EstadoPago.VERIFICANDO]
    
    def marcar_como_verificando(self):
        """Marca el pago como en verificación"""
        self.estado = EstadoPago.VERIFICANDO
        self.updated_at = datetime.utcnow()
    
    def aprobar_pago(self, admin_id: int, notas: str = None):
        """Aprueba el pago"""
        self.estado = EstadoPago.APROBADO
        self.verificado_por = admin_id
        self.fecha_verificacion = datetime.utcnow()
        if notas:
            self.notas_admin = notas
        self.updated_at = datetime.utcnow()
    
    def rechazar_pago(self, admin_id: int, notas: str = None):
        """Rechaza el pago"""
        self.estado = EstadoPago.RECHAZADO
        self.verificado_por = admin_id
        self.fecha_verificacion = datetime.utcnow()
        if notas:
            self.notas_admin = notas
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_codigo': self.plan_codigo,
            'monto': float(self.monto),
            'metodo_pago': self.metodo_pago,
            'referencia_yape': self.referencia_yape,
            'qr_data': self.qr_data,  # CAMPO AGREGADO
            'qr_url': self.qr_url,
            'comprobante_url': self.comprobante_url,
            'estado': self.estado,
            'fecha_pago_usuario': self.fecha_pago_usuario.isoformat() if self.fecha_pago_usuario else None,
            'fecha_verificacion': self.fecha_verificacion.isoformat() if self.fecha_verificacion else None,
            'verificado_por': self.verificado_por,  # CAMPO AGREGADO
            'notas_admin': self.notas_admin,
            'intentos': self.intentos or 0,  # CAMPO AGREGADO
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,  # CAMPO AGREGADO
        }