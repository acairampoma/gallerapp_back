# 📷 app/api/v1/fotos_clean.py - ENDPOINTS DE FOTOS LIMPIOS
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.gallo import Gallo
from app.models.foto import FotoGallo
from app.services.cloudinary_service import CloudinaryService
from app.services.validation_service import ValidationService

router = APIRouter()

# ========================================
# 📷 GESTIÓN DE FOTOS (3 ENDPOINTS)
# ========================================

@router.post("/{gallo_id}/foto", response_model=dict)
async def upload_foto(
    gallo_id: int,
    foto: UploadFile = File(...),
    descripcion: Optional[str] = Form("Foto del gallo"),
    tipo: str = Form("adicional"),  # principal o adicional
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📤 Subir foto (principal o adicional)"""
    
    try:
        # Verificar que el gallo existe y pertenece al usuario
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Validar archivo
        ValidationService.validate_photo_file(foto)
        
        # Si es foto principal, eliminar la anterior
        if tipo == "principal":
            foto_principal_anterior = db.query(FotoGallo).filter(
                FotoGallo.gallo_id == gallo_id,
                FotoGallo.tipo == "principal"
            ).first()
            
            if foto_principal_anterior:
                try:
                    CloudinaryService.delete_photo(foto_principal_anterior.cloudinary_public_id)
                    db.delete(foto_principal_anterior)
                except:
                    pass
        
        # Subir a Cloudinary
        cloudinary_result = CloudinaryService.upload_gallo_photo(
            file=foto,
            gallo_codigo=gallo.codigo_identificacion,
            photo_type=tipo
        )
        
        # Calcular orden para fotos adicionales
        orden = 0
        if tipo == "adicional":
            max_orden = db.query(FotoGallo).filter(
                FotoGallo.gallo_id == gallo_id,
                FotoGallo.tipo == "adicional"
            ).count()
            orden = max_orden + 1
        
        # Crear registro en BD
        nueva_foto = FotoGallo(
            gallo_id=gallo_id,
            cloudinary_public_id=cloudinary_result["public_id"],
            foto_url=cloudinary_result["secure_url"],
            tipo=tipo,
            descripcion=descripcion,
            orden=orden,
            foto_metadata=cloudinary_result["metadata"]
        )
        db.add(nueva_foto)
        
        # Si es principal, actualizar el gallo
        if tipo == "principal":
            gallo.foto_principal_url = cloudinary_result["secure_url"]
        
        db.commit()
        db.refresh(nueva_foto)
        
        return {
            "success": True,
            "message": f"Foto {tipo} subida exitosamente",
            "data": {
                "foto": {
                    "id": nueva_foto.id,
                    "url": nueva_foto.foto_url,
                    "tipo": nueva_foto.tipo,
                    "descripcion": nueva_foto.descripcion,
                    "orden": nueva_foto.orden,
                    "cloudinary_public_id": nueva_foto.cloudinary_public_id
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error subiendo foto: {str(e)}"
        )

@router.get("/{gallo_id}/fotos", response_model=dict)
async def list_fotos(
    gallo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Listar todas las fotos del gallo"""
    
    try:
        # Verificar que el gallo existe y pertenece al usuario
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Obtener fotos ordenadas
        fotos = db.query(FotoGallo).filter(
            FotoGallo.gallo_id == gallo_id
        ).order_by(
            FotoGallo.tipo.desc(),  # principal primero
            FotoGallo.orden
        ).all()
        
        fotos_data = []
        for foto in fotos:
            fotos_data.append({
                "id": foto.id,
                "url": foto.foto_url,
                "cloudinary_public_id": foto.cloudinary_public_id,
                "tipo": foto.tipo,
                "descripcion": foto.descripcion,
                "orden": foto.orden,
                "size_mb": foto.size_mb,
                "created_at": foto.created_at.isoformat()
            })
        
        # Estadísticas simples
        total_fotos = len(fotos_data)
        foto_principal = next((f for f in fotos_data if f["tipo"] == "principal"), None)
        fotos_adicionales = [f for f in fotos_data if f["tipo"] == "adicional"]
        
        return {
            "success": True,
            "data": {
                "fotos": fotos_data,
                "estadisticas": {
                    "total_fotos": total_fotos,
                    "tiene_foto_principal": foto_principal is not None,
                    "fotos_adicionales": len(fotos_adicionales),
                    "storage_usado_mb": sum([f["size_mb"] for f in fotos_data])
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo fotos: {str(e)}"
        )

@router.delete("/{gallo_id}/fotos/{foto_id}", response_model=dict)
async def delete_foto(
    gallo_id: int,
    foto_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🗑️ Eliminar foto específica"""
    
    try:
        # Verificar que el gallo existe y pertenece al usuario
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Obtener foto
        foto = db.query(FotoGallo).filter(
            FotoGallo.id == foto_id,
            FotoGallo.gallo_id == gallo_id
        ).first()
        
        if not foto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Foto no encontrada"
            )
        
        # Eliminar de Cloudinary
        try:
            CloudinaryService.delete_photo(foto.cloudinary_public_id)
        except Exception as e:
            print(f"Error eliminando de Cloudinary: {e}")
        
        # Si era foto principal, limpiar referencia en gallo
        if foto.tipo == "principal":
            gallo.foto_principal_url = None
        
        # Eliminar de BD
        foto_eliminada = {
            "id": foto.id,
            "url": foto.foto_url,
            "tipo": foto.tipo,
            "descripcion": foto.descripcion
        }
        
        db.delete(foto)
        db.commit()
        
        return {
            "success": True,
            "message": "Foto eliminada exitosamente",
            "data": {
                "foto_eliminada": foto_eliminada
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando foto: {str(e)}"
        )
