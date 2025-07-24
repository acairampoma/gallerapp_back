# 🧬 app/api/v1/razas_simple.py - ENDPOINTS DE RAZAS SIMPLES
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user_id

router = APIRouter()

@router.get("", response_model=dict)
async def list_razas_simple(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Listar razas - ENDPOINT SIMPLE"""
    
    razas_default = [
        {"id": 1, "nombre": "Kelso", "origen": "Estados Unidos"},
        {"id": 2, "nombre": "Hatch", "origen": "Estados Unidos"}, 
        {"id": 3, "nombre": "Sweater", "origen": "Estados Unidos"},
        {"id": 4, "nombre": "Asil", "origen": "India"},
        {"id": 5, "nombre": "Shamo", "origen": "Japón"}
    ]
    
    return {
        "success": True,
        "message": "Endpoint de razas funcionando",
        "data": {
            "razas": razas_default,
            "total": len(razas_default),
            "user_id": current_user_id
        }
    }

@router.get("/{raza_id}", response_model=dict)
async def get_raza_simple(
    raza_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🔍 Obtener raza - ENDPOINT SIMPLE"""
    
    return {
        "success": True,
        "message": f"Raza ID {raza_id} - endpoint funcionando",
        "data": {
            "raza_id": raza_id,
            "user_id": current_user_id,
            "raza": {
                "id": raza_id,
                "nombre": "Raza de Ejemplo",
                "origen": "Origen de Ejemplo",
                "descripcion": "Descripción de ejemplo"
            },
            "status": "endpoint funcionando"
        }
    }
