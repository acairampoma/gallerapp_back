# 🥊 Schemas para Peleas - MEJORES PRÁCTICAS
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date
from enum import Enum

class ResultadoPeleaEnum(str, Enum):
    """Enum para resultados de peleas"""
    GANADA = "ganada"
    PERDIDA = "perdida" 
    EMPATE = "empate"

class PeleaBase(BaseModel):
    """Schema base para peleas con validaciones mejoradas"""
    gallo_id: int = Field(..., gt=0, description="ID del gallo (debe ser positivo)")
    titulo: str = Field(..., min_length=3, max_length=255, description="Título de la pelea")
    descripcion: Optional[str] = Field(None, max_length=1000, description="Descripción detallada")
    fecha_pelea: datetime = Field(..., description="Fecha y hora de la pelea")
    ubicacion: Optional[str] = Field(None, min_length=2, max_length=255, description="Lugar de la pelea")
    oponente_nombre: Optional[str] = Field(None, min_length=2, max_length=255, description="Nombre del oponente")
    oponente_gallo: Optional[str] = Field(None, min_length=2, max_length=255, description="Nombre del gallo oponente")
    resultado: Optional[ResultadoPeleaEnum] = Field(None, description="Resultado de la pelea")
    notas_resultado: Optional[str] = Field(None, max_length=2000, description="Notas del resultado")
    
    # 🆕 NUEVOS CAMPOS AGREGADOS
    gallera: Optional[str] = Field(None, max_length=255, description="Nombre de la gallera")
    ciudad: Optional[str] = Field(None, max_length=255, description="Ciudad de la gallera")
    mi_gallo_nombre: Optional[str] = Field(None, max_length=255, description="Nombre de mi gallo")
    mi_gallo_propietario: Optional[str] = Field(None, max_length=255, description="Propietario de mi gallo")
    mi_gallo_peso: Optional[int] = Field(None, gt=0, le=5000, description="Peso de mi gallo en gramos")
    oponente_gallo_peso: Optional[int] = Field(None, gt=0, le=5000, description="Peso del gallo oponente en gramos")
    premio: Optional[str] = Field(None, max_length=100, description="Premio del combate")
    duracion_minutos: Optional[int] = Field(None, gt=0, le=480, description="Duración en minutos")

    @validator('fecha_pelea')
    def validar_fecha_pelea(cls, v):
        """La fecha no puede ser muy futura (máximo 1 año)"""
        if v > datetime.now().replace(year=datetime.now().year + 1):
            raise ValueError('La fecha de pelea no puede ser más de 1 año en el futuro')
        return v
    
    @validator('titulo')
    def validar_titulo(cls, v):
        """Título no puede ser solo espacios"""
        if not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip()

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
    
    # 🆕 NUEVOS CAMPOS AGREGADOS
    gallera: Optional[str] = Field(None, max_length=255)
    ciudad: Optional[str] = Field(None, max_length=255)
    mi_gallo_nombre: Optional[str] = Field(None, max_length=255)
    mi_gallo_propietario: Optional[str] = Field(None, max_length=255)
    mi_gallo_peso: Optional[int] = Field(None, gt=0, le=5000)
    oponente_gallo_peso: Optional[int] = Field(None, gt=0, le=5000)
    premio: Optional[str] = Field(None, max_length=100)
    duracion_minutos: Optional[int] = Field(None, gt=0, le=480)

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