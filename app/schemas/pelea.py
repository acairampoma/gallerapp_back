# 🥊 Schemas para Peleas
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class ResultadoPeleaEnum(str, Enum):
    """Enum para resultados de peleas"""
    GANADA = "ganada"
    PERDIDA = "perdida"
    EMPATE = "empate"

class PeleaBase(BaseModel):
    """Schema base para peleas"""
    gallo_id: int
    titulo: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    fecha_pelea: datetime
    ubicacion: Optional[str] = Field(None, max_length=255)
    oponente_nombre: Optional[str] = Field(None, max_length=255)
    oponente_gallo: Optional[str] = Field(None, max_length=255)
    resultado: Optional[ResultadoPeleaEnum] = None
    notas_resultado: Optional[str] = None

class PeleaCreate(PeleaBase):
    """Schema para crear pelea"""
    pass

class PeleaUpdate(BaseModel):
    """Schema para actualizar pelea"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    descripcion: Optional[str] = None
    fecha_pelea: Optional[datetime] = None
    ubicacion: Optional[str] = Field(None, max_length=255)
    oponente_nombre: Optional[str] = Field(None, max_length=255)
    oponente_gallo: Optional[str] = Field(None, max_length=255)
    resultado: Optional[ResultadoPeleaEnum] = None
    notas_resultado: Optional[str] = None

class PeleaResponse(PeleaBase):
    """Schema para respuesta de pelea"""
    id: int
    user_id: Optional[int]
    video_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class PeleaStats(BaseModel):
    """Schema para estadísticas de peleas"""
    total_peleas: int
    ganadas: int
    perdidas: int
    empates: int
    efectividad: float
    peleas_este_mes: int
    ultima_pelea: Optional[datetime]