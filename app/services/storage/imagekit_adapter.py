"""
📸 IMAGEKIT ADAPTER - Implementación del patrón Adapter para ImageKit
"""
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from app.core.config import settings
from app.services.storage.base_storage import (
    BaseStorageAdapter,
    UploadResult,
    TransformOptions
)
import logging
import base64
from typing import Optional

logger = logging.getLogger(__name__)


class ImageKitAdapter(BaseStorageAdapter):
    """Adaptador para ImageKit"""
    
    def __init__(self):
        """Inicializar cliente de ImageKit"""
        try:
            self.imagekit = ImageKit(
                private_key=settings.IMAGEKIT_PRIVATE_KEY,
                public_key=settings.IMAGEKIT_PUBLIC_KEY,
                url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
            )
            self._is_available = True
            logger.info("✅ ImageKitAdapter inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando ImageKitAdapter: {e}")
            self.imagekit = None
            self._is_available = False
    
    @property
    def provider_name(self) -> str:
        return "ImageKit"
    
    @property
    def is_available(self) -> bool:
        return self._is_available and self.imagekit is not None
    
    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        folder: str = "uploads",
        file_type: str = "auto"
    ) -> Optional[UploadResult]:
        """Subir archivo a ImageKit"""
        if not self.is_available:
            logger.error("❌ ImageKit no está disponible")
            return None
        
        try:
            logger.info(f"📤 [ImageKit] Subiendo: {file_name} a {folder}")
            
            # Convertir bytes a base64
            file_base64 = base64.b64encode(file_content).decode('utf-8')
            
            # Opciones de upload
            options = UploadFileRequestOptions(
                folder=folder,
                use_unique_file_name=True
            )
            
            # Subir archivo
            upload_result = self.imagekit.upload_file(
                file=file_base64,
                file_name=file_name,
                options=options
            )
            
            if upload_result and upload_result.response_metadata.raw:
                result_data = upload_result.response_metadata.raw
                
                logger.info(f"✅ [ImageKit] Archivo subido exitosamente")
                logger.info(f"   📍 URL: {result_data.get('url')}")
                logger.info(f"   🆔 File ID: {result_data.get('file_id')}")
                
                return UploadResult(
                    url=result_data.get('url'),
                    file_id=result_data.get('file_id'),
                    thumbnail_url=result_data.get('thumbnail_url') or result_data.get('thumbnailUrl'),
                    file_path=result_data.get('file_path') or result_data.get('filePath'),
                    file_type=result_data.get('file_type') or result_data.get('fileType'),
                    width=result_data.get('width'),
                    height=result_data.get('height'),
                    size=result_data.get('size')
                )
            else:
                logger.error("❌ [ImageKit] Upload falló - No se recibió respuesta")
                return None
                
        except Exception as e:
            logger.error(f"❌ [ImageKit] Error subiendo archivo: {str(e)}")
            logger.exception(e)
            return None
    
    def upload_with_transformations(
        self,
        file_content: bytes,
        file_name: str,
        folder: str = "uploads",
        transforms: TransformOptions = None
    ) -> Optional[UploadResult]:
        """Subir archivo con transformaciones"""
        # Primero subir el archivo
        result = self.upload_file(file_content, file_name, folder)
        
        if result and transforms:
            # Aplicar transformaciones a la URL
            optimized_url = self.get_optimized_url(result.url, transforms)
            result.url = optimized_url
        
        return result
    
    def delete_file(self, file_id: str) -> bool:
        """Eliminar archivo de ImageKit"""
        if not self.is_available:
            logger.error("❌ ImageKit no está disponible")
            return False
        
        try:
            logger.info(f"🗑️ [ImageKit] Eliminando: {file_id}")
            
            result = self.imagekit.delete_file(file_id=file_id)
            
            if result:
                logger.info(f"✅ [ImageKit] Archivo eliminado exitosamente")
                return True
            else:
                logger.error(f"❌ [ImageKit] No se pudo eliminar el archivo")
                return False
                
        except Exception as e:
            logger.error(f"❌ [ImageKit] Error eliminando archivo: {str(e)}")
            return False
    
    def get_optimized_url(
        self,
        url: str,
        transforms: TransformOptions
    ) -> str:
        """Generar URL optimizada con transformaciones de ImageKit"""
        if not url or not transforms:
            return url
        
        # Construir string de transformaciones
        transformation_parts = []
        
        if transforms.width:
            transformation_parts.append(f"w-{transforms.width}")
        if transforms.height:
            transformation_parts.append(f"h-{transforms.height}")
        if transforms.quality != 80:
            transformation_parts.append(f"q-{transforms.quality}")
        if transforms.crop != "maintain_ratio":
            # Mapear nombres estándar a ImageKit
            crop_map = {
                "force": "force",
                "at_least": "at_least",
                "at_max": "at_max",
                "maintain_ratio": "maintain_ratio"
            }
            crop_value = crop_map.get(transforms.crop, "maintain_ratio")
            transformation_parts.append(f"c-{crop_value}")
        if transforms.format != "auto":
            transformation_parts.append(f"f-{transforms.format}")
        
        if not transformation_parts:
            return url
        
        # Insertar transformaciones en la URL de ImageKit
        # URL: https://ik.imagekit.io/tu_id/ruta/archivo.jpg
        # Con transformaciones: https://ik.imagekit.io/tu_id/tr:w-400,h-300/ruta/archivo.jpg
        
        transformation_string = f"tr:{','.join(transformation_parts)}"
        
        # Buscar donde insertar las transformaciones
        parts = url.split('/')
        for i, part in enumerate(parts):
            if 'imagekit' in part.lower():
                # Insertar después del ID de ImageKit (siguiente posición)
                if i + 1 < len(parts):
                    parts.insert(i + 2, transformation_string)
                    break
        
        return '/'.join(parts)
    
    def get_thumbnail_url(
        self,
        url: str,
        width: int = 200,
        height: int = 200,
        quality: int = 60
    ) -> str:
        """Generar URL de thumbnail optimizado"""
        transforms = TransformOptions(
            width=width,
            height=height,
            quality=quality,
            crop="force",
            format="webp"
        )
        return self.get_optimized_url(url, transforms)


# Instancia global del adaptador
imagekit_adapter = ImageKitAdapter()
