"""
🎬 IMAGEKIT SERVICE - Servicio para subir videos a ImageKit
Solo para videos de EVENTO x PELEAS
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


# Instancia global del servicio
imagekit_service = ImageKitService()
