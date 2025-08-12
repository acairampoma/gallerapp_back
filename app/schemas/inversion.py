# 📋 Schemas de Inversiones
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional

class InversionBase(BaseModel):
    año: int = Field(..., ge=2020, le=2100)
    mes: int = Field(..., ge=1, le=12)
    tipo_gasto: str = Field(..., pattern="^(alimento|medicina|limpieza_galpon|entrenador)$")
    costo: Decimal = Field(..., ge=0)

class InversionCreate(InversionBase):
    pass

class InversionUpdate(BaseModel):
    costo: Decimal = Field(..., ge=0)

class InversionResponse(InversionBase):
    id: int
    user_id: int
    fecha_registro: datetime
    
    class Config:
        from_attributes = True

class InversionesMensuales(BaseModel):
    año: int
    mes: int
    alimento: Decimal
    medicina: Decimal
    limpieza_galpon: Decimal
    entrenador: Decimal
    total: Decimal

class ReporteAnual(BaseModel):
    año: int
    meses: list
    total_anual: float

class ResumenInversiones(BaseModel):
    total_historico: float
    promedio_mensual: float
    por_tipo: dict
    ultimo_mes: str