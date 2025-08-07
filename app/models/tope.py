# 🏋️ Modelo de Topes (Entrenamientos)
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class TipoEntrenamiento(enum.Enum):
    """Enum para tipos de entrenamiento"""
    SPARRING = "sparring"
    TECNICA = "tecnica"
    RESISTENCIA = "resistencia"
    VELOCIDAD = "velocidad"

class Tope(Base):
    """Modelo para registro de topes/entrenamientos de gallos"""
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
    tipo_entrenamiento = Column(Enum(TipoEntrenamiento), nullable=True)
    
    # Video y observaciones
    video_url = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", backref="topes")
    gallo = relationship("Gallo", backref="topes")