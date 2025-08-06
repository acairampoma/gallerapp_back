from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class VacunaBase(BaseModel):
    gallo_id: Optional[int] = None
    tipo_vacuna: str = Field(..., min_length=1, max_length=255)
    laboratorio: Optional[str] = Field(None, max_length=255)
    fecha_aplicacion: date
    proxima_dosis: Optional[date] = None
    veterinario_nombre: Optional[str] = Field(None, max_length=255)
    clinica: Optional[str] = Field(None, max_length=255)
    dosis: Optional[str] = Field(None, max_length=50)
    notas: Optional[str] = None

class VacunaCreate(VacunaBase):
    pass

class VacunaUpdate(BaseModel):
    gallo_id: Optional[int] = None
    tipo_vacuna: Optional[str] = Field(None, min_length=1, max_length=255)
    laboratorio: Optional[str] = Field(None, max_length=255)
    fecha_aplicacion: Optional[date] = None
    proxima_dosis: Optional[date] = None
    veterinario_nombre: Optional[str] = Field(None, max_length=255)
    clinica: Optional[str] = Field(None, max_length=255)
    dosis: Optional[str] = Field(None, max_length=50)
    notas: Optional[str] = None

class VacunaResponse(VacunaBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class VacunaWithGallo(VacunaResponse):
    gallo_nombre: Optional[str] = None
    gallo_codigo: Optional[str] = None
    
    class Config:
        orm_mode = True

class ProximaVacuna(BaseModel):
    gallo_id: int
    gallo_nombre: str
    tipo_vacuna: str
    proxima_dosis: date
    dias_restantes: int
    estado: str  # urgente, proximo, normal

class VacunaStats(BaseModel):
    total_vacunas: int
    vacunas_este_mes: int
    proximas_vacunas: int
    vacunas_vencidas: int

class VacunaRegistroRapido(BaseModel):
    gallo_ids: List[int] = Field(..., min_items=1)
    tipo_vacunas: List[str] = Field(..., min_items=1)
    fecha_aplicacion: date
    veterinario_nombre: Optional[str] = None
    clinica: Optional[str] = None
    dosis: Optional[str] = None
    proxima_dosis: Optional[date] = None
    notas: Optional[str] = None