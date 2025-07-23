from sqlalchemy.orm import Session
from app.models.profile import Profile
from app.schemas.profile import ProfileUpdate
from app.core.exceptions import NotFoundException, ValidationException

class ProfileService:
    """Servicio de perfiles"""
    
    @staticmethod
    def get_profile_by_user_id(db: Session, user_id: int) -> Profile:
        """Obtener perfil por ID de usuario"""
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            raise NotFoundException("Perfil no encontrado")
        return profile
    
    @staticmethod
    def update_profile(db: Session, user_id: int, profile_data: ProfileUpdate) -> Profile:
        """Actualizar perfil del usuario"""
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        
        if not profile:
            raise NotFoundException("Perfil no encontrado")
        
        # Actualizar solo los campos que se enviaron
        update_data = profile_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        
        return profile
    
    @staticmethod
    def update_avatar(db: Session, user_id: int, avatar_url: str) -> Profile:
        """Actualizar avatar del usuario"""
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        
        if not profile:
            raise NotFoundException("Perfil no encontrado")
        
        profile.avatar_url = avatar_url
        db.commit()
        db.refresh(profile)
        
        return profile
    
    @staticmethod
    def get_profile_with_user(db: Session, user_id: int):
        """Obtener perfil con datos de usuario"""
        result = db.query(Profile).join(Profile.user).filter(Profile.user_id == user_id).first()
        if not result:
            raise NotFoundException("Perfil no encontrado")
        return result
