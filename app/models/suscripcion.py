# 📋 Modelo de Suscripciones - Sistema Premium
from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import date

class Suscripcion(Base):
    """Modelo para suscripciones de usuarios - COINCIDE CON BD POSTGRESQL"""
    __tablename__ = "suscripciones"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Información del plan
    plan_type = Column(String(50), nullable=False, default="gratuito")  # gratuito, basico, premium, profesional
    plan_name = Column(String(100), nullable=False, default="Plan Gratuito")
    precio = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    # Estado de la suscripción
    status = Column(String(20), nullable=False, default="active")  # active, inactive, expired, cancelled
    
    # Fechas
    fecha_inicio = Column(Date, nullable=False, default=date.today)
    fecha_fin = Column(Date, nullable=True)  # NULL = sin vencimiento
    
    # Límites del plan (copiados del plan_catalogo al activarse)
    gallos_maximo = Column(Integer, nullable=False, default=5)
    topes_por_gallo = Column(Integer, nullable=False, default=2)
    peleas_por_gallo = Column(Integer, nullable=False, default=2)
    vacunas_por_gallo = Column(Integer, nullable=False, default=2)
    # marketplace_publicaciones_max se obtiene via JOIN con planes_catalogo
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="suscripciones")
    
    def __repr__(self):
        return f"<Suscripcion(id={self.id}, user_id={self.user_id}, plan={self.plan_type}, status={self.status})>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan_type": self.plan_type,
            "plan_name": self.plan_name,
            "precio": float(self.precio) if self.precio else 0.0,
            "status": self.status,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
            "gallos_maximo": self.gallos_maximo,
            "topes_por_gallo": self.topes_por_gallo,
            "peleas_por_gallo": self.peleas_por_gallo,
            "vacunas_por_gallo": self.vacunas_por_gallo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def es_premium(self) -> bool:
        """Indica si es un plan de pago"""
        return self.plan_type in ["basico", "premium", "profesional"] and self.precio > 0
    
    @property
    def esta_activa(self) -> bool:
        """Indica si la suscripción está activa"""
        if self.status != "active":
            return False
        
        if self.fecha_fin and self.fecha_fin < date.today():
            return False
            
        return True
    
    @property
    def dias_restantes(self) -> int:
        """Días restantes hasta el vencimiento"""
        if not self.fecha_fin:
            return 999  # Sin vencimiento
        
        delta = self.fecha_fin - date.today()
        return max(0, delta.days)