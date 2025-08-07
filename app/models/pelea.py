# 🥊 Modelo de Peleas
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class ResultadoPelea(enum.Enum):
    """Enum para resultados de peleas"""
    GANADA = "ganada"
    PERDIDA = "perdida"
    EMPATE = "empate"

class Pelea(Base):
    """Modelo para registro de peleas de gallos"""
    __tablename__ = "peleas"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    gallo_id = Column(Integer, ForeignKey("gallos.id"), nullable=True)
    
    # Información de la pelea
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_pelea = Column(DateTime, nullable=False)
    ubicacion = Column(String(255), nullable=True)
    
    # Información del oponente
    oponente_nombre = Column(String(255), nullable=True)  # Nombre del dueño oponente
    oponente_gallo = Column(String(255), nullable=True)   # Nombre del gallo oponente
    
    # Resultado
    resultado = Column(Enum(ResultadoPelea), nullable=True)
    notas_resultado = Column(Text, nullable=True)
    
    # Video
    video_url = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", backref="peleas")
    gallo = relationship("Gallo", backref="peleas")