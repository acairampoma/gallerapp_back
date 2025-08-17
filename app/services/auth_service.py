from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import random
import string
from app.models.user import User
from app.models.profile import Profile
from app.models.password_reset_token import PasswordResetToken
from app.schemas.auth import UserRegister
from app.core.security import SecurityService
from app.core.exceptions import AuthenticationException, ValidationException
from app.services.email_service import email_service

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
    
    @staticmethod
    def change_password(db: Session, user_id: int, current_password: str, new_password: str) -> bool:
        """Cambiar contraseña del usuario"""
        
        # Obtener usuario
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise AuthenticationException("Usuario no encontrado")
        
        # Verificar contraseña actual
        if not SecurityService.verify_password(current_password, user.password_hash):
            raise AuthenticationException("Contraseña actual incorrecta")
        
        # Hashear nueva contraseña y actualizar
        user.password_hash = SecurityService.get_password_hash(new_password)
        db.commit()
        
        return True
    
    # 🔐 MÉTODOS PARA RECUPERACIÓN DE CONTRASEÑA
    
    @staticmethod
    def generate_reset_code() -> str:
        """Generar código de 6 dígitos"""
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def request_password_reset(db: Session, email: str) -> bool:
        """Solicitar recuperación de contraseña"""
        
        # Buscar usuario por email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Por seguridad, no revelamos si el email existe
            return True
        
        # Generar código y fecha de expiración (15 minutos)
        code = AuthService.generate_reset_code()
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        # Invalidar tokens anteriores del usuario
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False
        ).update({"used": True})
        
        # Crear nuevo token
        reset_token = PasswordResetToken(
            user_id=user.id,
            email=user.email,
            token=code,
            expires_at=expires_at
        )
        
        db.add(reset_token)
        db.commit()
        
        # Obtener nombre del usuario para personalizar email
        profile = AuthService.get_user_profile(db, user.id)
        user_name = profile.nombre_completo if profile else None
        
        # Enviar email con el código
        email_sent = email_service.send_password_reset_code(
            to_email=user.email,
            code=code,
            user_name=user_name
        )
        
        if email_sent:
            print(f"✅ Email de recuperación enviado a {email}")
        else:
            print(f"❌ Error enviando email a {email}, pero código generado: {code}")
        
        return True
    
    @staticmethod
    def verify_reset_code(db: Session, email: str, code: str) -> bool:
        """Verificar código de recuperación"""
        
        token = db.query(PasswordResetToken).filter(
            PasswordResetToken.email == email,
            PasswordResetToken.token == code,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        
        return token is not None
    
    @staticmethod
    def reset_password_with_code(db: Session, email: str, code: str, new_password: str) -> bool:
        """Resetear contraseña usando código de verificación"""
        
        # Verificar código válido
        token = db.query(PasswordResetToken).filter(
            PasswordResetToken.email == email,
            PasswordResetToken.token == code,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        
        if not token:
            return False
        
        # Obtener usuario
        user = db.query(User).filter(User.id == token.user_id).first()
        if not user:
            return False
        
        # Actualizar contraseña
        user.password_hash = SecurityService.get_password_hash(new_password)
        
        # Marcar token como usado
        token.used = True
        
        # Invalidar todos los refresh tokens del usuario (forzar re-login)
        user.refresh_token = None
        
        db.commit()
        
        return True
