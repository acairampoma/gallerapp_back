# 🔥 app/services/cloudinary_service.py - Servicio ÉPICO Cloudinary para Gallos
import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import HTTPException, UploadFile
from typing import Optional, List, Dict, Any
import os
import uuid
import magic
from PIL import Image
import io

class CloudinaryService:
    """🌟 Servicio épico para gestión de fotos de gallos en Cloudinary"""
    
    # 📋 CONFIGURACIÓN
    ALLOWED_FORMATS = ['jpg', 'jpeg', 'png', 'webp']
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    FOLDER_GALLOS = "gallos"
    TRANSFORMATIONS = {
        'thumbnail': {'width': 150, 'height': 150, 'crop': 'thumb', 'gravity': 'face'},
        'medium': {'width': 400, 'height': 400, 'crop': 'limit', 'quality': 'auto'},
        'large': {'width': 800, 'height': 800, 'crop': 'limit', 'quality': 'auto'},
        'optimized': {'format': 'webp', 'quality': 'auto:good', 'fetch_format': 'auto'}
    }
    
    @staticmethod
    def validate_image_file(file: UploadFile) -> bool:
        """🔍 Validar archivo de imagen"""
        try:
            # Verificar tamaño
            file_content = file.file.read()
            file.file.seek(0)  # Reset pointer
            
            if len(file_content) > CloudinaryService.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Archivo muy grande. Máximo {CloudinaryService.MAX_FILE_SIZE // (1024*1024)}MB"
                )
            
            # Verificar tipo MIME
            mime = magic.from_buffer(file_content, mime=True)
            if not mime.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail="El archivo debe ser una imagen válida"
                )
            
            # Verificar formato
            format_extension = mime.split('/')[-1].lower()
            if format_extension not in CloudinaryService.ALLOWED_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Formato no permitido. Use: {', '.join(CloudinaryService.ALLOWED_FORMATS)}"
                )
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error validando imagen: {str(e)}"
            )
    
    @staticmethod
    def upload_gallo_photo(
        file: UploadFile, 
        gallo_codigo: str, 
        photo_type: str = "principal",
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """🔥 Subir foto de gallo a Cloudinary con naming convention épica"""
        
        try:
            # Validar archivo
            CloudinaryService.validate_image_file(file)
            
            # Generar public_id único
            unique_id = str(uuid.uuid4())[:8]
            public_id = f"{CloudinaryService.FOLDER_GALLOS}/{gallo_codigo.upper()}_{photo_type}_{unique_id}"
            
            if user_id:
                public_id = f"{CloudinaryService.FOLDER_GALLOS}/user_{user_id}/{gallo_codigo.upper()}_{photo_type}_{unique_id}"
            
            # Upload a Cloudinary
            upload_result = cloudinary.uploader.upload(
                file.file,
                public_id=public_id,
                resource_type="image",
                format="jpg",  # Convertir todo a JPG para consistencia
                quality="auto:good",
                fetch_format="auto",
                flags="progressive",
                transformation=[
                    {"quality": "auto:good"},
                    {"fetch_format": "auto"}
                ],
                # Metadata
                context={
                    "gallo_codigo": gallo_codigo,
                    "photo_type": photo_type,
                    "uploaded_by": f"user_{user_id}" if user_id else "system"
                }
            )
            
            # Generar URLs con transformaciones
            urls = {
                'original': upload_result['secure_url'],
                'thumbnail': cloudinary.CloudinaryImage(public_id).build_url(**CloudinaryService.TRANSFORMATIONS['thumbnail']),
                'medium': cloudinary.CloudinaryImage(public_id).build_url(**CloudinaryService.TRANSFORMATIONS['medium']),
                'large': cloudinary.CloudinaryImage(public_id).build_url(**CloudinaryService.TRANSFORMATIONS['large']),
                'optimized': cloudinary.CloudinaryImage(public_id).build_url(**CloudinaryService.TRANSFORMATIONS['optimized'])
            }
            
            return {
                'success': True,
                'public_id': upload_result['public_id'],
                'secure_url': upload_result['secure_url'],
                'urls': urls,
                'metadata': {
                    'width': upload_result.get('width'),
                    'height': upload_result.get('height'),
                    'format': upload_result.get('format'),
                    'size_bytes': upload_result.get('bytes'),
                    'created_at': upload_result.get('created_at')
                },
                'cloudinary_response': upload_result
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error subiendo foto a Cloudinary: {str(e)}"
            )
    
    @staticmethod
    def upload_multiple_photos(
        files: List[UploadFile],
        gallo_codigo: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """📸 Subir múltiples fotos adicionales"""
        
        results = []
        errors = []
        
        for i, file in enumerate(files):
            try:
                photo_type = f"adicional_{i+1}"
                result = CloudinaryService.upload_gallo_photo(
                    file=file,
                    gallo_codigo=gallo_codigo,
                    photo_type=photo_type,
                    user_id=user_id
                )
                results.append(result)
                
            except Exception as e:
                errors.append({
                    'file_index': i,
                    'filename': file.filename,
                    'error': str(e)
                })
        
        return {
            'success': len(results) > 0,
            'uploaded_count': len(results),
            'total_files': len(files),
            'results': results,
            'errors': errors
        }
    
    @staticmethod
    def delete_photo(public_id: str) -> Dict[str, Any]:
        """🗑️ Eliminar foto de Cloudinary"""
        
        try:
            result = cloudinary.uploader.destroy(public_id)
            
            return {
                'success': result.get('result') == 'ok',
                'public_id': public_id,
                'cloudinary_response': result
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error eliminando foto: {str(e)}"
            )
    
    @staticmethod
    def delete_photo_by_url(secure_url: str) -> Dict[str, Any]:
        """🗑️ Eliminar foto por URL"""
        
        try:
            # Extraer public_id de la URL
            url_parts = secure_url.split('/')
            public_id_with_extension = '/'.join(url_parts[-3:])  # carpeta/archivo.formato
            public_id = public_id_with_extension.rsplit('.', 1)[0]  # Sin extensión
            
            return CloudinaryService.delete_photo(public_id)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error eliminando foto por URL: {str(e)}"
            )
    
    @staticmethod
    def get_photo_info(public_id: str) -> Dict[str, Any]:
        """ℹ️ Obtener información de foto"""
        
        try:
            result = cloudinary.api.resource(public_id)
            
            return {
                'success': True,
                'public_id': result['public_id'],
                'secure_url': result['secure_url'],
                'width': result['width'],
                'height': result['height'],
                'format': result['format'],
                'size_bytes': result['bytes'],
                'created_at': result['created_at'],
                'metadata': result
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"Foto no encontrada: {str(e)}"
            )
    
    @staticmethod
    def list_gallo_photos(gallo_codigo: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """📋 Listar todas las fotos de un gallo"""
        
        try:
            # Construir prefix de búsqueda
            prefix = f"{CloudinaryService.FOLDER_GALLOS}/{gallo_codigo.upper()}_"
            if user_id:
                prefix = f"{CloudinaryService.FOLDER_GALLOS}/user_{user_id}/{gallo_codigo.upper()}_"
            
            result = cloudinary.api.resources(
                type="upload",
                prefix=prefix,
                max_results=50
            )
            
            photos = []
            for resource in result.get('resources', []):
                # Determinar tipo de foto del public_id
                filename = resource['public_id'].split('/')[-1]
                if '_principal_' in filename:
                    photo_type = 'principal'
                elif '_adicional_' in filename:
                    photo_type = 'adicional'
                else:
                    photo_type = 'otros'
                
                photos.append({
                    'public_id': resource['public_id'],
                    'secure_url': resource['secure_url'],
                    'photo_type': photo_type,
                    'width': resource.get('width'),
                    'height': resource.get('height'),
                    'format': resource.get('format'),
                    'size_bytes': resource.get('bytes'),
                    'created_at': resource.get('created_at')
                })
            
            return {
                'success': True,
                'gallo_codigo': gallo_codigo,
                'total_photos': len(photos),
                'photos': photos
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error listando fotos: {str(e)}"
            )
    
    @staticmethod
    def generate_optimized_url(public_id: str, transformation: str = 'optimized') -> str:
        """⚡ Generar URL optimizada con transformaciones"""
        
        if transformation in CloudinaryService.TRANSFORMATIONS:
            return cloudinary.CloudinaryImage(public_id).build_url(
                **CloudinaryService.TRANSFORMATIONS[transformation]
            )
        else:
            return cloudinary.CloudinaryImage(public_id).build_url()
    
    @staticmethod
    def batch_delete_gallo_photos(gallo_codigo: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """🧹 Eliminar todas las fotos de un gallo"""
        
        try:
            # Listar fotos existentes
            photos_list = CloudinaryService.list_gallo_photos(gallo_codigo, user_id)
            
            deleted_count = 0
            errors = []
            
            for photo in photos_list.get('photos', []):
                try:
                    CloudinaryService.delete_photo(photo['public_id'])
                    deleted_count += 1
                except Exception as e:
                    errors.append({
                        'public_id': photo['public_id'],
                        'error': str(e)
                    })
            
            return {
                'success': deleted_count > 0,
                'gallo_codigo': gallo_codigo,
                'deleted_count': deleted_count,
                'total_photos': len(photos_list.get('photos', [])),
                'errors': errors
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error eliminando fotos en lote: {str(e)}"
            )
    
    @staticmethod
    def get_storage_stats() -> Dict[str, Any]:
        """📊 Obtener estadísticas de uso de Cloudinary"""
        
        try:
            # Stats generales
            usage = cloudinary.api.usage()
            
            # Stats de gallos específicamente
            gallos_resources = cloudinary.api.resources(
                type="upload",
                prefix=CloudinaryService.FOLDER_GALLOS,
                max_results=500
            )
            
            total_photos = len(gallos_resources.get('resources', []))
            total_bytes = sum([r.get('bytes', 0) for r in gallos_resources.get('resources', [])])
            
            return {
                'success': True,
                'cloudinary_usage': {
                    'credits_used': usage.get('credits', {}).get('used', 0),
                    'credits_limit': usage.get('credits', {}).get('limit', 0),
                    'storage_used_mb': usage.get('storage', {}).get('used', 0) / (1024 * 1024),
                    'bandwidth_used_mb': usage.get('bandwidth', {}).get('used', 0) / (1024 * 1024)
                },
                'gallos_stats': {
                    'total_photos': total_photos,
                    'total_size_mb': total_bytes / (1024 * 1024),
                    'average_size_kb': (total_bytes / total_photos / 1024) if total_photos > 0 else 0
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error obteniendo estadísticas: {str(e)}"
            )
