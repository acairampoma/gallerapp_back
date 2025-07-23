from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

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
        if len(v) < 6:
            raise ValueError('Password debe tener al menos 6 caracteres')
        return v

class UserLogin(BaseModel):
    """Schema para login de usuario"""
    email: EmailStr
    password: str

class TokenRefresh(BaseModel):
    """Schema para refresh token"""
    refresh_token: str

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
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    """Schema para respuesta de login exitoso"""
    user: UserResponse
    token: Token
    message: str = "Login exitoso"

class RegisterResponse(BaseModel):
    """Schema para respuesta de registro exitoso"""
    user: UserResponse
    message: str = "Usuario registrado exitosamente"

class MessageResponse(BaseModel):
    """Schema para respuestas simples"""
    message: str
    success: bool = True
