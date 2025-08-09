# 🔔 Modelo de Notificaciones para Administradores
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
from enum import Enum

class TipoNotificacion(str, Enum):
    """Tipos de notificaciones para admins"""
    NUEVO_PAGO = "nuevo_pago"
    PAGO_CONFIRMADO = "pago_confirmado"
    USUARIO_PREMIUM_VENCIDO = "usuario_premium_vencido"
    ERROR_SISTEMA = "error_sistema"
    USUARIO_REGISTRADO = "usuario_registrado"
    LIMITE_ALCANZADO = "limite_alcanzado"

class PrioridadNotificacion(str, Enum):
    """Prioridades de notificaciones"""
    BAJA = "baja"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"

class NotificacionAdmin(Base):
    """Notificaciones para administradores del sistema"""
    __tablename__ = "notificaciones_admin"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tipo = Column(String(50), nullable=False, index=True)
    titulo = Column(String(255), nullable=False)
    mensaje = Column(Text, nullable=False)
    data = Column(JSON)  # Datos adicionales (pago_id, user_id, etc)
    
    # Estados
    leido = Column(Boolean, default=False, index=True)
    procesado = Column(Boolean, default=False)
    fecha_leido = Column(DateTime)
    
    # Prioridad
    prioridad = Column(String(10), default=PrioridadNotificacion.NORMAL, index=True)
    
    # Timestamp
    created_at = Column(DateTime, server_default=func.now())
    
    # Relaciones
    admin = relationship("User", foreign_keys=[admin_id])
    
    def __repr__(self):
        return f"<NotificacionAdmin(id={self.id}, tipo='{self.tipo}', leido={self.leido})>"
    
    @property
    def es_urgente(self):
        """Verifica si la notificación es urgente"""
        return self.prioridad == PrioridadNotificacion.URGENTE
    
    @property
    def es_alta_prioridad(self):
        """Verifica si la notificación es de alta prioridad"""
        return self.prioridad in [PrioridadNotificacion.ALTA, PrioridadNotificacion.URGENTE]
    
    @property
    def tiempo_transcurrido(self):
        """Calcula el tiempo transcurrido desde creación"""
        if not self.created_at:
            return None
        delta = datetime.utcnow() - self.created_at
        return delta.total_seconds()
    
    def marcar_como_leido(self):
        """Marca la notificación como leída"""
        self.leido = True
        self.fecha_leido = datetime.utcnow()
    
    def marcar_como_procesado(self):
        """Marca la notificación como procesada"""
        self.procesado = True
        if not self.leido:
            self.marcar_como_leido()
    
    @classmethod
    def crear_notificacion_pago(cls, admin_id: int, pago_id: int, user_email: str):
        """Factory method para crear notificación de nuevo pago"""
        return cls(
            admin_id=admin_id,
            tipo=TipoNotificacion.NUEVO_PAGO,
            titulo="💰 Nuevo Pago Pendiente",
            mensaje=f"El usuario {user_email} ha realizado un pago que requiere verificación",
            data={'pago_id': pago_id, 'user_email': user_email},
            prioridad=PrioridadNotificacion.ALTA
        )
    
    @classmethod
    def crear_notificacion_registro(cls, admin_id: int, user_id: int, user_email: str):
        """Factory method para crear notificación de nuevo usuario"""
        return cls(
            admin_id=admin_id,
            tipo=TipoNotificacion.USUARIO_REGISTRADO,
            titulo="👋 Nuevo Usuario Registrado",
            mensaje=f"Se ha registrado un nuevo usuario: {user_email}",
            data={'user_id': user_id, 'user_email': user_email},
            prioridad=PrioridadNotificacion.NORMAL
        )
    
    @classmethod
    def crear_notificacion_limite(cls, admin_id: int, user_id: int, recurso: str, limite: int):
        """Factory method para crear notificación de límite alcanzado"""
        return cls(
            admin_id=admin_id,
            tipo=TipoNotificacion.LIMITE_ALCANZADO,
            titulo="⚠️ Usuario Alcanzó Límite",
            mensaje=f"Usuario ha alcanzado el límite de {recurso}: {limite}",
            data={'user_id': user_id, 'recurso': recurso, 'limite': limite},
            prioridad=PrioridadNotificacion.NORMAL
        )
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'tipo': self.tipo,
            'titulo': self.titulo,
            'mensaje': self.mensaje,
            'data': self.data,
            'leido': self.leido,
            'procesado': self.procesado,
            'prioridad': self.prioridad,
            'fecha_leido': self.fecha_leido.isoformat() if self.fecha_leido else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'tiempo_transcurrido': self.tiempo_transcurrido,
        }