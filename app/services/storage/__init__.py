"""
🎯 STORAGE MODULE - Sistema de almacenamiento con patrón Adapter
Permite cambiar de proveedor sin modificar código
"""
from app.services.storage.storage_manager import (
    storage_manager,
    StorageProvider,
    upload_image,
    upload_video,
    upload_avatar,
    delete_file
)
from app.services.storage.base_storage import (
    UploadResult,
    TransformOptions
)

__all__ = [
    # Manager principal
    'storage_manager',
    'StorageProvider',
    
    # Funciones de conveniencia
    'upload_image',
    'upload_video',
    'upload_avatar',
    'delete_file',
    
    # Tipos
    'UploadResult',
    'TransformOptions',
]
