from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime
from .profile import ProfileResponse
import re

# 🔐 VALIDADOR DE CONTRASEÑA COMPARTIDO
def validate_password_strength(password: str) -> str:
    """Validación robusta de contraseña"""
    errors = []
    
    # Longitud mínima
    if len(password) < 6:
        errors.append('debe tener al menos 6 caracteres')
    
    # Longitud máxima
    if len(password) > 128:
        errors.append('no puede tener más de 128 caracteres')
    
    # Al menos una letra
    if not re.search(r'[a-zA-Z]', password):
        errors.append('debe contener al menos una letra')
    
    # Al menos un número
    if not re.search(r'\d', password):
        errors.append('debe contener al menos un número')
    
    # No espacios en blanco
    if ' ' in password:
        errors.append('no puede contener espacios')
    
    # Contraseñas comunes prohibidas
    weak_passwords = ['123456', '654321', 'password', 'qwerty', '111111', 'abc123']
    if password.lower() in weak_passwords:
        errors.append('no puede ser una contraseña común')
    
    if errors:
        raise ValueError(f'La contraseña {', '.join(errors)}')
    
    return password

# 📝 REQUEST SCHEMAS

class UserRegister(BaseModel):
    """Schema para registro de usuario"""
    email: EmailStr
    password: str
    nombre_completo: str
    telefono: Optional[str] = None
    nombre_galpon: Optional[str] = None
    ciudad: str = "Lima"
    ubigeo: str = "150101"  # Lima por defecto

    @validator('password')
    def validate_password(cls, v):
        return validate_password_strength(v)

class UserLogin(BaseModel):
    """Schema para login de usuario"""
    email: EmailStr
    password: str

class TokenRefresh(BaseModel):
    """Schema para refresh token"""
    refresh_token: str

class ChangePassword(BaseModel):
    """Schema para cambio de contraseña"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        return validate_password_strength(v)

# 📤 RESPONSE SCHEMAS

class Token(BaseModel):
    """Schema para respuesta de token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # minutos

class UserResponse(BaseModel):
    """Schema para respuesta de usuario"""
    id: int
    email: str
    is_active: bool
    is_verified: bool
    is_premium: bool
    es_admin: bool  # 👑 NUEVO: Campo admin
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    """Schema para respuesta de login exitoso"""
    user: UserResponse
    profile: Optional[ProfileResponse] = None
    token: Optional[Token] = None
    message: str = "Login exitoso"
    login_success: bool = True
    redirect_to: str = "home"

class RegisterResponse(BaseModel):
    """Schema para respuesta de registro exitoso"""
    user: UserResponse
    profile: Optional[ProfileResponse] = None
    message: str = "Usuario registrado exitosamente"
    verification_required: bool = False
    next_step: str = "login"  # "login" o "verify_email"

class MessageResponse(BaseModel):
    """Schema para respuestas simples"""
    message: str
    success: bool = True

class LogoutResponse(BaseModel):
    """Schema para respuesta de logout"""
    message: str = "Logout exitoso"
    success: bool = True
    redirect_to: str = "login"
    clear_session: bool = True

# 🔐 ESQUEMAS PARA RECUPERACIÓN DE CONTRASEÑA
class ForgotPasswordRequest(BaseModel):
    """Schema para solicitar recuperación de contraseña"""
    email: EmailStr

class VerifyResetCodeRequest(BaseModel):
    """Schema para verificar código de recuperación"""
    email: EmailStr
    code: str
    
class ResetPasswordRequest(BaseModel):
    """Schema para resetear contraseña"""
    email: EmailStr
    code: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        return validate_password_strength(v)

class PasswordResetResponse(BaseModel):
    """Schema para respuestas de recuperación"""
    message: str
    success: bool = True
    next_step: Optional[str] = None

# 🗑️ ESQUEMAS PARA ELIMINACIÓN DE CUENTA
class DeleteAccountRequest(BaseModel):
    """Schema para solicitar eliminación de cuenta"""
    password: str
    confirmation_text: str
    
    @validator('confirmation_text')
    def validate_confirmation(cls, v):
        if v != "ELIMINAR MI CUENTA":
            raise ValueError('Debes escribir exactamente: ELIMINAR MI CUENTA')
        return v

class DeleteAccountResponse(BaseModel):
    """Schema para respuesta de eliminación de cuenta"""
    message: str = "Cuenta eliminada exitosamente"
    success: bool = True
    account_deleted: bool = True
    redirect_to: str = "login"

# 📧 ESQUEMAS PARA VERIFICACIÓN DE EMAIL
class VerifyEmailRequest(BaseModel):
    """Schema para verificar código de email"""
    email: EmailStr
    code: str
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('El código debe ser de 6 dígitos numéricos')
        return v

class VerifyEmailResponse(BaseModel):
    """Schema para respuesta de verificación de email"""
    success: bool
    message: str
    verified: bool
    next_step: str  # "login" o "register"
    user_data: Optional[Dict[str, Any]] = None

class ResendVerificationRequest(BaseModel):
    """Schema para reenviar código de verificación"""
    email: EmailStr

class VerificationStatusResponse(BaseModel):
    """Schema para verificar estado de verificación"""
    email: str
    is_verified: bool
    verification_sent: bool
    can_resend: bool
    message: str
