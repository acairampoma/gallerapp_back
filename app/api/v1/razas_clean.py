# 🧬 app/api/v1/razas_clean.py - ENDPOINTS DE RAZAS LIMPIOS
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.raza import Raza
from app.models.gallo import Gallo

router = APIRouter()

# ========================================
# 🧬 GESTIÓN DE RAZAS (2 ENDPOINTS)
# ========================================

@router.get("", response_model=dict)
async def list_razas(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Listar todas las razas disponibles"""
    
    try:
        # Obtener todas las razas
        razas = db.query(Raza).order_by(Raza.nombre).all()
        
        razas_data = []
        for raza in razas:
            # Contar gallos del usuario con esta raza
            gallos_count = db.query(Gallo).filter(
                Gallo.raza_id == raza.id,
                Gallo.user_id == current_user_id
            ).count()
            
            razas_data.append({
                "id": raza.id,
                "nombre": raza.nombre,
                "origen": raza.origen,
                "descripcion": raza.descripcion,
                "caracteristicas": raza.caracteristicas,
                "gallos_count": gallos_count,
                "created_at": raza.created_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "razas": razas_data,
                "total": len(razas_data)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo razas: {str(e)}"
        )

@router.get("/{raza_id}", response_model=dict)
async def get_raza(
    raza_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🔍 Obtener raza específica con estadísticas"""
    
    try:
        # Obtener raza
        raza = db.query(Raza).filter(Raza.id == raza_id).first()
        
        if not raza:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Raza no encontrada"
            )
        
        # Obtener gallos del usuario con esta raza
        gallos_usuario = db.query(Gallo).filter(
            Gallo.raza_id == raza_id,
            Gallo.user_id == current_user_id
        ).all()
        
        # Estadísticas básicas
        gallos_data = []
        for gallo in gallos_usuario:
            gallos_data.append({
                "id": gallo.id,
                "nombre": gallo.nombre,
                "codigo_identificacion": gallo.codigo_identificacion,
                "estado": gallo.estado,
                "foto_principal_url": gallo.foto_principal_url
            })
        
        return {
            "success": True,
            "data": {
                "raza": {
                    "id": raza.id,
                    "nombre": raza.nombre,
                    "origen": raza.origen,
                    "descripcion": raza.descripcion,
                    "caracteristicas": raza.caracteristicas,
                    "created_at": raza.created_at.isoformat()
                },
                "gallos_usuario": gallos_data,
                "estadisticas": {
                    "total_gallos": len(gallos_data),
                    "gallos_activos": len([g for g in gallos_data if g["estado"] == "activo"]),
                    "gallos_con_foto": len([g for g in gallos_data if g["foto_principal_url"]])
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo raza: {str(e)}"
        )
