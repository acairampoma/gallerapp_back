# 🧬 app/models/raza_simple.py - Modelo de Raza SIMPLE
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Raza(Base):
    __tablename__ = "razas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    origen = Column(String(255), nullable=True)
    descripcion = Column(Text, nullable=True)
    caracteristicas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
