# 📷 app/api/v1/fotos_simple.py - ENDPOINTS DE FOTOS CON CLOUDINARY REAL
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from io import BytesIO

from app.database import get_db
from app.core.security import get_current_user_id

router = APIRouter()

@router.post("/{gallo_id}/foto", response_model=dict)
async def upload_foto_real(
    gallo_id: int,
    foto: UploadFile = File(...),
    descripcion: str = Form("Foto del gallo"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📤 Subir foto REAL a Cloudinary"""
    
    try:
        # Validar que es una imagen
        if not foto.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser una imagen"
            )
        
        # Validar tamaño (max 5MB)
        if foto.size and foto.size > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="La imagen es muy grande (máximo 5MB)"
            )
        
        # Leer el archivo
        file_content = await foto.read()
        
        # Subir a Cloudinary
        try:
            upload_result = cloudinary.uploader.upload(
                file_content,
                folder=f"galloapp/user_{current_user_id}/gallo_{gallo_id}",
                public_id=f"gallo_{gallo_id}_{foto.filename.split('.')[0]}",
                overwrite=True,
                resource_type="image",
                format="webp",  # Convertir a WebP para mejor compresion
                quality="auto",
                fetch_format="auto"
            )
            
            return {
                "success": True,
                "message": f"Foto subida exitosamente a Cloudinary para gallo {gallo_id}",
                "data": {
                    "gallo_id": gallo_id,
                    "user_id": current_user_id,
                    "cloudinary": {
                        "public_id": upload_result["public_id"],
                        "secure_url": upload_result["secure_url"],
                        "url": upload_result["url"],
                        "format": upload_result["format"],
                        "width": upload_result["width"],
                        "height": upload_result["height"],
                        "bytes": upload_result["bytes"]
                    },
                    "archivo_original": {
                        "filename": foto.filename,
                        "content_type": foto.content_type,
                        "size_mb": round(foto.size / (1024 * 1024), 2) if foto.size else 0
                    },
                    "descripcion": descripcion,
                    "status": "✅ SUBIDO A CLOUDINARY EXITOSAMENTE"
                }
            }
            
        except Exception as cloudinary_error:
            raise HTTPException(
                status_code=500,
                detail=f"Error subiendo a Cloudinary: {str(cloudinary_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando foto: {str(e)}"
        )

@router.get("/{gallo_id}/fotos", response_model=dict)
async def list_fotos_simple(
    gallo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Listar fotos del gallo desde Cloudinary"""
    
    try:
        # Buscar fotos en Cloudinary
        search_expression = f"folder:galloapp/user_{current_user_id}/gallo_{gallo_id}/*"
        
        try:
            search_result = cloudinary.Search().expression(search_expression).execute()
            
            fotos = []
            for resource in search_result.get('resources', []):
                fotos.append({
                    "public_id": resource["public_id"],
                    "secure_url": resource["secure_url"],
                    "url": resource["url"],
                    "format": resource["format"],
                    "width": resource["width"],
                    "height": resource["height"],
                    "bytes": resource["bytes"],
                    "created_at": resource["created_at"]
                })
            
            return {
                "success": True,
                "message": f"Fotos del gallo {gallo_id} desde Cloudinary",
                "data": {
                    "gallo_id": gallo_id,
                    "user_id": current_user_id,
                    "fotos": fotos,
                    "total_fotos": len(fotos),
                    "cloudinary_folder": f"galloapp/user_{current_user_id}/gallo_{gallo_id}",
                    "status": "✅ CLOUDINARY SINCRONIZADO"
                }
            }
            
        except Exception as cloudinary_error:
            return {
                "success": True,
                "message": f"No se encontraron fotos para gallo {gallo_id}",
                "data": {
                    "gallo_id": gallo_id,
                    "user_id": current_user_id,
                    "fotos": [],
                    "total_fotos": 0,
                    "error": str(cloudinary_error)
                }
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error consultando fotos: {str(e)}"
        )

@router.delete("/{gallo_id}/fotos/{public_id}", response_model=dict)
async def delete_foto_cloudinary(
    gallo_id: int,
    public_id: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🗑️ Eliminar foto de Cloudinary"""
    
    try:
        # Eliminar de Cloudinary
        delete_result = cloudinary.uploader.destroy(public_id)
        
        return {
            "success": True,
            "message": f"Foto eliminada de Cloudinary",
            "data": {
                "gallo_id": gallo_id,
                "public_id": public_id,
                "user_id": current_user_id,
                "cloudinary_result": delete_result,
                "status": "✅ ELIMINADO DE CLOUDINARY"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error eliminando foto: {str(e)}"
        )
