# 📷 app/api/v1/fotos_final.py - ESTRUCTURA SIMPLE CORRECTA
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import cloudinary
import cloudinary.uploader

from app.database import get_db
from app.core.security import get_current_user_id

router = APIRouter()

@router.post("/{gallo_id}/foto", response_model=dict)
async def upload_foto_estructura_simple(
    gallo_id: int,
    foto: UploadFile = File(...),
    descripcion: str = Form("Foto del gallo"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📤 Subir foto con ESTRUCTURA SIMPLE: user_X/gallo_Y_foto1.webp"""
    
    try:
        # Validaciones básicas
        if not foto.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
        if foto.size and foto.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="La imagen es muy grande (máximo 5MB)")
        
        # Leer el archivo
        file_content = await foto.read()
        
        # 📁 ESTRUCTURA CORRECTA: galloapp/user_X/gallo_Y_foto1.webp
        upload_result = cloudinary.uploader.upload(
            file_content,
            folder=f"galloapp/user_{current_user_id}",      # ← galloapp/user_3/
            public_id=f"gallo_{gallo_id}_foto1",            # ← gallo_10_foto1
            overwrite=True,
            resource_type="image",
            format="webp",
            quality="auto"
        )
        
        # Guardar URL en PostgreSQL
        update_query = text("""
            UPDATE gallos 
            SET foto_principal_url = :foto_url, updated_at = CURRENT_TIMESTAMP
            WHERE id = :gallo_id AND user_id = :user_id
        """)
        
        db.execute(update_query, {
            "foto_url": upload_result["secure_url"],
            "gallo_id": gallo_id,
            "user_id": current_user_id
        })
        db.commit()
        
        return {
            "success": True,
            "message": f"✅ FOTO SUBIDA A CLOUDINARY - ESTRUCTURA SIMPLE",
            "data": {
                "gallo_id": gallo_id,
                "user_id": current_user_id,
                "cloudinary": {
                    "public_id": upload_result["public_id"],  # user_3/gallo_10_foto1
                    "secure_url": upload_result["secure_url"],
                    "folder": f"galloapp/user_{current_user_id}",
                    "filename": f"gallo_{gallo_id}_foto1.webp",
                    "width": upload_result["width"],
                    "height": upload_result["height"],
                    "bytes": upload_result["bytes"]
                },
                "archivo_original": {
                    "filename": foto.filename,
                    "content_type": foto.content_type,
                    "size_mb": round(foto.size / (1024 * 1024), 2) if foto.size else 0
                },
                "estructura": f"galloapp/user_{current_user_id}/gallo_{gallo_id}_foto1.webp"
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error subiendo foto: {str(e)}")

@router.get("/{gallo_id}/fotos", response_model=dict)
async def list_fotos_estructura_simple(
    gallo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Listar fotos con ESTRUCTURA SIMPLE"""
    
    try:
        # Buscar fotos del gallo específico en la carpeta del usuario
        search_expression = f"folder:galloapp/user_{current_user_id} AND public_id:gallo_{gallo_id}_*"
        
        search_result = cloudinary.Search().expression(search_expression).execute()
        
        fotos = []
        for resource in search_result.get('resources', []):
            fotos.append({
                "public_id": resource["public_id"],      # user_3/gallo_10_foto1
                "secure_url": resource["secure_url"],
                "filename": resource["public_id"].split('/')[-1] + ".webp",  # gallo_10_foto1.webp
                "format": resource["format"],
                "width": resource["width"],
                "height": resource["height"],
                "size_mb": round(resource["bytes"] / (1024 * 1024), 2),
                "created_at": resource["created_at"]
            })
        
        return {
            "success": True,
            "message": f"📁 FOTOS DEL GALLO {gallo_id} - ESTRUCTURA SIMPLE",
            "data": {
                "gallo_id": gallo_id,
                "user_id": current_user_id,
                "fotos": fotos,
                "total_fotos": len(fotos),
                "estructura": f"galloapp/user_{current_user_id}/gallo_{gallo_id}_fotoX.webp",
                "cloudinary_folder": f"galloapp/user_{current_user_id}"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando fotos: {str(e)}")

@router.delete("/{gallo_id}/fotos/{foto_numero}", response_model=dict)
async def delete_foto_estructura_simple(
    gallo_id: int,
    foto_numero: int = 1,  # Por defecto foto1
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🗑️ Eliminar foto específica con ESTRUCTURA SIMPLE"""
    
    try:
        # Construir public_id con estructura simple
        public_id = f"galloapp/user_{current_user_id}/gallo_{gallo_id}_foto{foto_numero}"
        
        # Eliminar de Cloudinary
        delete_result = cloudinary.uploader.destroy(public_id)
        
        # Si era foto1 (principal), limpiar referencia en BD
        if foto_numero == 1:
            update_query = text("""
                UPDATE gallos 
                SET foto_principal_url = NULL, updated_at = CURRENT_TIMESTAMP
                WHERE id = :gallo_id AND user_id = :user_id
            """)
            db.execute(update_query, {"gallo_id": gallo_id, "user_id": current_user_id})
            db.commit()
        
        return {
            "success": True,
            "message": f"✅ FOTO ELIMINADA - ESTRUCTURA SIMPLE",
            "data": {
                "gallo_id": gallo_id,
                "foto_eliminada": f"gallo_{gallo_id}_foto{foto_numero}.webp",
                "public_id": public_id,
                "cloudinary_result": delete_result
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando foto: {str(e)}")
