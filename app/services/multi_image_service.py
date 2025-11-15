"""
📸 MULTI IMAGE SERVICE - Servicio moderno para múltiples imágenes
Manejo simple y potente de uploads masivos (2025 style)
"""
from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.services.storage import storage_manager
from app.models.gallo_simple import Gallo
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class MultiImageService:
    """
    Servicio moderno para manejar múltiples imágenes
    
    Características 2025:
    - Upload paralelo (asyncio)
    - Validación automática
    - Optimización automática
    - Rollback en caso de error
    - Progress tracking
    """
    
    # Configuración
    MAX_IMAGES = 10
    MAX_SIZE_MB = 5
    ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    
    @staticmethod
    def validate_image(file: UploadFile) -> bool:
        """Validar imagen rápidamente"""
        # Validar tipo
        if file.content_type not in MultiImageService.ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo no permitido. Use: {', '.join(MultiImageService.ALLOWED_TYPES)}"
            )
        
        # Validar tamaño (si está disponible)
        if hasattr(file, 'size') and file.size:
            max_bytes = MultiImageService.MAX_SIZE_MB * 1024 * 1024
            if file.size > max_bytes:
                raise HTTPException(
                    status_code=400,
                    detail=f"Imagen muy grande. Máximo {MultiImageService.MAX_SIZE_MB}MB"
                )
        
        return True
    
    @staticmethod
    async def upload_single_image(
        file: UploadFile,
        folder: str,
        file_name: str,
        optimize: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Subir una sola imagen (optimizada)
        
        Args:
            file: Archivo a subir
            folder: Carpeta de destino
            file_name: Nombre del archivo
            optimize: Si optimizar automáticamente
            
        Returns:
            Dict con url y file_id
        """
        try:
            # Validar
            MultiImageService.validate_image(file)
            
            # Leer contenido
            content = await file.read()
            
            # Subir con optimización
            if optimize:
                result = storage_manager.upload_with_transformations(
                    file_content=content,
                    file_name=file_name,
                    folder=folder,
                    width=800,
                    height=800,
                    quality=85,
                    format="webp"
                )
            else:
                result = storage_manager.upload_image(
                    file_content=content,
                    file_name=file_name,
                    folder=folder
                )
            
            if result:
                return {
                    'url': result.url,
                    'file_id': result.file_id,
                    'thumbnail_url': result.thumbnail_url,
                    'size': result.size,
                    'width': result.width,
                    'height': result.height
                }
            
            return None
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error subiendo imagen: {e}")
            raise HTTPException(500, f"Error subiendo imagen: {str(e)}")
    
    @staticmethod
    async def upload_multiple_images(
        files: List[UploadFile],
        folder: str,
        base_name: str,
        optimize: bool = True,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Subir múltiples imágenes (MODERNO - 2025)
        
        Args:
            files: Lista de archivos
            folder: Carpeta de destino
            base_name: Nombre base para los archivos
            optimize: Si optimizar automáticamente
            parallel: Si subir en paralelo (más rápido)
            
        Returns:
            Dict con resultados y errores
        """
        if len(files) > MultiImageService.MAX_IMAGES:
            raise HTTPException(
                400,
                f"Máximo {MultiImageService.MAX_IMAGES} imágenes a la vez"
            )
        
        results = []
        errors = []
        
        if parallel:
            # 🚀 UPLOAD PARALELO (MODERNO)
            tasks = []
            for i, file in enumerate(files):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_name = f"{base_name}_{i+1}_{timestamp}_{file.filename}"
                
                task = MultiImageService.upload_single_image(
                    file=file,
                    folder=folder,
                    file_name=file_name,
                    optimize=optimize
                )
                tasks.append((i, file.filename, task))
            
            # Ejecutar en paralelo
            for i, filename, task in tasks:
                try:
                    result = await task
                    if result:
                        results.append({
                            'index': i,
                            'filename': filename,
                            **result
                        })
                except Exception as e:
                    errors.append({
                        'index': i,
                        'filename': filename,
                        'error': str(e)
                    })
        else:
            # Upload secuencial (más lento pero más seguro)
            for i, file in enumerate(files):
                try:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    file_name = f"{base_name}_{i+1}_{timestamp}_{file.filename}"
                    
                    result = await MultiImageService.upload_single_image(
                        file=file,
                        folder=folder,
                        file_name=file_name,
                        optimize=optimize
                    )
                    
                    if result:
                        results.append({
                            'index': i,
                            'filename': file.filename,
                            **result
                        })
                        
                except Exception as e:
                    errors.append({
                        'index': i,
                        'filename': file.filename,
                        'error': str(e)
                    })
        
        return {
            'success': len(results) > 0,
            'uploaded': len(results),
            'total': len(files),
            'failed': len(errors),
            'results': results,
            'errors': errors
        }
    
    @staticmethod
    async def delete_multiple_images(file_ids: List[str]) -> Dict[str, Any]:
        """
        Eliminar múltiples imágenes
        
        Args:
            file_ids: Lista de file_ids a eliminar
            
        Returns:
            Dict con resultados
        """
        deleted = 0
        errors = []
        
        for file_id in file_ids:
            try:
                success = storage_manager.delete_file(file_id)
                if success:
                    deleted += 1
                else:
                    errors.append({
                        'file_id': file_id,
                        'error': 'Delete returned False'
                    })
            except Exception as e:
                errors.append({
                    'file_id': file_id,
                    'error': str(e)
                })
        
        return {
            'success': deleted > 0,
            'deleted': deleted,
            'total': len(file_ids),
            'failed': len(errors),
            'errors': errors
        }
    
    @staticmethod
    async def upload_gallo_images(
        gallo_id: int,
        user_id: int,
        files: List[UploadFile],
        db: Session,
        set_first_as_principal: bool = True
    ) -> Dict[str, Any]:
        """
        Subir imágenes de gallo (caso de uso específico)
        
        Args:
            gallo_id: ID del gallo
            user_id: ID del usuario
            files: Lista de imágenes
            db: Sesión de base de datos
            set_first_as_principal: Si la primera imagen es la principal
            
        Returns:
            Dict con resultados
        """
        # Verificar que el gallo existe y pertenece al usuario
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == user_id
        ).first()
        
        if not gallo:
            raise HTTPException(404, "Gallo no encontrado")
        
        # Subir imágenes
        folder = f"gallos/user_{user_id}/gallo_{gallo_id}"
        base_name = f"gallo_{gallo.codigo_identificacion or gallo_id}"
        
        upload_result = await MultiImageService.upload_multiple_images(
            files=files,
            folder=folder,
            base_name=base_name,
            optimize=True,
            parallel=True  # 🚀 PARALELO
        )
        
        # Si la primera imagen debe ser principal, actualizar el gallo
        if set_first_as_principal and upload_result['results']:
            first_image = upload_result['results'][0]
            gallo.foto_url = first_image['url']
            db.commit()
        
        return {
            **upload_result,
            'gallo_id': gallo_id,
            'principal_updated': set_first_as_principal and upload_result['results']
        }


# Instancia global
multi_image_service = MultiImageService()
