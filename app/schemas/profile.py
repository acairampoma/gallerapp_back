from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, date

# 📝 REQUEST SCHEMAS

class ProfileUpdate(BaseModel):
    """Schema para actualizar perfil"""
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    nombre_galpon: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    ubigeo: Optional[str] = None
    pais: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    biografia: Optional[str] = None

    @validator('telefono')
    def validate_telefono(cls, v):
        if v and len(v) < 9:
            raise ValueError('Teléfono debe tener al menos 9 dígitos')
        return v

class AvatarUpload(BaseModel):
    """Schema para upload de avatar"""
    avatar_url: str

# 📤 RESPONSE SCHEMAS

class ProfileResponse(BaseModel):
    """Schema para respuesta de perfil"""
    id: int
    user_id: int
    nombre_completo: str
    telefono: Optional[str]
    nombre_galpon: Optional[str]
    direccion: Optional[str]
    ciudad: Optional[str]
    ubigeo: Optional[str]
    pais: Optional[str]
    avatar_url: Optional[str]
    fecha_nacimiento: Optional[date]
    biografia: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProfileWithUser(BaseModel):
    """Schema para perfil con datos de usuario"""
    id: int
    email: str
    is_premium: bool
    profile: Optional[ProfileResponse]

    class Config:
        from_attributes = True
