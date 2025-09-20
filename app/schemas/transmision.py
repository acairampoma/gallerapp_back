from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# ========================================
# SCHEMAS DE COLISEO
# ========================================

class ColiseoBase(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    ciudad: str
    departamento: Optional[str] = None
    aforo_maximo: Optional[int] = None
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    tipo_coliseo: str = "local"  # local, grande, especial
    activo: bool = True

class ColiseoCreate(ColiseoBase):
    pass

class ColiseoUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    departamento: Optional[str] = None
    aforo_maximo: Optional[int] = None
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    tipo_coliseo: Optional[str] = None
    activo: Optional[bool] = None

class ColiseoResponse(ColiseoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ========================================
# SCHEMAS DE EVENTO TRANSMISION
# ========================================

class EventoTransmisionBase(BaseModel):
    coliseo_id: int
    titulo: str
    descripcion: Optional[str] = None
    fecha_evento: datetime
    fecha_fin_evento: Optional[datetime] = None
    url_transmision: str
    estado: str = "programado"  # programado, en_vivo, finalizado, cancelado
    tipo_evento: str = "local"  # local, grande, especial
    precio_entrada: Optional[Decimal] = None
    es_premium: bool = False
    thumbnail_url: Optional[str] = None

    @validator('estado')
    def validate_estado(cls, v):
        estados_validos = ['programado', 'en_vivo', 'finalizado', 'cancelado']
        if v not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {estados_validos}')
        return v

    @validator('tipo_evento')
    def validate_tipo_evento(cls, v):
        tipos_validos = ['local', 'grande', 'especial']
        if v not in tipos_validos:
            raise ValueError(f'Tipo evento debe ser uno de: {tipos_validos}')
        return v

class EventoTransmisionCreate(EventoTransmisionBase):
    pass

class EventoTransmisionUpdate(BaseModel):
    coliseo_id: Optional[int] = None
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_evento: Optional[datetime] = None
    fecha_fin_evento: Optional[datetime] = None
    url_transmision: Optional[str] = None
    estado: Optional[str] = None
    tipo_evento: Optional[str] = None
    precio_entrada: Optional[Decimal] = None
    es_premium: Optional[bool] = None
    thumbnail_url: Optional[str] = None

    @validator('estado')
    def validate_estado(cls, v):
        if v is not None:
            estados_validos = ['programado', 'en_vivo', 'finalizado', 'cancelado']
            if v not in estados_validos:
                raise ValueError(f'Estado debe ser uno de: {estados_validos}')
        return v

class EventoTransmisionResponse(EventoTransmisionBase):
    id: int
    admin_creador_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    # Información del coliseo incluida
    coliseo: Optional[ColiseoResponse] = None

    class Config:
        from_attributes = True

# ========================================
# SCHEMAS PARA FILTROS Y BUSQUEDAS
# ========================================

class EventoFiltros(BaseModel):
    coliseo_id: Optional[int] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    estado: Optional[str] = None
    tipo_evento: Optional[str] = None
    es_premium: Optional[bool] = None
    solo_hoy: Optional[bool] = False

class EventosResponse(BaseModel):
    eventos: List[EventoTransmisionResponse]
    total: int
    pagina: int
    por_pagina: int
    total_paginas: int

# ========================================
# SCHEMAS DE ESTADISTICAS
# ========================================

class EstadisticasTransmision(BaseModel):
    total_eventos: int
    eventos_hoy: int
    eventos_en_vivo: int
    eventos_programados: int
    total_coliseos: int
    coliseos_activos: int