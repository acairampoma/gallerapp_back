from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.profile import ProfileResponse, ProfileUpdate, AvatarUpload, ProfileWithUser
from app.schemas.auth import MessageResponse
from app.services.profile_service import ProfileService
from app.core.security import get_current_user_id
from app.services.imagekit_service import imagekit_service
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """👤 Obtener mi perfil"""
    
    profile = ProfileService.get_profile_by_user_id(db, current_user_id)
    return ProfileResponse.from_orm(profile)

@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """✏️ Actualizar mi perfil"""
    
    profile = ProfileService.update_profile(db, current_user_id, profile_data)
    return ProfileResponse.from_orm(profile)

@router.post("/avatar", response_model=ProfileResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📸 Subir avatar del usuario"""
    
    try:
        logger.info(f"📸 Usuario {current_user_id} subiendo avatar")
        
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Subir a ImageKit con transformaciones (200x200, crop force, webp)
        upload_result = imagekit_service.upload_image_with_transformations(
            file_content=file_content,
            file_name=f"avatar_user_{current_user_id}_{file.filename}",
            folder="galloapp/avatars",
            width=200,
            height=200,
            crop="force",
            quality=90,
            format="webp"
        )
        
        if not upload_result:
            raise Exception("ImageKit no retornó resultado de upload")
        
        # Actualizar avatar en perfil
        avatar_url = upload_result["url"]
        profile = ProfileService.update_avatar(db, current_user_id, avatar_url)
        
        logger.info(f"✅ Avatar actualizado para usuario {current_user_id}")
        return ProfileResponse.from_orm(profile)
        
    except Exception as e:
        logger.error(f"❌ Error subiendo avatar: {e}")
        from app.core.exceptions import ValidationException
        raise ValidationException(f"Error subiendo avatar: {str(e)}")

@router.get("/me/complete", response_model=ProfileWithUser)
async def get_complete_profile(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Obtener perfil completo con datos de usuario"""
    
    profile = ProfileService.get_profile_with_user(db, current_user_id)
    
    # Construir respuesta manual porque es join
    return {
        "id": profile.user.id,
        "email": profile.user.email,
        "is_premium": profile.user.is_premium,
        "profile": ProfileResponse.from_orm(profile)
    }

@router.delete("/avatar", response_model=MessageResponse)
async def remove_avatar(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🗑️ Eliminar avatar del usuario"""
    
    # Remover avatar (poner None)
    ProfileService.update_avatar(db, current_user_id, None)
    
    return MessageResponse(message="Avatar eliminado exitosamente")
