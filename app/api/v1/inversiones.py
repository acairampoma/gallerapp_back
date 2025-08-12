# 💰 API Endpoints para Inversiones
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.core.security import get_current_user_id
from app.schemas.inversion import (
    InversionCreate, 
    InversionUpdate, 
    InversionResponse,
    InversionesMensuales,
    ReporteAnual,
    ResumenInversiones
)
from app.services.inversion_service import InversionService

router = APIRouter(prefix="/inversiones", tags=["💰 Inversiones"])

@router.get("/", response_model=List[InversionResponse])
async def obtener_inversiones(
    año: Optional[int] = None,
    mes: Optional[int] = None,
    tipo_gasto: Optional[str] = None,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📊 Obtener inversiones del usuario con filtros opcionales"""
    inversiones = InversionService.obtener_inversiones(
        db, current_user_id, año, mes, tipo_gasto
    )
    return inversiones

@router.get("/mensual", response_model=InversionesMensuales)
async def obtener_inversiones_mensuales(
    año: int,
    mes: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📅 Obtener resumen de inversiones de un mes específico"""
    resumen = InversionService.obtener_resumen_mensual(db, current_user_id, año, mes)
    return InversionesMensuales(**resumen)

@router.post("/", response_model=InversionResponse)
async def crear_inversion(
    inversion: InversionCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """➕ Crear o actualizar inversión"""
    nueva_inversion = InversionService.crear_o_actualizar(
        db, current_user_id, inversion
    )
    return nueva_inversion

@router.put("/{año}/{mes}/{tipo_gasto}", response_model=InversionResponse)
async def actualizar_inversion(
    año: int,
    mes: int,
    tipo_gasto: str,
    inversion: InversionUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """✏️ Actualizar costo de inversión específica"""
    inversion_data = InversionCreate(
        año=año,
        mes=mes,
        tipo_gasto=tipo_gasto,
        costo=inversion.costo
    )
    actualizada = InversionService.crear_o_actualizar(
        db, current_user_id, inversion_data
    )
    return actualizada

@router.get("/reporte/anual/{año}", response_model=ReporteAnual)
async def reporte_anual(
    año: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📈 Reporte anual de inversiones"""
    reporte = InversionService.generar_reporte_anual(db, current_user_id, año)
    return ReporteAnual(**reporte)