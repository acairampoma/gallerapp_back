"""
🎯 STORAGE MANAGER - Gestor centralizado de almacenamiento
Permite cambiar de proveedor (ImageKit, Cloudinary, S3) como cambiar de zapatillas
"""
from app.services.storage.base_storage import (
    BaseStorageAdapter,
    UploadResult,
    TransformOptions
)
from app.services.storage.imagekit_adapter import imagekit_adapter
from app.services.storage.cloudinary_adapter import cloudinary_adapter
from app.core.config import settings
import logging
from typing import Optional, Literal
from enum import Enum

logger = logging.getLogger(__name__)


class StorageProvider(str, Enum):
    """Proveedores de almacenamiento disponibles"""
    IMAGEKIT = "imagekit"
    CLOUDINARY = "cloudinary"
    S3 = "s3"  # Para futuro
    LOCAL = "local"  # Para desarrollo


class StorageManager:
    """
    Gestor centralizado de almacenamiento
    
    Permite cambiar de proveedor sin modificar código:
    - En settings.py: STORAGE_PROVIDER = "imagekit" o "cloudinary"
    - Todo el código sigue funcionando igual
    """
    
    def __init__(self):
        """Inicializar gestor con el proveedor configurado"""
        self._adapters = {
            StorageProvider.IMAGEKIT: imagekit_adapter,
            StorageProvider.CLOUDINARY: cloudinary_adapter,
            # Agregar más proveedores aquí en el futuro
        }
        
        # Obtener proveedor activo desde settings
        self._active_provider = self._get_active_provider()
        self._adapter = self._get_adapter()
        
        logger.info(f"🎯 StorageManager inicializado con proveedor: {self.provider_name}")
    
    def _get_active_provider(self) -> StorageProvider:
        """Obtener proveedor activo desde configuración"""
        # Leer desde settings (agregar STORAGE_PROVIDER a settings.py)
        provider_name = getattr(settings, 'STORAGE_PROVIDER', 'imagekit').lower()
        
        try:
            return StorageProvider(provider_name)
        except ValueError:
            logger.warning(f"⚠️ Proveedor '{provider_name}' no válido, usando ImageKit por defecto")
            return StorageProvider.IMAGEKIT
    
    def _get_adapter(self) -> BaseStorageAdapter:
        """Obtener adaptador del proveedor activo"""
        adapter = self._adapters.get(self._active_provider)
        
        if not adapter:
            logger.error(f"❌ No hay adaptador para {self._active_provider}")
            # Fallback a ImageKit
            return self._adapters[StorageProvider.IMAGEKIT]
        
        if not adapter.is_available:
            logger.warning(f"⚠️ {adapter.provider_name} no está disponible, buscando alternativa...")
            # Buscar primer adaptador disponible
            for alt_adapter in self._adapters.values():
                if alt_adapter.is_available:
                    logger.info(f"✅ Usando {alt_adapter.provider_name} como alternativa")
                    return alt_adapter
        
        return adapter
    
    @property
    def provider_name(self) -> str:
        """Nombre del proveedor activo"""
        return self._adapter.provider_name
    
    @property
    def is_available(self) -> bool:
        """Verificar si el proveedor está disponible"""
        return self._adapter.is_available
    
    def switch_provider(self, provider: StorageProvider):
        """
        Cambiar de proveedor en runtime (útil para testing o migración gradual)
        
        Args:
            provider: Nuevo proveedor a usar
        """
        if provider not in self._adapters:
            raise ValueError(f"Proveedor {provider} no disponible")
        
        old_provider = self.provider_name
        self._active_provider = provider
        self._adapter = self._get_adapter()
        
        logger.info(f"🔄 Proveedor cambiado: {old_provider} → {self.provider_name}")
    
    # ========================================
    # MÉTODOS DELEGADOS AL ADAPTADOR ACTIVO
    # ========================================
    
    def upload_image(
        self,
        file_content: bytes,
        file_name: str,
        folder: str = "images"
    ) -> Optional[UploadResult]:
        """
        Subir imagen
        
        Args:
            file_content: Contenido del archivo
            file_name: Nombre del archivo
            folder: Carpeta de destino
            
        Returns:
            UploadResult con datos del archivo
        """
        return self._adapter.upload_file(
            file_content=file_content,
            file_name=file_name,
            folder=folder,
            file_type="image"
        )
    
    def upload_video(
        self,
        file_content: bytes,
        file_name: str,
        folder: str = "videos"
    ) -> Optional[UploadResult]:
        """
        Subir video
        
        Args:
            file_content: Contenido del archivo
            file_name: Nombre del archivo
            folder: Carpeta de destino
            
        Returns:
            UploadResult con datos del archivo
        """
        return self._adapter.upload_file(
            file_content=file_content,
            file_name=file_name,
            folder=folder,
            file_type="video"
        )
    
    def upload_with_transformations(
        self,
        file_content: bytes,
        file_name: str,
        folder: str = "images",
        width: int = 400,
        height: int = 400,
        crop: str = "maintain_ratio",
        quality: int = 80,
        format: str = "auto"
    ) -> Optional[UploadResult]:
        """
        Subir archivo con transformaciones
        
        Args:
            file_content: Contenido del archivo
            file_name: Nombre del archivo
            folder: Carpeta de destino
            width: Ancho deseado
            height: Alto deseado
            crop: Modo de recorte
            quality: Calidad (1-100)
            format: Formato de salida
            
        Returns:
            UploadResult con URL optimizada
        """
        transforms = TransformOptions(
            width=width,
            height=height,
            quality=quality,
            crop=crop,
            format=format
        )
        
        return self._adapter.upload_with_transformations(
            file_content=file_content,
            file_name=file_name,
            folder=folder,
            transforms=transforms
        )
    
    def delete_file(self, file_id: str) -> bool:
        """
        Eliminar archivo
        
        Args:
            file_id: ID del archivo a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        return self._adapter.delete_file(file_id)
    
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
        Generar URL optimizada
        
        Args:
            url: URL original
            width: Ancho deseado
            height: Alto deseado
            quality: Calidad
            crop: Modo de recorte
            format: Formato de salida
            
        Returns:
            URL con transformaciones
        """
        transforms = TransformOptions(
            width=width,
            height=height,
            quality=quality,
            crop=crop,
            format=format
        )
        
        return self._adapter.get_optimized_url(url, transforms)
    
    def get_thumbnail_url(
        self,
        url: str,
        width: int = 200,
        height: int = 200,
        quality: int = 60
    ) -> str:
        """
        Generar URL de thumbnail
        
        Args:
            url: URL original
            width: Ancho del thumbnail
            height: Alto del thumbnail
            quality: Calidad
            
        Returns:
            URL del thumbnail
        """
        return self._adapter.get_thumbnail_url(url, width, height, quality)


# ========================================
# INSTANCIA GLOBAL - SINGLETON
# ========================================
storage_manager = StorageManager()


# ========================================
# FUNCIONES DE CONVENIENCIA
# ========================================

def upload_image(file_content: bytes, file_name: str, folder: str = "images") -> Optional[UploadResult]:
    """Shortcut para subir imagen"""
    return storage_manager.upload_image(file_content, file_name, folder)


def upload_video(file_content: bytes, file_name: str, folder: str = "videos") -> Optional[UploadResult]:
    """Shortcut para subir video"""
    return storage_manager.upload_video(file_content, file_name, folder)


def upload_avatar(file_content: bytes, file_name: str, user_id: int) -> Optional[UploadResult]:
    """Shortcut para subir avatar optimizado"""
    return storage_manager.upload_with_transformations(
        file_content=file_content,
        file_name=file_name,
        folder=f"avatars/user_{user_id}",
        width=200,
        height=200,
        crop="force",
        quality=90,
        format="webp"
    )


def delete_file(file_id: str) -> bool:
    """Shortcut para eliminar archivo"""
    return storage_manager.delete_file(file_id)
