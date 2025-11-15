# 🥊 Modelo de Peleas - CORREGIDO para BD existente
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class ResultadoPelea(enum.Enum):
    """Enum para resultados de peleas (solo para validación)"""
    GANADA = "ganada"
    PERDIDA = "perdida"
    EMPATE = "empate"

class Pelea(Base):
    """Modelo para registro de peleas de gallos - COINCIDE CON BD POSTGRESQL"""
    __tablename__ = "peleas"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Sin FK constraint por ahora
    gallo_id = Column(Integer, nullable=True)  # Sin FK constraint por ahora
    
    # Información de la pelea
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_pelea = Column(DateTime, nullable=False)
    ubicacion = Column(String(255), nullable=True)
    
    # Información del oponente
    oponente_nombre = Column(String(255), nullable=True)
    oponente_gallo = Column(String(255), nullable=True)
    
    # Resultado - VARCHAR en BD, no ENUM
    resultado = Column(String(20), nullable=True)  # ← CAMBIADO: String en lugar de Enum
    notas_resultado = Column(Text, nullable=True)
    
    # Video
    video_url = Column(Text, nullable=True)
    file_id = Column(String(255), nullable=True)  # ImageKit file_id para eliminar
    
    # 🆕 NUEVOS CAMPOS AGREGADOS
    gallera = Column(String(255), nullable=True)
    ciudad = Column(String(255), nullable=True)
    mi_gallo_nombre = Column(String(255), nullable=True)
    mi_gallo_propietario = Column(String(255), nullable=True)
    mi_gallo_peso = Column(Integer, nullable=True)  # gramos
    oponente_gallo_peso = Column(Integer, nullable=True)  # gramos
    premio = Column(String(100), nullable=True)
    duracion_minutos = Column(Integer, nullable=True)
    
    # Timestamps - EXACTOS como en BD
    created_at = Column(DateTime, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(DateTime, server_default="CURRENT_TIMESTAMP", onupdate=datetime.utcnow)
    
    # Relaciones (opcionales por si las necesitamos)
    # user = relationship("User", backref="peleas")
    # gallo = relationship("Gallo", backref="peleas")