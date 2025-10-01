# 🥊 Schemas para Peleas de Evento
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import time, datetime


class PeleaEventoBase(BaseModel):
    """Schema base para PeleaEvento"""
    numero_pelea: int = Field(..., description="Número y orden de la pelea", ge=1)
    titulo_pelea: str = Field(..., max_length=255, description="Título de la pelea")
    descripcion_pelea: Optional[str] = Field(None, description="Descripción opcional")

    # Gallo Izquierda
    galpon_izquierda: str = Field(..., max_length=100, description="Galpón del gallo izquierdo")
    gallo_izquierda_nombre: str = Field(..., max_length=100, description="Nombre del gallo izquierdo")

    # Gallo Derecha
    galpon_derecha: str = Field(..., max_length=100, description="Galpón del gallo derecho")
    gallo_derecha_nombre: str = Field(..., max_length=100, description="Nombre del gallo derecho")

    # Tiempos opcionales
    hora_inicio_estimada: Optional[time] = Field(None, description="Hora estimada de inicio")

    class Config:
        from_attributes = True


class PeleaEventoCreate(PeleaEventoBase):
    """Schema para crear una pelea de evento"""
    evento_id: int = Field(..., description="ID del evento al que pertenece")

    @validator('numero_pelea')
    def validate_numero_pelea(cls, v):
        if v < 1:
            raise ValueError('El número de pelea debe ser mayor a 0')
        return v


class PeleaEventoUpdate(BaseModel):
    """Schema para actualizar una pelea de evento"""
    numero_pelea: Optional[int] = Field(None, ge=1)
    titulo_pelea: Optional[str] = Field(None, max_length=255)
    descripcion_pelea: Optional[str] = None

    galpon_izquierda: Optional[str] = Field(None, max_length=100)
    gallo_izquierda_nombre: Optional[str] = Field(None, max_length=100)

    galpon_derecha: Optional[str] = Field(None, max_length=100)
    gallo_derecha_nombre: Optional[str] = Field(None, max_length=100)

    hora_inicio_estimada: Optional[time] = None
    hora_inicio_real: Optional[datetime] = None
    hora_fin_real: Optional[datetime] = None
    duracion_minutos: Optional[int] = Field(None, ge=0)

    resultado: Optional[str] = Field(None, description="izquierda, derecha, empate")
    video_url: Optional[str] = None
    thumbnail_pelea_url: Optional[str] = None
    estado_video: Optional[str] = Field(None, description="sin_video, procesando, disponible")

    class Config:
        from_attributes = True

    @validator('resultado')
    def validate_resultado(cls, v):
        if v and v not in ['izquierda', 'derecha', 'empate']:
            raise ValueError('Resultado debe ser: izquierda, derecha, o empate')
        return v

    @validator('estado_video')
    def validate_estado_video(cls, v):
        if v and v not in ['sin_video', 'procesando', 'disponible']:
            raise ValueError('Estado video debe ser: sin_video, procesando, o disponible')
        return v


class PeleaEventoResponse(PeleaEventoBase):
    """Schema de respuesta para una pelea de evento"""
    id: int
    evento_id: int

    hora_inicio_real: Optional[datetime] = None
    hora_fin_real: Optional[datetime] = None
    duracion_minutos: Optional[int] = None

    resultado: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_pelea_url: Optional[str] = None
    estado_video: str = "sin_video"

    admin_editor_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PeleaEventoOrdenUpdate(BaseModel):
    """Schema para actualizar solo el orden de una pelea"""
    numero_pelea: int = Field(..., description="Nuevo número de orden", ge=1)

    class Config:
        from_attributes = True
