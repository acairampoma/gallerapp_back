# 📋 Modelo de Planes de Suscripción - Catálogo
from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, DateTime
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime

class PlanCatalogo(Base):
    """Catálogo de planes de suscripción disponibles"""
    __tablename__ = "planes_catalogo"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False, index=True)  # 'gratuito', 'premium', etc
    nombre = Column(String(100), nullable=False)
    precio = Column(DECIMAL(8, 2), default=0.00, nullable=False)
    duracion_dias = Column(Integer, default=30, nullable=False)
    
    # Límites del plan
    gallos_maximo = Column(Integer, nullable=False)
    topes_por_gallo = Column(Integer, nullable=False)
    peleas_por_gallo = Column(Integer, nullable=False)
    vacunas_por_gallo = Column(Integer, nullable=False)
    
    # Características premium
    soporte_premium = Column(Boolean, default=False)
    respaldo_nube = Column(Boolean, default=False)
    estadisticas_avanzadas = Column(Boolean, default=False)
    videos_ilimitados = Column(Boolean, default=False)
    
    # Control y UI
    activo = Column(Boolean, default=True)
    orden = Column(Integer, default=0)  # Para ordenar en UI
    destacado = Column(Boolean, default=False)  # Plan recomendado
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlanCatalogo(codigo='{self.codigo}', nombre='{self.nombre}', precio={self.precio})>"
    
    @property
    def es_gratuito(self):
        """Verifica si es el plan gratuito"""
        return self.codigo == 'gratuito'
    
    @property
    def es_premium(self):
        """Verifica si es un plan de pago"""
        return self.precio > 0
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'precio': float(self.precio),
            'duracion_dias': self.duracion_dias,
            'limites': {
                'gallos_maximo': self.gallos_maximo,
                'topes_por_gallo': self.topes_por_gallo,
                'peleas_por_gallo': self.peleas_por_gallo,
                'vacunas_por_gallo': self.vacunas_por_gallo,
            },
            'caracteristicas': {
                'soporte_premium': self.soporte_premium,
                'respaldo_nube': self.respaldo_nube,
                'estadisticas_avanzadas': self.estadisticas_avanzadas,
                'videos_ilimitados': self.videos_ilimitados,
            },
            'destacado': self.destacado,
            'activo': self.activo,
        }