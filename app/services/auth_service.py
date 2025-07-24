from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.profile import Profile
from app.schemas.auth import UserRegister
from app.core.security import SecurityService
from app.core.exceptions import AuthenticationException, ValidationException

class AuthService:
    """Servicio de autenticación"""
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> User:
        """Registrar nuevo usuario con perfil"""
        
        # Verificar si el email ya existe
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValidationException("El email ya está registrado")
        
        # Crear usuario
        hashed_password = SecurityService.get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            is_verified=True  # Auto-verificado para desarrollo
        )
        
        db.add(db_user)
        db.flush()  # Para obtener el ID sin hacer commit
        
        # Crear perfil asociado
        db_profile = Profile(
            user_id=db_user.id,
            nombre_completo=user_data.nombre_completo,
            telefono=user_data.telefono,
            nombre_galpon=user_data.nombre_galpon,
            ciudad=user_data.ciudad,
            ubigeo=user_data.ubigeo
        )
        
        db.add(db_profile)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """Autenticar usuario"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise AuthenticationException("Credenciales inválidas")
        
        if not user.is_active:
            raise AuthenticationException("Usuario inactivo")
        
        if not SecurityService.verify_password(password, user.password_hash):
            raise AuthenticationException("Credenciales inválidas")
        
        # Actualizar último login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """Obtener usuario por ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise AuthenticationException("Usuario no encontrado")
        return user
    
    @staticmethod
    def update_refresh_token(db: Session, user_id: int, refresh_token: str):
        """Actualizar refresh token del usuario"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.refresh_token = refresh_token
            db.commit()
    
    @staticmethod
    def verify_refresh_token(db: Session, refresh_token: str) -> User:
        """Verificar refresh token"""
        user = db.query(User).filter(User.refresh_token == refresh_token).first()
        if not user:
            raise AuthenticationException("Refresh token inválido")
        return user
    
    @staticmethod
    def get_user_profile(db: Session, user_id: int) -> Profile:
        """Obtener perfil del usuario"""
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        return profile
