# 🏋️ Schemas para Topes
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from enum import Enum

class TipoEntrenamientoEnum(str, Enum):
    """Enum para tipos de entrenamiento"""
    SPARRING = "sparring"
    TECNICA = "tecnica"
    RESISTENCIA = "resistencia"
    VELOCIDAD = "velocidad"

class TopeBase(BaseModel):
    """Schema base para topes"""
    gallo_id: int
    titulo: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    fecha_tope: datetime
    ubicacion: Optional[str] = Field(None, max_length=255)
    duracion_minutos: Optional[int] = Field(None, ge=1, le=300)
    tipo_entrenamiento: Optional[TipoEntrenamientoEnum] = None
    observaciones: Optional[str] = None

class TopeCreate(TopeBase):
    """Schema para crear tope"""
    pass

class TopeUpdate(BaseModel):
    """Schema para actualizar tope"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    descripcion: Optional[str] = None
    fecha_tope: Optional[datetime] = None
    ubicacion: Optional[str] = Field(None, max_length=255)
    duracion_minutos: Optional[int] = Field(None, ge=1, le=300)
    tipo_entrenamiento: Optional[TipoEntrenamientoEnum] = None
    observaciones: Optional[str] = None

class TopeResponse(TopeBase):
    """Schema para respuesta de tope"""
    id: int
    user_id: Optional[int]
    video_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class TopeStats(BaseModel):
    """Schema para estadísticas de topes"""
    total_topes: int
    topes_este_mes: int
    promedio_duracion: float
    tipos_entrenamiento: Dict[str, int]
    ultimo_tope: Optional[datetime]