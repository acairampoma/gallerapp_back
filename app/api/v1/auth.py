from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import (
    UserRegister, UserLogin, TokenRefresh, 
    LoginResponse, RegisterResponse, Token, 
    UserResponse, MessageResponse, LogoutResponse
)
from app.schemas.profile import ProfileResponse
from app.services.auth_service import AuthService
from app.core.security import SecurityService, get_current_user_id, verify_token_dependency
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """🔐 Registrar nuevo usuario con respuesta mejorada"""
    
    # Registrar usuario con perfil
    user = AuthService.register_user(db, user_data)
    
    # Obtener perfil creado
    profile = AuthService.get_user_profile(db, user.id)
    
    # Convertir a response schemas
    user_response = UserResponse.from_orm(user)
    profile_response = ProfileResponse.from_orm(profile) if profile else None
    
    return RegisterResponse(
        user=user_response,
        profile=profile_response,
        message=f"Usuario {user.email} registrado exitosamente",
        login_credentials={
            "email": user.email,
            "suggested_login": True,
            "message": "Credenciales listas para login automático"
        },
        redirect_to="login"
    )

@router.post("/login", response_model=LoginResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """🔐 Login de usuario con respuesta mejorada"""
    
    # Autenticar usuario
    user = AuthService.authenticate_user(db, user_data.email, user_data.password)
    
    # Crear tokens JWT
    access_token = SecurityService.create_access_token(data={"sub": str(user.id)})
    refresh_token = SecurityService.create_refresh_token(data={"sub": str(user.id)})
    
    # Guardar refresh token en BD
    AuthService.update_refresh_token(db, user.id, refresh_token)
    
    # Cargar perfil del usuario
    profile = AuthService.get_user_profile(db, user.id)
    
    # Crear responses
    token_response = Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    user_response = UserResponse.from_orm(user)
    profile_response = ProfileResponse.from_orm(profile) if profile else None
    
    return LoginResponse(
        user=user_response,
        profile=profile_response,
        token=token_response,
        message=f"Bienvenido {profile.nombre_completo if profile else user.email}",
        login_success=True,
        redirect_to="home"
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """🔄 Renovar access token"""
    
    # Verificar refresh token
    payload = SecurityService.verify_token(token_data.refresh_token, "refresh")
    user_id = int(payload.get("sub"))
    
    # Verificar que el refresh token esté en BD
    user = AuthService.verify_refresh_token(db, token_data.refresh_token)
    
    # Crear nuevo access token
    access_token = SecurityService.create_access_token(data={"sub": str(user_id)})
    
    return Token(
        access_token=access_token,
        refresh_token=token_data.refresh_token,  # Mantener el mismo refresh token
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user_id: int = Depends(get_current_user_id), 
    db: Session = Depends(get_db)
):
    """👤 Obtener información del usuario actual"""
    
    user = AuthService.get_user_by_id(db, current_user_id)
    return UserResponse.from_orm(user)

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🚪 Logout del usuario con respuesta mejorada"""
    
    # Obtener info del usuario para el mensaje personalizado
    user = AuthService.get_user_by_id(db, current_user_id)
    profile = AuthService.get_user_profile(db, current_user_id)
    
    # Limpiar refresh token de la BD
    AuthService.update_refresh_token(db, current_user_id, None)
    
    nombre_usuario = profile.nombre_completo if profile else user.email
    
    return LogoutResponse(
        message=f"Hasta luego, {nombre_usuario}. Sesión cerrada exitosamente",
        success=True,
        redirect_to="login",
        clear_session=True
    )

@router.get("/protected-test", response_model=MessageResponse)
async def protected_test(token_data: dict = Depends(verify_token_dependency)):
    """🔒 Endpoint de prueba protegido"""
    return MessageResponse(
        message=f"¡Acceso autorizado! Token válido para usuario ID: {token_data.get('sub')}"
    )
