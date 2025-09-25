# 🛒 Schemas de Marketplace - Validación y Serialización
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# ================================
# SCHEMAS DE PUBLICACIÓN
# ================================

class MarketplacePublicacionBase(BaseModel):
    """Schema base para publicaciones de marketplace"""
    precio: Decimal = Field(..., gt=0, description="Precio debe ser mayor a 0")
    estado: str = Field(default="venta", description="Estado de la publicación")
    icono_ejemplo: Optional[str] = Field(default="🐓", max_length=100, description="Ícono visual")

    @validator('estado')
    def validate_estado(cls, v):
        estados_validos = ['venta', 'vendido', 'pausado']
        if v not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {estados_validos}')
        return v

    @validator('precio')
    def validate_precio(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        if v > 999999.99:
            raise ValueError('El precio no puede exceder 999,999.99')
        return v


class MarketplacePublicacionCreate(MarketplacePublicacionBase):
    """Schema para crear nueva publicación"""
    gallo_id: int = Field(..., gt=0, description="ID del gallo a publicar")

    class Config:
        schema_extra = {
            "example": {
                "gallo_id": 123,
                "precio": 250.50,
                "estado": "venta",
                "icono_ejemplo": "🐓"
            }
        }


class MarketplacePublicacionUpdate(BaseModel):
    """Schema para actualizar publicación existente"""
    precio: Optional[Decimal] = Field(None, gt=0, description="Nuevo precio")
    estado: Optional[str] = Field(None, description="Nuevo estado")
    icono_ejemplo: Optional[str] = Field(None, max_length=100, description="Nuevo ícono")

    @validator('estado')
    def validate_estado(cls, v):
        if v is not None:
            estados_validos = ['venta', 'vendido', 'pausado']
            if v not in estados_validos:
                raise ValueError(f'Estado debe ser uno de: {estados_validos}')
        return v

    @validator('precio')
    def validate_precio(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('El precio debe ser mayor a 0')
            if v > 999999.99:
                raise ValueError('El precio no puede exceder 999,999.99')
        return v

    class Config:
        schema_extra = {
            "example": {
                "precio": 300.00,
                "estado": "pausado"
            }
        }


class MarketplacePublicacionResponse(MarketplacePublicacionBase):
    """Schema para respuesta de publicación con datos completos"""
    id: int
    user_id: int
    gallo_id: int
    fecha_publicacion: datetime
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int

    # Datos del gallo (se agregarán en el endpoint)
    gallo_info: Optional[Dict[str, Any]] = None

    # Datos del vendedor (se agregarán en el endpoint)
    vendedor_info: Optional[Dict[str, Any]] = None

    # Contadores (se agregarán en el endpoint si están disponibles)
    es_favorito: Optional[bool] = False
    total_favoritos: Optional[int] = 0

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123,
                "gallo_id": 456,
                "precio": 250.50,
                "estado": "venta",
                "icono_ejemplo": "🐓",
                "fecha_publicacion": "2024-01-15T10:30:00Z",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "created_by": 123,
                "updated_by": 123,
                "gallo_info": {
                    "nombre": "Campeón Rojo",
                    "codigo_identificacion": "CR-001",
                    "foto_principal_url": "https://example.com/foto.jpg"
                },
                "vendedor_info": {
                    "nombre": "Juan Pérez",
                    "telefono": "+51987654321"
                },
                "es_favorito": False,
                "total_favoritos": 3
            }
        }


# ================================
# SCHEMAS DE FAVORITOS
# ================================

class MarketplaceFavoritoCreate(BaseModel):
    """Schema para crear favorito"""
    publicacion_id: int = Field(..., gt=0, description="ID de la publicación a marcar como favorita")

    class Config:
        schema_extra = {
            "example": {
                "publicacion_id": 123
            }
        }


class MarketplaceFavoritoResponse(BaseModel):
    """Schema para respuesta de favorito"""
    id: int
    user_id: int
    publicacion_id: int
    created_at: datetime

    # Información de la publicación (se agregará en el endpoint)
    publicacion_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123,
                "publicacion_id": 456,
                "created_at": "2024-01-15T10:30:00Z",
                "publicacion_info": {
                    "precio": 250.50,
                    "estado": "venta",
                    "gallo_nombre": "Campeón Rojo"
                }
            }
        }


# ================================
# SCHEMAS DE FILTROS Y BÚSQUEDA
# ================================

class MarketplaceFiltros(BaseModel):
    """Schema para filtros de búsqueda en marketplace"""
    precio_min: Optional[Decimal] = Field(None, ge=0, description="Precio mínimo")
    precio_max: Optional[Decimal] = Field(None, ge=0, description="Precio máximo")
    estado: Optional[str] = Field(None, description="Estado de publicación")
    user_id: Optional[int] = Field(None, description="ID del vendedor")
    buscar: Optional[str] = Field(None, max_length=100, description="Texto de búsqueda")

    # Paginación
    skip: int = Field(default=0, ge=0, description="Registros a saltar")
    limit: int = Field(default=20, ge=1, le=100, description="Límite de registros")

    @validator('precio_max')
    def validate_precio_max(cls, v, values):
        if v is not None and 'precio_min' in values and values['precio_min'] is not None:
            if v < values['precio_min']:
                raise ValueError('precio_max debe ser mayor o igual a precio_min')
        return v

    @validator('estado')
    def validate_estado(cls, v):
        if v is not None:
            estados_validos = ['venta', 'vendido', 'pausado']
            if v not in estados_validos:
                raise ValueError(f'Estado debe ser uno de: {estados_validos}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "precio_min": 100.00,
                "precio_max": 500.00,
                "estado": "venta",
                "buscar": "champion",
                "skip": 0,
                "limit": 20
            }
        }


# ================================
# SCHEMAS DE LÍMITES Y VALIDACIÓN
# ================================

class MarketplaceLimites(BaseModel):
    """Schema para información de límites del usuario"""
    publicaciones_permitidas: int = Field(..., description="Total de publicaciones permitidas por el plan")
    publicaciones_activas: int = Field(..., description="Publicaciones activas del usuario")
    publicaciones_disponibles: int = Field(..., description="Publicaciones que puede crear todavía")
    puede_publicar: bool = Field(..., description="Si puede crear nuevas publicaciones")
    plan_codigo: str = Field(..., description="Código del plan actual")
    plan_nombre: str = Field(..., description="Nombre del plan actual")

    class Config:
        schema_extra = {
            "example": {
                "publicaciones_permitidas": 5,
                "publicaciones_activas": 2,
                "publicaciones_disponibles": 3,
                "puede_publicar": True,
                "plan_codigo": "premium",
                "plan_nombre": "Plan Premium"
            }
        }


# ================================
# SCHEMAS DE RESPUESTA GENERAL
# ================================

class MarketplaceListResponse(BaseModel):
    """Schema para respuesta de lista paginada"""
    publicaciones: List[MarketplacePublicacionResponse]
    total: int = Field(..., description="Total de registros encontrados")
    skip: int = Field(..., description="Registros saltados")
    limit: int = Field(..., description="Límite aplicado")
    has_next: bool = Field(..., description="Si hay más páginas")

    class Config:
        schema_extra = {
            "example": {
                "publicaciones": [],
                "total": 25,
                "skip": 0,
                "limit": 20,
                "has_next": True
            }
        }


class MarketplaceStatsResponse(BaseModel):
    """Schema para estadísticas generales del marketplace"""
    total_publicaciones: int
    publicaciones_activas: int
    publicaciones_vendidas: int
    publicaciones_pausadas: int
    precio_promedio: Optional[Decimal]
    precio_minimo: Optional[Decimal]
    precio_maximo: Optional[Decimal]

    class Config:
        schema_extra = {
            "example": {
                "total_publicaciones": 150,
                "publicaciones_activas": 120,
                "publicaciones_vendidas": 25,
                "publicaciones_pausadas": 5,
                "precio_promedio": 275.50,
                "precio_minimo": 50.00,
                "precio_maximo": 1500.00
            }
        }