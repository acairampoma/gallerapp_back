# 🔥 app/schemas/gallo.py - Schemas ÉPICOS para Técnica Recursiva Genealógica
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from decimal import Decimal

# ========================
# 🎯 SCHEMAS BASE
# ========================

class RazaBase(BaseModel):
    """📋 Schema base para razas"""
    id: int
    nombre: str
    descripcion: Optional[str] = None
    origen: Optional[str] = None
    
    class Config:
        from_attributes = True

class PhotoData(BaseModel):
    """📸 Schema para datos de foto"""
    url: str
    public_id: Optional[str] = None
    photo_type: str = Field(..., description="principal, adicional, thumbnail")
    width: Optional[int] = None
    height: Optional[int] = None
    size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None

class PhotoUrls(BaseModel):
    """📸 Schema para URLs de fotos con transformaciones"""
    original: str
    thumbnail: Optional[str] = None
    medium: Optional[str] = None
    large: Optional[str] = None
    optimized: Optional[str] = None

# ========================
# 🐓 SCHEMAS DE GALLO
# ========================

class GalloBase(BaseModel):
    """🐓 Schema base de gallo"""
    nombre: str = Field(..., min_length=2, max_length=255)
    codigo_identificacion: str = Field(..., min_length=3, max_length=20)
    raza_id: Optional[int] = None
    fecha_nacimiento: Optional[date] = None
    peso: Optional[Decimal] = Field(None, ge=0.5, le=10.0)
    altura: Optional[int] = Field(None, ge=20, le=100)
    color: Optional[str] = Field(None, max_length=100)
    estado: str = Field(default="activo", max_length=20)
    procedencia: Optional[str] = Field(None, max_length=255)
    notas: Optional[str] = None
    
    # Campos adicionales detallados
    color_plumaje: Optional[str] = Field(None, max_length=100)
    color_placa: Optional[str] = Field(None, max_length=50)
    ubicacion_placa: Optional[str] = Field(None, max_length=50)
    color_patas: Optional[str] = Field(None, max_length=50)
    criador: Optional[str] = Field(None, max_length=255)
    propietario_actual: Optional[str] = Field(None, max_length=255)
    observaciones: Optional[str] = None
    numero_registro: Optional[str] = Field(None, max_length=100)
    
    @validator('codigo_identificacion')
    def validate_codigo(cls, v):
        if v:
            return v.strip().upper()
        return v
    
    @validator('estado')
    def validate_estado(cls, v):
        estados_validos = ['activo', 'inactivo', 'padre', 'madre', 'campeon', 'retirado', 'vendido']
        if v and v.lower() not in estados_validos:
            raise ValueError(f"Estado debe ser uno de: {', '.join(estados_validos)}")
        return v.lower() if v else "activo"

class GalloCreate(GalloBase):
    """🔥 Schema para crear gallo con técnica recursiva genealógica"""
    
    # Control de padres
    crear_padre: bool = Field(default=False, description="Crear padre automáticamente")
    crear_madre: bool = Field(default=False, description="Crear madre automáticamente")
    padre_id: Optional[int] = Field(None, description="ID de padre existente")
    madre_id: Optional[int] = Field(None, description="ID de madre existente")
    
    # Datos del padre (si crear_padre=True)
    padre_nombre: Optional[str] = Field(None, min_length=2, max_length=255)
    padre_codigo: Optional[str] = Field(None, min_length=3, max_length=20)
    padre_raza_id: Optional[int] = None
    padre_color: Optional[str] = Field(None, max_length=100)
    padre_peso: Optional[Decimal] = Field(None, ge=0.5, le=10.0)
    padre_procedencia: Optional[str] = Field(None, max_length=255)
    padre_notas: Optional[str] = None
    padre_color_plumaje: Optional[str] = Field(None, max_length=100)
    padre_color_patas: Optional[str] = Field(None, max_length=50)
    padre_criador: Optional[str] = Field(None, max_length=255)
    
    # Datos de la madre (si crear_madre=True)
    madre_nombre: Optional[str] = Field(None, min_length=2, max_length=255)
    madre_codigo: Optional[str] = Field(None, min_length=3, max_length=20)
    madre_raza_id: Optional[int] = None
    madre_color: Optional[str] = Field(None, max_length=100)
    madre_peso: Optional[Decimal] = Field(None, ge=0.5, le=10.0)
    madre_procedencia: Optional[str] = Field(None, max_length=255)
    madre_notas: Optional[str] = None
    madre_color_plumaje: Optional[str] = Field(None, max_length=100)
    madre_color_patas: Optional[str] = Field(None, max_length=50)
    madre_criador: Optional[str] = Field(None, max_length=255)
    
    @validator('padre_codigo')
    def validate_padre_codigo(cls, v, values):
        if values.get('crear_padre') and not v:
            raise ValueError("Código del padre es obligatorio si crear_padre=True")
        if v:
            return v.strip().upper()
        return v
    
    @validator('madre_codigo')
    def validate_madre_codigo(cls, v, values):
        if values.get('crear_madre') and not v:
            raise ValueError("Código de la madre es obligatorio si crear_madre=True")
        if v:
            return v.strip().upper()
        return v
    
    @validator('padre_nombre')
    def validate_padre_nombre(cls, v, values):
        if values.get('crear_padre') and not v:
            raise ValueError("Nombre del padre es obligatorio si crear_padre=True")
        return v
    
    @validator('madre_nombre')
    def validate_madre_nombre(cls, v, values):
        if values.get('crear_madre') and not v:
            raise ValueError("Nombre de la madre es obligatorio si crear_madre=True")
        return v

class GalloUpdate(BaseModel):
    """✏️ Schema para actualizar gallo"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=255)
    peso: Optional[Decimal] = Field(None, ge=0.5, le=10.0)
    altura: Optional[int] = Field(None, ge=20, le=100)
    color: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=20)
    procedencia: Optional[str] = Field(None, max_length=255)
    notas: Optional[str] = None
    
    # Campos adicionales actualizables
    color_plumaje: Optional[str] = Field(None, max_length=100)
    color_placa: Optional[str] = Field(None, max_length=50)
    ubicacion_placa: Optional[str] = Field(None, max_length=50)
    color_patas: Optional[str] = Field(None, max_length=50)
    criador: Optional[str] = Field(None, max_length=255)
    propietario_actual: Optional[str] = Field(None, max_length=255)
    observaciones: Optional[str] = None
    numero_registro: Optional[str] = Field(None, max_length=100)
    
    # Control de genealogía
    actualizar_padre: bool = Field(default=False)
    padre_id: Optional[int] = None
    crear_padre: bool = Field(default=False)
    padre_nombre: Optional[str] = Field(None, min_length=2, max_length=255)
    padre_codigo: Optional[str] = Field(None, min_length=3, max_length=20)
    
    actualizar_madre: bool = Field(default=False)
    madre_id: Optional[int] = None
    crear_madre: bool = Field(default=False)
    madre_nombre: Optional[str] = Field(None, min_length=2, max_length=255)
    madre_codigo: Optional[str] = Field(None, min_length=3, max_length=20)

class GalloSimple(BaseModel):
    """📋 Schema simple de gallo para listas"""
    id: int
    nombre: str
    codigo_identificacion: str
    raza: Optional[RazaBase] = None
    peso: Optional[Decimal] = None
    color: Optional[str] = None
    estado: str
    foto_principal_url: Optional[str] = None
    url_foto_cloudinary: Optional[str] = None
    tipo_registro: str
    id_gallo_genealogico: Optional[int] = None
    padre_id: Optional[int] = None
    madre_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class GalloDetallado(GalloSimple):
    """📋 Schema detallado de gallo"""
    altura: Optional[int] = None
    fecha_nacimiento: Optional[date] = None
    procedencia: Optional[str] = None
    notas: Optional[str] = None
    
    # Campos adicionales detallados
    color_plumaje: Optional[str] = None
    color_placa: Optional[str] = None
    ubicacion_placa: Optional[str] = None
    color_patas: Optional[str] = None
    criador: Optional[str] = None
    propietario_actual: Optional[str] = None
    observaciones: Optional[str] = None
    numero_registro: Optional[str] = None
    
    # Fotos
    fotos_adicionales: Optional[List[str]] = []
    photos_data: Optional[List[PhotoData]] = []
    photo_urls: Optional[PhotoUrls] = None
    
    updated_at: datetime

# ========================
# 🧬 SCHEMAS GENEALÓGICOS
# ========================

class GenealogiaSummary(BaseModel):
    """📊 Resumen genealógico"""
    generaciones_disponibles: int = 0
    ancestros_totales: int = 0
    descendientes_totales: int = 0
    lineas_completas: int = 0
    tiene_padre: bool = False
    tiene_madre: bool = False
    genealogy_id: Optional[int] = None

class AncestroData(BaseModel):
    """🌳 Datos de ancestro en árbol genealógico"""
    gallo: GalloSimple
    relacion: str = Field(..., description="padre, madre, abuelo_paterno, etc.")
    nivel: int = Field(..., description="Nivel en el árbol (1=padres, 2=abuelos, etc.)")

class DescendienteData(BaseModel):
    """👶 Datos de descendiente"""
    gallo: GalloSimple
    relacion: str = Field(..., description="hijo_como_padre, hijo_como_madre")
    madre_o_padre: Optional[GalloSimple] = None

class ArbolGenealogico(BaseModel):
    """🌳 Árbol genealógico completo"""
    gallo_base: GalloSimple
    ancestros: List[AncestroData] = []
    descendientes: List[DescendienteData] = []
    familia_completa: List[GalloSimple] = []
    estadisticas: GenealogiaSummary

# ========================
# 🔥 SCHEMAS DE RESPUESTA ÉPICOS
# ========================

class GenealogyCreateResponse(BaseModel):
    """🔥 Respuesta épica de creación con genealogía"""
    success: bool = True
    message: str
    data: Dict[str, Any] = Field(..., description="Datos de la respuesta")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Gallo registrado exitosamente con genealogía",
                "data": {
                    "gallo_principal": {
                        "id": 15,
                        "nombre": "El Campeón",
                        "codigo_identificacion": "CAM001",
                        "padre_id": 16,
                        "madre_id": 17
                    },
                    "padre_creado": {
                        "id": 16,
                        "nombre": "Tornado",
                        "codigo_identificacion": "TOR001"
                    },
                    "madre_creada": {
                        "id": 17,
                        "nombre": "Reina",
                        "codigo_identificacion": "REI001"
                    },
                    "total_registros_creados": 3,
                    "genealogy_summary": {
                        "generaciones_disponibles": 1,
                        "ancestros_totales": 2,
                        "lineas_completas": 1
                    }
                }
            }
        }

class GallosListResponse(BaseModel):
    """📋 Respuesta de lista de gallos"""
    success: bool = True
    data: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "gallos": [],
                    "pagination": {
                        "current_page": 1,
                        "per_page": 20,
                        "total_pages": 3,
                        "total_count": 45
                    },
                    "stats": {
                        "total_gallos": 45,
                        "gallos_con_foto": 32,
                        "gallos_con_padres": 28
                    }
                }
            }
        }

class GalloDetailResponse(BaseModel):
    """📋 Respuesta detallada de gallo"""
    success: bool = True
    data: Dict[str, Any]

class PhotoUploadResponse(BaseModel):
    """📸 Respuesta de subida de foto"""
    success: bool = True
    message: str
    data: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Foto subida exitosamente",
                "data": {
                    "foto_url": "https://res.cloudinary.com/.../CAM001_principal.jpg",
                    "cloudinary_public_id": "gallos/CAM001_principal",
                    "metadata": {
                        "width": 1024,
                        "height": 768,
                        "format": "jpg",
                        "size_bytes": 245760
                    }
                }
            }
        }

class GenealogySearchResponse(BaseModel):
    """🔍 Respuesta de búsqueda genealógica"""
    success: bool = True
    data: Dict[str, Any]

class ErrorResponse(BaseModel):
    """❌ Respuesta de error"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None

# ========================
# 🔍 SCHEMAS DE BÚSQUEDA Y FILTROS
# ========================

class GalloSearchParams(BaseModel):
    """🔍 Parámetros de búsqueda de gallos"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    search: Optional[str] = Field(None, min_length=2)
    raza_id: Optional[int] = None
    estado: Optional[str] = None
    tiene_foto: Optional[bool] = None
    tiene_padres: Optional[bool] = None
    created_after: Optional[date] = None
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$")
    include_genealogy: bool = Field(default=False)

class GenealogySearchParams(BaseModel):
    """🧬 Parámetros de búsqueda genealógica"""
    genealogy_id: Optional[int] = None
    ancestro_id: Optional[int] = None
    descendiente_id: Optional[int] = None
    max_depth: int = Field(default=5, ge=1, le=10)
    include_descendants: bool = Field(default=False)

# ========================
# 📊 SCHEMAS DE ESTADÍSTICAS
# ========================

class GenealogyStats(BaseModel):
    """📊 Estadísticas genealógicas"""
    estadisticas_generales: Dict[str, int]
    distribucion_tipos: Dict[str, int]
    familias_genealogicas: Dict[str, Union[int, float]]
    user_id: Optional[int] = None

class DashboardStats(BaseModel):
    """📈 Estadísticas del dashboard"""
    resumen_general: Dict[str, int]
    distribucion_por_raza: List[Dict[str, Union[str, int, float]]]
    estadisticas_genealogicas: Dict[str, Union[int, float]]
    actividad_reciente: List[Dict[str, Any]]
    fotos_estadisticas: Dict[str, Union[int, float]]

# ========================
# 🎯 SCHEMAS DE VALIDACIÓN
# ========================

class ValidationRules(BaseModel):
    """✅ Reglas de validación del sistema"""
    codigo_identificacion: Dict[str, Any]
    nombre: Dict[str, Any]
    peso: Dict[str, Any]
    altura: Dict[str, Any]
    estado: Dict[str, Any]
    tipo_registro: Dict[str, Any]
    fecha_nacimiento: Dict[str, Any]
    foto: Dict[str, Any]

class CodeValidationResponse(BaseModel):
    """✅ Respuesta de validación de código"""
    codigo: str
    disponible: bool
    conflicto_con: Optional[Dict[str, Any]] = None
    sugerencias: List[str] = []

# ========================
# 🔧 SCHEMAS DE UTILIDADES
# ========================

class SuccessResponse(BaseModel):
    """✅ Respuesta genérica de éxito"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None

class PaginationInfo(BaseModel):
    """📄 Información de paginación"""
    current_page: int
    per_page: int
    total_pages: int
    total_count: int
    has_next: bool = False
    has_prev: bool = False

class FilterInfo(BaseModel):
    """🔍 Información de filtros aplicados"""
    search: Optional[str] = None
    raza_id: Optional[int] = None
    estado: Optional[str] = None
    include_genealogy: bool = False
    total_filters_applied: int = 0
