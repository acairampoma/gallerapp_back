# 🏋️ Modelo de Topes - CORREGIDO para BD existente
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class TipoEntrenamiento(enum.Enum):
    """Enum para tipos de entrenamiento (solo para validación)"""
    SPARRING = "sparring"
    TECNICA = "tecnica"
    RESISTENCIA = "resistencia"
    VELOCIDAD = "velocidad"

class Tope(Base):
    """Modelo para registro de topes/entrenamientos - COINCIDE CON BD POSTGRESQL"""
    __tablename__ = "topes"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    gallo_id = Column(Integer, ForeignKey("gallos.id"), nullable=True)
    
    # Información del tope
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_tope = Column(DateTime, nullable=False)
    ubicacion = Column(String(255), nullable=True)
    
    # Detalles del entrenamiento
    duracion_minutos = Column(Integer, nullable=True)
    tipo_entrenamiento = Column(String(100), nullable=True)  # ← CAMBIADO: String en lugar de Enum
    
    # Video y observaciones
    video_url = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    
    # Timestamps - EXACTOS como en BD
    created_at = Column(DateTime, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(DateTime, server_default="CURRENT_TIMESTAMP", onupdate=datetime.utcnow)
    
    # Relaciones (opcionales por si las necesitamos)
    # user = relationship("User", backref="topes")
    # gallo = relationship("Gallo", backref="topes")