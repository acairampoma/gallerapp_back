# 📷 app/api/v1/fotos_simple.py - ENDPOINTS DE FOTOS SIMPLES
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user_id

router = APIRouter()

@router.post("/{gallo_id}/foto", response_model=dict)
async def upload_foto_simple(
    gallo_id: int,
    foto: UploadFile = File(...),
    descripcion: str = Form("Foto del gallo"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📤 Subir foto del gallo - ENDPOINT SIMPLE"""
    
    # Validar que es una imagen
    if not foto.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen"
        )
    
    # Validar tamaño (max 5MB)
    if foto.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="La imagen es muy grande (máximo 5MB)"
        )
    
    return {
        "success": True,
        "message": f"Foto subida para gallo {gallo_id}",
        "data": {
            "gallo_id": gallo_id,
            "user_id": current_user_id,
            "archivo": {
                "filename": foto.filename,
                "content_type": foto.content_type,
                "size_mb": round(foto.size / (1024 * 1024), 2)
            },
            "descripcion": descripcion,
            "status": "endpoint funcionando - foto recibida correctamente",
            "nota": "Próximamente se subirá a Cloudinary"
        }
    }

@router.get("/{gallo_id}/fotos", response_model=dict)
async def list_fotos_simple(
    gallo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Listar fotos del gallo - ENDPOINT SIMPLE"""
    
    return {
        "success": True,
        "message": f"Fotos del gallo {gallo_id}",
        "data": {
            "gallo_id": gallo_id,
            "user_id": current_user_id,
            "fotos": [],
            "total_fotos": 0,
            "status": "endpoint funcionando - listo para implementar"
        }
    }

@router.delete("/{gallo_id}/fotos/{foto_id}", response_model=dict)
async def delete_foto_simple(
    gallo_id: int,
    foto_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🗑️ Eliminar foto - ENDPOINT SIMPLE"""
    
    return {
        "success": True,
        "message": f"Foto {foto_id} del gallo {gallo_id} eliminada",
        "data": {
            "gallo_id": gallo_id,
            "foto_id": foto_id,
            "user_id": current_user_id,
            "status": "endpoint funcionando - listo para implementar"
        }
    }
