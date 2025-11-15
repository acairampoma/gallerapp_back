"""
📸 GALLO IMAGES API - Endpoints modernos para múltiples imágenes
Upload masivo simple y potente (2025 style)
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.core.security import get_current_user_id
from app.services.multi_image_service import multi_image_service
from app.models.gallo_simple import Gallo
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/gallos/{gallo_id}/images/upload")
async def upload_gallo_images(
    gallo_id: int,
    files: List[UploadFile] = File(..., description="Hasta 10 imágenes"),
    set_first_as_principal: bool = Form(True),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    📸 Subir múltiples imágenes de gallo (MODERNO - 2025)
    
    **Características:**
    - ✅ Upload paralelo (más rápido)
    - ✅ Optimización automática (webp, 800x800)
    - ✅ Validación automática
    - ✅ Hasta 10 imágenes a la vez
    - ✅ Primera imagen como principal (opcional)
    
    **Ejemplo:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/gallos/123/images/upload" \
      -H "Authorization: Bearer TOKEN" \
      -F "files=@foto1.jpg" \
      -F "files=@foto2.jpg" \
      -F "files=@foto3.jpg" \
      -F "set_first_as_principal=true"
    ```
    """
    try:
        logger.info(f"📸 Usuario {current_user_id} subiendo {len(files)} imágenes para gallo {gallo_id}")
        
        result = await multi_image_service.upload_gallo_images(
            gallo_id=gallo_id,
            user_id=current_user_id,
            files=files,
            db=db,
            set_first_as_principal=set_first_as_principal
        )
        
        logger.info(f"✅ Subidas {result['uploaded']}/{result['total']} imágenes")
        
        return {
            "success": True,
            "message": f"Subidas {result['uploaded']} de {result['total']} imágenes",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error subiendo imágenes: {e}")
        raise HTTPException(500, f"Error subiendo imágenes: {str(e)}")


@router.post("/gallos/{gallo_id}/images/principal")
async def upload_principal_image(
    gallo_id: int,
    file: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    📸 Subir/actualizar imagen principal del gallo
    
    **Características:**
    - ✅ Optimización automática
    - ✅ Reemplaza imagen anterior
    - ✅ Actualiza gallo.foto_url
    """
    try:
        # Verificar gallo
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(404, "Gallo no encontrado")
        
        # Subir nueva imagen
        folder = f"gallos/user_{current_user_id}/gallo_{gallo_id}"
        file_name = f"gallo_{gallo.codigo_identificacion or gallo_id}_principal_{file.filename}"
        
        result = await multi_image_service.upload_single_image(
            file=file,
            folder=folder,
            file_name=file_name,
            optimize=True
        )
        
        if not result:
            raise HTTPException(500, "Error subiendo imagen")
        
        # Actualizar gallo
        gallo.foto_url = result['url']
        db.commit()
        
        logger.info(f"✅ Imagen principal actualizada para gallo {gallo_id}")
        
        return {
            "success": True,
            "message": "Imagen principal actualizada",
            "data": {
                "gallo_id": gallo_id,
                "foto_url": result['url'],
                "file_id": result['file_id']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(500, str(e))


@router.delete("/gallos/{gallo_id}/images")
async def delete_gallo_images(
    gallo_id: int,
    file_ids: List[str] = Form(...),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🗑️ Eliminar múltiples imágenes de gallo
    
    **Ejemplo:**
    ```bash
    curl -X DELETE "http://localhost:8000/api/v1/gallos/123/images" \
      -H "Authorization: Bearer TOKEN" \
      -F "file_ids=file_id_1" \
      -F "file_ids=file_id_2"
    ```
    """
    try:
        # Verificar gallo
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(404, "Gallo no encontrado")
        
        # Eliminar imágenes
        result = await multi_image_service.delete_multiple_images(file_ids)
        
        logger.info(f"🗑️ Eliminadas {result['deleted']}/{result['total']} imágenes")
        
        return {
            "success": True,
            "message": f"Eliminadas {result['deleted']} de {result['total']} imágenes",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(500, str(e))


@router.post("/upload-multiple")
async def upload_multiple_generic(
    files: List[UploadFile] = File(..., description="Hasta 10 imágenes"),
    folder: str = Form("uploads"),
    optimize: bool = Form(True),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    📸 Upload genérico de múltiples imágenes
    
    **Uso general para cualquier tipo de imagen**
    """
    try:
        base_name = f"user_{current_user_id}"
        
        result = await multi_image_service.upload_multiple_images(
            files=files,
            folder=folder,
            base_name=base_name,
            optimize=optimize,
            parallel=True
        )
        
        return {
            "success": True,
            "message": f"Subidas {result['uploaded']} de {result['total']} imágenes",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(500, str(e))
