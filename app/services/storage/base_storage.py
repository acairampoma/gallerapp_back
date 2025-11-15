"""
🎯 BASE STORAGE ADAPTER - Patrón Adapter para proveedores de almacenamiento
Permite cambiar entre ImageKit, Cloudinary, S3, etc. sin modificar código
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class UploadResult:
    """Resultado estandarizado de upload"""
    url: str
    file_id: str
    thumbnail_url: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    size: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'url': self.url,
            'file_id': self.file_id,
            'thumbnail_url': self.thumbnail_url,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'width': self.width,
            'height': self.height,
            'size': self.size
        }


@dataclass
class TransformOptions:
    """Opciones de transformación estandarizadas"""
    width: Optional[int] = None
    height: Optional[int] = None
    quality: int = 80
    crop: str = "maintain_ratio"  # maintain_ratio, force, at_least, at_max
    format: str = "auto"  # auto, jpg, png, webp


class BaseStorageAdapter(ABC):
    """
    Interfaz base para adaptadores de almacenamiento
    
    Cualquier proveedor (ImageKit, Cloudinary, S3, etc.) debe implementar esta interfaz
    """
    
    @abstractmethod
    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        folder: str = "uploads",
        file_type: str = "auto"  # image, video, auto
    ) -> Optional[UploadResult]:
        """
        Subir archivo al proveedor
        
        Args:
            file_content: Contenido del archivo en bytes
            file_name: Nombre del archivo
            folder: Carpeta de destino
            file_type: Tipo de archivo (image, video, auto)
            
        Returns:
            UploadResult con datos del archivo subido o None si falla
        """
        pass
    
    @abstractmethod
    def upload_with_transformations(
        self,
        file_content: bytes,
        file_name: str,
        folder: str = "uploads",
        transforms: TransformOptions = None
    ) -> Optional[UploadResult]:
        """
        Subir archivo con transformaciones
        
        Args:
            file_content: Contenido del archivo
            file_name: Nombre del archivo
            folder: Carpeta de destino
            transforms: Opciones de transformación
            
        Returns:
            UploadResult con URL optimizada
        """
        pass
    
    @abstractmethod
    def delete_file(self, file_id: str) -> bool:
        """
        Eliminar archivo del proveedor
        
        Args:
            file_id: ID del archivo a eliminar
            
        Returns:
            True si se eliminó correctamente, False si falló
        """
        pass
    
    @abstractmethod
    def get_optimized_url(
        self,
        url: str,
        transforms: TransformOptions
    ) -> str:
        """
        Generar URL optimizada con transformaciones
        
        Args:
            url: URL original
            transforms: Opciones de transformación
            
        Returns:
            URL con transformaciones aplicadas
        """
        pass
    
    @abstractmethod
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
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nombre del proveedor (ImageKit, Cloudinary, S3, etc.)"""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Verificar si el proveedor está disponible y configurado"""
        pass
