# 🐓 app/models/gallo_simple.py - Modelo de Gallo SIMPLE
from sqlalchemy import Column, Integer, String, Date, Numeric, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Gallo(Base):
    __tablename__ = "gallos"
    
    # Campos básicos
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    raza_id = Column(Integer, ForeignKey("razas.id"), nullable=True)
    
    # Información del gallo
    nombre = Column(String(255), nullable=False)
    codigo_identificacion = Column(String(50), nullable=False, index=True)
    fecha_nacimiento = Column(Date, nullable=True)
    peso = Column(Numeric(5, 2), nullable=True)  # kg
    altura = Column(Integer, nullable=True)  # cm
    color = Column(String(100), nullable=True)
    estado = Column(String(20), default="activo")  # activo, inactivo, padre, madre, campeon, retirado
    procedencia = Column(String(255), nullable=True)
    notas = Column(Text, nullable=True)
    
    # Genealogía
    padre_id = Column(Integer, ForeignKey("gallos.id"), nullable=True)
    madre_id = Column(Integer, ForeignKey("gallos.id"), nullable=True)
    
    # Fotos
    foto_principal_url = Column(Text, nullable=True)
    fotos_adicionales = Column(JSON, nullable=True)  # Array de URLs
    
    # Timestamps
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relaciones
    raza = relationship("Raza", foreign_keys=[raza_id])
    padre = relationship("Gallo", remote_side=[id], foreign_keys=[padre_id])
    madre = relationship("Gallo", remote_side=[id], foreign_keys=[madre_id])
