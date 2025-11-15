"""
☁️ CLOUDINARY ADAPTER - Implementación del patrón Adapter para Cloudinary
Permite volver a Cloudinary sin cambiar código
"""
import cloudinary
import cloudinary.uploader
from app.core.config import settings
from app.services.storage.base_storage import (
    BaseStorageAdapter,
    UploadResult,
    TransformOptions
)
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CloudinaryAdapter(BaseStorageAdapter):
    """Adaptador para Cloudinary"""
    
    def __init__(self):
        """Inicializar cliente de Cloudinary"""
        try:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET
            )
            self._is_available = True
            logger.info("✅ CloudinaryAdapter inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando CloudinaryAdapter: {e}")
            self._is_available = False
    
    @property
    def provider_name(self) -> str:
        return "Cloudinary"
    
    @property
    def is_available(self) -> bool:
        return self._is_available
    
    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        folder: str = "uploads",
        file_type: str = "auto"
    ) -> Optional[UploadResult]:
        """Subir archivo a Cloudinary"""
        if not self.is_available:
            logger.error("❌ Cloudinary no está disponible")
            return None
        
        try:
            logger.info(f"📤 [Cloudinary] Subiendo: {file_name} a {folder}")
            
            # Determinar resource_type
            resource_type = "auto"
            if file_type == "video":
                resource_type = "video"
            elif file_type == "image":
                resource_type = "image"
            
            # Subir archivo
            upload_result = cloudinary.uploader.upload(
                file_content,
                folder=folder,
                resource_type=resource_type
            )
            
            logger.info(f"✅ [Cloudinary] Archivo subido exitosamente")
            logger.info(f"   📍 URL: {upload_result.get('secure_url')}")
            logger.info(f"   🆔 Public ID: {upload_result.get('public_id')}")
            
            return UploadResult(
                url=upload_result.get('secure_url'),
                file_id=upload_result.get('public_id'),  # En Cloudinary es public_id
                thumbnail_url=upload_result.get('thumbnail_url'),
                file_path=upload_result.get('public_id'),
                file_type=upload_result.get('resource_type'),
                width=upload_result.get('width'),
                height=upload_result.get('height'),
                size=upload_result.get('bytes')
            )
                
        except Exception as e:
            logger.error(f"❌ [Cloudinary] Error subiendo archivo: {str(e)}")
            logger.exception(e)
            return None
    
    def upload_with_transformations(
        self,
        file_content: bytes,
        file_name: str,
        folder: str = "uploads",
        transforms: TransformOptions = None
    ) -> Optional[UploadResult]:
        """Subir archivo con transformaciones a Cloudinary"""
        if not self.is_available:
            logger.error("❌ Cloudinary no está disponible")
            return None
        
        try:
            # Construir transformaciones de Cloudinary
            transformation = []
            if transforms:
                trans_dict = {}
                if transforms.width:
                    trans_dict['width'] = transforms.width
                if transforms.height:
                    trans_dict['height'] = transforms.height
                if transforms.quality != 80:
                    trans_dict['quality'] = transforms.quality
                if transforms.crop != "maintain_ratio":
                    # Mapear a Cloudinary crop modes
                    crop_map = {
                        "force": "fill",
                        "at_least": "lfill",
                        "at_max": "limit",
                        "maintain_ratio": "fit"
                    }
                    trans_dict['crop'] = crop_map.get(transforms.crop, "fit")
                if transforms.format != "auto":
                    trans_dict['format'] = transforms.format
                
                if trans_dict:
                    transformation.append(trans_dict)
            
            # Subir con transformaciones
            upload_result = cloudinary.uploader.upload(
                file_content,
                folder=folder,
                transformation=transformation if transformation else None
            )
            
            logger.info(f"✅ [Cloudinary] Archivo subido con transformaciones")
            
            return UploadResult(
                url=upload_result.get('secure_url'),
                file_id=upload_result.get('public_id'),
                thumbnail_url=upload_result.get('thumbnail_url'),
                file_path=upload_result.get('public_id'),
                file_type=upload_result.get('resource_type'),
                width=upload_result.get('width'),
                height=upload_result.get('height'),
                size=upload_result.get('bytes')
            )
                
        except Exception as e:
            logger.error(f"❌ [Cloudinary] Error subiendo archivo: {str(e)}")
            return None
    
    def delete_file(self, file_id: str) -> bool:
        """Eliminar archivo de Cloudinary"""
        if not self.is_available:
            logger.error("❌ Cloudinary no está disponible")
            return False
        
        try:
            logger.info(f"🗑️ [Cloudinary] Eliminando: {file_id}")
            
            # Intentar eliminar como imagen
            result = cloudinary.uploader.destroy(file_id)
            
            # Si falla, intentar como video
            if result.get('result') != 'ok':
                result = cloudinary.uploader.destroy(file_id, resource_type="video")
            
            if result.get('result') == 'ok':
                logger.info(f"✅ [Cloudinary] Archivo eliminado exitosamente")
                return True
            else:
                logger.warning(f"⚠️ [Cloudinary] No se pudo eliminar: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ [Cloudinary] Error eliminando archivo: {str(e)}")
            return False
    
    def get_optimized_url(
        self,
        url: str,
        transforms: TransformOptions
    ) -> str:
        """
        Generar URL optimizada con transformaciones de Cloudinary
        
        Nota: Cloudinary permite transformaciones on-the-fly en la URL
        """
        if not url or not transforms:
            return url
        
        # Construir string de transformaciones
        trans_parts = []
        
        if transforms.width:
            trans_parts.append(f"w_{transforms.width}")
        if transforms.height:
            trans_parts.append(f"h_{transforms.height}")
        if transforms.quality != 80:
            trans_parts.append(f"q_{transforms.quality}")
        if transforms.crop != "maintain_ratio":
            crop_map = {
                "force": "fill",
                "at_least": "lfill",
                "at_max": "limit",
                "maintain_ratio": "fit"
            }
            crop_value = crop_map.get(transforms.crop, "fit")
            trans_parts.append(f"c_{crop_value}")
        if transforms.format != "auto":
            trans_parts.append(f"f_{transforms.format}")
        
        if not trans_parts:
            return url
        
        # Insertar transformaciones en URL de Cloudinary
        # URL: https://res.cloudinary.com/cloud_name/image/upload/v123/folder/file.jpg
        # Con transformaciones: https://res.cloudinary.com/cloud_name/image/upload/w_400,h_300/v123/folder/file.jpg
        
        transformation_string = ','.join(trans_parts)
        
        # Buscar "upload/" y insertar después
        if '/upload/' in url:
            url = url.replace('/upload/', f'/upload/{transformation_string}/')
        
        return url
    
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
cloudinary_adapter = CloudinaryAdapter()
