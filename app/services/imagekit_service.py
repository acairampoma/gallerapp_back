"""
🎬📸 IMAGEKIT SERVICE - Servicio completo para ImageKit
Maneja videos e imágenes para todo el backend
"""
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from app.core.config import settings
import logging
from typing import Optional, Dict, Any
import base64

logger = logging.getLogger(__name__)

class ImageKitService:
    """Servicio para manejar uploads de videos a ImageKit"""

    def __init__(self):
        """Inicializar cliente de ImageKit"""
        try:
            self.imagekit = ImageKit(
                private_key=settings.IMAGEKIT_PRIVATE_KEY,
                public_key=settings.IMAGEKIT_PUBLIC_KEY,
                url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
            )
            logger.info("✅ ImageKit inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando ImageKit: {e}")
            self.imagekit = None

    def upload_video(
        self,
        file_content: bytes,
        file_name: str,
        folder: str = "eventos_peleas"
    ) -> Optional[Dict[str, Any]]:
        """
        Subir video a ImageKit

        Args:
            file_content: Contenido del archivo en bytes
            file_name: Nombre del archivo
            folder: Carpeta en ImageKit (default: eventos_peleas)

        Returns:
            Dict con url, file_id, etc. o None si falla
        """
        if not self.imagekit:
            logger.error("❌ ImageKit no está inicializado")
            return None

        try:
            logger.info(f"🎬 [IMAGEKIT] Subiendo video: {file_name} a carpeta: {folder}")

            # Convertir bytes a base64 para ImageKit
            file_base64 = base64.b64encode(file_content).decode('utf-8')

            # Opciones de upload (SIN response_fields que causa error)
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
                logger.info(f"✅ [IMAGEKIT] Video subido exitosamente")
                logger.info(f"   📹 URL: {result_data.get('url')}")
                logger.info(f"   🆔 File ID: {result_data.get('file_id')}")

                return {
                    'url': result_data.get('url'),
                    'file_id': result_data.get('file_id'),
                    'thumbnail_url': result_data.get('thumbnail_url') or result_data.get('thumbnailUrl'),
                    'file_path': result_data.get('file_path') or result_data.get('filePath'),
                    'file_type': result_data.get('file_type') or result_data.get('fileType')
                }
            else:
                logger.error("❌ [IMAGEKIT] Upload falló - No se recibió respuesta")
                return None

        except Exception as e:
            logger.error(f"❌ [IMAGEKIT] Error subiendo video: {str(e)}")
            logger.exception(e)  # Log completo del error
            return None

    def delete_video(self, file_id: str) -> bool:
        """
        Eliminar video de ImageKit

        Args:
            file_id: ID del archivo en ImageKit

        Returns:
            True si se eliminó correctamente, False si falló
        """
        if not self.imagekit:
            logger.error("❌ ImageKit no está inicializado")
            return False

        try:
            logger.info(f"🗑️ [IMAGEKIT] Eliminando video: {file_id}")

            result = self.imagekit.delete_file(file_id=file_id)

            if result:
                logger.info(f"✅ [IMAGEKIT] Video eliminado exitosamente")
                return True
            else:
                logger.error(f"❌ [IMAGEKIT] No se pudo eliminar el video")
                return False

        except Exception as e:
            logger.error(f"❌ [IMAGEKIT] Error eliminando video: {str(e)}")
            return False

    # ========================================
    # MÉTODOS PARA IMÁGENES
    # ========================================

    def upload_image(
        self,
        file_content: bytes,
        file_name: str,
        folder: str = "images",
        width: Optional[int] = None,
        height: Optional[int] = None,
        quality: int = 80
    ) -> Optional[Dict[str, Any]]:
        """
        Subir imagen a ImageKit

        Args:
            file_content: Contenido del archivo en bytes
            file_name: Nombre del archivo
            folder: Carpeta en ImageKit (default: images)
            width: Ancho para redimensionar (opcional)
            height: Alto para redimensionar (opcional)
            quality: Calidad de la imagen (1-100, default: 80)

        Returns:
            Dict con url, file_id, thumbnail_url, etc. o None si falla
        """
        if not self.imagekit:
            logger.error("❌ ImageKit no está inicializado")
            return None

        try:
            logger.info(f"📸 [IMAGEKIT] Subiendo imagen: {file_name} a carpeta: {folder}")

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
                
                # Construir URL optimizada si se especificaron dimensiones
                url = result_data.get('url')
                if width or height or quality != 80:
                    url = self.get_optimized_url(url, width, height, quality)
                
                logger.info(f"✅ [IMAGEKIT] Imagen subida exitosamente")
                logger.info(f"   📸 URL: {url}")
                logger.info(f"   🆔 File ID: {result_data.get('file_id')}")

                return {
                    'url': url,
                    'url_original': result_data.get('url'),
                    'file_id': result_data.get('file_id'),
                    'thumbnail_url': result_data.get('thumbnail_url') or result_data.get('thumbnailUrl'),
                    'file_path': result_data.get('file_path') or result_data.get('filePath'),
                    'file_type': result_data.get('file_type') or result_data.get('fileType'),
                    'width': result_data.get('width'),
                    'height': result_data.get('height'),
                    'size': result_data.get('size')
                }
            else:
                logger.error("❌ [IMAGEKIT] Upload falló - No se recibió respuesta")
                return None

        except Exception as e:
            logger.error(f"❌ [IMAGEKIT] Error subiendo imagen: {str(e)}")
            logger.exception(e)
            return None

    def upload_image_with_transformations(
        self,
        file_content: bytes,
        file_name: str,
        folder: str = "images",
        width: int = 400,
        height: int = 400,
        crop: str = "maintain_ratio",
        quality: int = 80,
        format: str = "auto"
    ) -> Optional[Dict[str, Any]]:
        """
        Subir imagen con transformaciones específicas (para avatares, thumbnails, etc.)

        Args:
            file_content: Contenido del archivo en bytes
            file_name: Nombre del archivo
            folder: Carpeta en ImageKit
            width: Ancho deseado
            height: Alto deseado
            crop: Modo de recorte (maintain_ratio, force, at_least, at_max)
            quality: Calidad (1-100)
            format: Formato de salida (auto, jpg, png, webp)

        Returns:
            Dict con url optimizada, file_id, etc.
        """
        result = self.upload_image(file_content, file_name, folder)
        
        if result:
            # Generar URL con transformaciones
            optimized_url = self.get_optimized_url(
                url=result['url_original'],
                width=width,
                height=height,
                quality=quality,
                crop=crop,
                format=format
            )
            result['url'] = optimized_url
            result['url_optimized'] = optimized_url
        
        return result

    def delete_image(self, file_id: str) -> bool:
        """
        Eliminar imagen de ImageKit (alias de delete_video)

        Args:
            file_id: ID del archivo en ImageKit

        Returns:
            True si se eliminó correctamente, False si falló
        """
        return self.delete_video(file_id)

    def get_optimized_url(
        self,
        url: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        quality: int = 80,
        crop: str = "maintain_ratio",
        format: str = "auto"
    ) -> str:
        """
        Generar URL optimizada con transformaciones de ImageKit

        Args:
            url: URL original de ImageKit
            width: Ancho deseado
            height: Alto deseado
            quality: Calidad (1-100)
            crop: Modo de recorte
            format: Formato de salida

        Returns:
            URL con transformaciones aplicadas
        """
        if not url:
            return url

        # Construir string de transformaciones
        transformations = []
        
        if width:
            transformations.append(f"w-{width}")
        if height:
            transformations.append(f"h-{height}")
        if quality != 80:
            transformations.append(f"q-{quality}")
        if crop != "maintain_ratio":
            transformations.append(f"c-{crop}")
        if format != "auto":
            transformations.append(f"f-{format}")

        if not transformations:
            return url

        # Insertar transformaciones en la URL
        # URL de ImageKit: https://ik.imagekit.io/tu_id/ruta/archivo.jpg
        # Con transformaciones: https://ik.imagekit.io/tu_id/tr:w-400,h-300,q-80/ruta/archivo.jpg
        
        transformation_string = f"tr:{','.join(transformations)}"
        
        # Buscar donde insertar las transformaciones
        parts = url.split('/')
        for i, part in enumerate(parts):
            if part.startswith('ik.imagekit.io') or 'imagekit' in part:
                # Insertar después del ID de ImageKit
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
        """
        Generar URL de thumbnail optimizado

        Args:
            url: URL original
            width: Ancho del thumbnail (default: 200)
            height: Alto del thumbnail (default: 200)
            quality: Calidad (default: 60)

        Returns:
            URL del thumbnail
        """
        return self.get_optimized_url(
            url=url,
            width=width,
            height=height,
            quality=quality,
            crop="force",
            format="webp"
        )


# Instancia global del servicio
imagekit_service = ImageKitService()
