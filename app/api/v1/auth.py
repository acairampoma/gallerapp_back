from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import (
    UserRegister, UserLogin, TokenRefresh, ChangePassword,
    LoginResponse, RegisterResponse, Token, 
    UserResponse, MessageResponse, LogoutResponse,
    ForgotPasswordRequest, VerifyResetCodeRequest, 
    ResetPasswordRequest, PasswordResetResponse,
    DeleteAccountRequest, DeleteAccountResponse,
    # 📧 Nuevos schemas de verificación
    VerifyEmailRequest, VerifyEmailResponse,
    ResendVerificationRequest, VerificationStatusResponse
)
from app.schemas.profile import ProfileResponse
from app.services.auth_service import AuthService
from app.core.security import SecurityService, get_current_user_id, verify_token_dependency, get_current_user
from app.core.config import settings
from app.core.exceptions import AuthenticationException
from app.models.user import User
from app.models.fcm_token import FCMToken
from typing import Dict, Any
from datetime import datetime, timedelta
import logging

router = APIRouter()

@router.post("/register-simple")
async def register_simple(user_data: UserRegister, db: Session = Depends(get_db)):
    """🧪 Registro simple sin email para debug"""
    try:
        # Solo registrar usuario sin email
        user = AuthService.register_user(db, user_data)
        profile = AuthService.get_user_profile(db, user.id)
        
        user_response = UserResponse.from_orm(user)
        profile_response = ProfileResponse.from_orm(profile) if profile else None
        
        return {
            "success": True,
            "message": "Registro simple exitoso",
            "user": user_response.dict(),
            "profile": profile_response.dict() if profile else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error en registro simple"
        }

@router.post("/register-debug")
async def register_debug(user_data: dict):
    """🧪 Debug endpoint para registro"""
    try:
        return {
            "status": "✅ Endpoint recibiendo datos",
            "data_received": user_data,
            "email_service_available": True,
            "message": "Si ves esto, el problema no es CORS"
        }
    except Exception as e:
        return {
            "status": "❌ Error en debug",
            "error": str(e),
            "data": user_data
        }

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """🔐 Registrar nuevo usuario con verificación de email"""
    
    # Registrar usuario con perfil
    user = AuthService.register_user(db, user_data)
    db.commit()
    db.refresh(user)
    
    # Generar código de verificación y actualizar usuario
    from app.services.email_service import email_service
    verification_code = email_service.generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    user.email_verification_code = verification_code
    user.email_verification_expires = expires_at
    user.is_verified = False
    db.commit()
    
    # Obtener perfil creado
    profile = AuthService.get_user_profile(db, user.id)
    
    # Enviar email de verificación
    user_name = profile.nombre_completo if profile else user.email.split('@')[0]
    try:
        email_result = await email_service.send_verification_email(
            email=user.email,
            name=user_name,
            verification_code=verification_code
        )
        logger.info(f"✅ Email de verificación enviado a {user.email}")
    except Exception as e:
        logger.error(f"❌ Error enviando email de verificación: {e}")
        # No fallar el registro si el email no se envía
        email_result = {"success": False, "message": str(e)}
    
    # Convertir a response schemas
    user_response = UserResponse.from_orm(user)
    profile_response = ProfileResponse.from_orm(profile) if profile else None
    
    return RegisterResponse(
        user=user_response,
        profile=profile_response,
        message=f"Usuario {user.email} registrado. Revisa tu email para verificar tu cuenta.",
        verification_required=True,
        next_step="verify_email"
    )

@router.post("/login", response_model=LoginResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """🔐 Login de usuario con verificación de email"""
    
    # Autenticar usuario
    user = AuthService.authenticate_user(db, user_data.email, user_data.password)
    
    # Verificar si el email está verificado
    if not user.is_verified:
        return LoginResponse(
            user=UserResponse.from_orm(user),
            profile=None,
            token=None,
            message="Debes verificar tu email antes de iniciar sesión. Revisa tu bandeja de entrada.",
            login_success=False,
            redirect_to="verify_email"
        )
    
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

@router.put("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePassword,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🔐 Cambiar contraseña del usuario"""
    
    # Cambiar contraseña usando el servicio
    success = AuthService.change_password(
        db, 
        current_user_id, 
        password_data.current_password, 
        password_data.new_password
    )
    
    if success:
        return MessageResponse(
            message="Contraseña cambiada exitosamente",
            success=True
        )
    else:
        return MessageResponse(
            message="Error cambiando contraseña",
            success=False
        )

@router.get("/protected-test", response_model=MessageResponse)
async def protected_test(token_data: dict = Depends(verify_token_dependency)):
    """🔒 Endpoint de prueba protegido"""
    return MessageResponse(
        message=f"¡Acceso autorizado! Token válido para usuario ID: {token_data.get('sub')}"
    )

# 🔐 ENDPOINTS DE RECUPERACIÓN DE CONTRASEÑA

@router.post("/forgot-password", response_model=PasswordResetResponse)
async def forgot_password(
    request: ForgotPasswordRequest, 
    db: Session = Depends(get_db)
):
    """🔐 Solicitar recuperación de contraseña"""
    success = AuthService.request_password_reset(db, request.email)
    
    return PasswordResetResponse(
        message="Si el email existe, recibirás un código de recuperación",
        next_step="verify_code"
    )

@router.post("/verify-reset-code", response_model=PasswordResetResponse)
async def verify_reset_code(
    request: VerifyResetCodeRequest,
    db: Session = Depends(get_db)
):
    """🔐 Verificar código de recuperación"""
    is_valid = AuthService.verify_reset_code(db, request.email, request.code)
    
    if is_valid:
        return PasswordResetResponse(
            message="Código válido. Puedes cambiar tu contraseña",
            next_step="reset_password"
        )
    else:
        return PasswordResetResponse(
            message="Código inválido o expirado",
            success=False
        )

@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """🔐 Resetear contraseña con código"""
    success = AuthService.reset_password_with_code(
        db, request.email, request.code, request.new_password
    )
    
    if success:
        return PasswordResetResponse(
            message="Contraseña cambiada exitosamente",
            next_step="login"
        )
    else:
        return PasswordResetResponse(
            message="Error al cambiar contraseña. Código inválido",
            success=False
        )

# 🗑️ ENDPOINT DE ELIMINACIÓN DE CUENTA

@router.delete("/delete-account", response_model=DeleteAccountResponse)
async def delete_account(
    delete_request: DeleteAccountRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🗑️ Eliminar cuenta de usuario permanentemente
    Apple requiere eliminación real, no solo desactivación
    
    Requiere:
    - Contraseña actual para confirmar
    - Texto de confirmación: "ELIMINAR MI CUENTA"
    """
    
    try:
        # Obtener información del usuario antes de eliminar
        user = AuthService.get_user_by_id(db, current_user_id)
        profile = AuthService.get_user_profile(db, current_user_id)
        user_email = user.email
        user_name = profile.nombre_completo if profile else user_email
        
        # Eliminar cuenta usando el servicio
        success = AuthService.delete_user_account(
            db, 
            current_user_id, 
            delete_request.password
        )
        
        if success:
            return DeleteAccountResponse(
                message=f"Cuenta de {user_name} eliminada permanentemente. Lamentamos que te vayas.",
                success=True,
                account_deleted=True,
                redirect_to="login"
            )
        
    except AuthenticationException as e:
        # Contraseña incorrecta o usuario no encontrado
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "message": str(e),
                "error_code": "AUTH_ERROR"
            }
        )
    except Exception as e:
        # Otro error  
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "message": f"Error eliminando cuenta: {str(e)}",
                "error_code": "INTERNAL_ERROR"
            }
        )

# 🔔 FCM TOKEN ENDPOINTS - DIRECTOS EN AUTH

logger = logging.getLogger(__name__)

@router.post("/register-fcm-token")
async def register_fcm_token(
    token_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """🔔 Registrar token FCM - DIRECTO EN AUTH"""
    
    logger.info(f"🔔 Registrando token FCM para usuario {current_user.id}")
    
    try:
        fcm_token = token_data.get("fcm_token")
        platform = token_data.get("platform", "android")
        device_info = token_data.get("device_info", "")
        
        if not fcm_token:
            return {
                "success": False,
                "message": "fcm_token es requerido"
            }
        
        # Buscar si ya existe este token específico
        existing_token = db.query(FCMToken).filter(
            FCMToken.fcm_token == fcm_token
        ).first()
        
        if existing_token:
            # Token ya existe, solo actualizar info
            existing_token.user_id = current_user.id
            existing_token.platform = platform
            existing_token.device_info = device_info
            existing_token.is_active = True
            existing_token.updated_at = datetime.now()
            db.commit()
            
            logger.info(f"✅ Token FCM actualizado para usuario {current_user.id}")
            return {
                "success": True,
                "message": "Token FCM actualizado exitosamente",
                "token_id": existing_token.id,
                "action": "updated"
            }
        
        # Desactivar tokens anteriores del mismo usuario + plataforma (un dispositivo por plataforma)
        db.query(FCMToken).filter(
            FCMToken.user_id == current_user.id,
            FCMToken.platform == platform
        ).update({
            "is_active": False,
            "updated_at": datetime.now()
        })
        
        # Crear nuevo token activo
        new_token = FCMToken(
            user_id=current_user.id,
            fcm_token=fcm_token,
            platform=platform,
            device_info=device_info,
            is_active=True
        )
        
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
        
        logger.info(f"✅ Nuevo token FCM registrado para usuario {current_user.id}")
        return {
            "success": True,
            "message": "Token FCM registrado exitosamente",
            "token_id": new_token.id,
            "action": "created"
        }
            
    except Exception as e:
        logger.error(f"❌ Error registrando token FCM: {e}")
        db.rollback()
        return {
            "success": False,
            "message": f"Error registrando token: {str(e)}"
        }

@router.get("/my-fcm-tokens")
async def get_my_fcm_tokens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """🔔 Ver mis tokens FCM registrados"""
    
    tokens = db.query(FCMToken).filter(
        FCMToken.user_id == current_user.id,
        FCMToken.is_active == True
    ).all()
    
    return {
        "success": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "tokens": [
            {
                "id": t.id,
                "token_preview": t.fcm_token[:20] + "...",
                "platform": t.platform,
                "device_info": t.device_info,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat()
            }
            for t in tokens
        ],
        "total_tokens": len(tokens)
    }

# 📧 ENDPOINTS DE VERIFICACIÓN DE EMAIL

@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """📧 Verificar código de email de registro"""
    try:
        # Buscar usuario por email
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            return VerifyEmailResponse(
                success=False,
                message="Email no encontrado",
                verified=False,
                next_step="register"
            )
        
        # Verificar si ya está verificado
        if user.is_verified:
            return VerifyEmailResponse(
                success=True,
                message="Email ya verificado anteriormente",
                verified=True,
                next_step="login"
            )
        
        # Verificar código y expiración
        if (user.email_verification_code != request.code or 
            user.email_verification_expires < datetime.utcnow()):
            
            # Incrementar intentos fallidos
            user.email_verification_attempts += 1
            
            # Bloquear después de 5 intentos
            if user.email_verification_attempts >= 5:
                user.email_verification_code = None
                user.email_verification_expires = None
                db.commit()
                return VerifyEmailResponse(
                    success=False,
                    message="Demasiados intentos fallidos. Solicita un nuevo código.",
                    verified=False,
                    next_step="resend"
                )
            
            db.commit()
            return VerifyEmailResponse(
                success=False,
                message=f"Código inválido o expirado. Intento {user.email_verification_attempts}/5",
                verified=False,
                next_step="verify"
            )
        
        # ✅ Verificación exitosa
        user.is_verified = True
        user.email_verification_code = None
        user.email_verification_expires = None
        user.email_verification_attempts = 0
        db.commit()
        
        logger.info(f"✅ Email verificado exitosamente: {request.email}")
        
        return VerifyEmailResponse(
            success=True,
            message="¡Email verificado exitosamente! Ya puedes iniciar sesión.",
            verified=True,
            next_step="login",
            user_data={
                "email": user.email,
                "is_verified": user.is_verified
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error verificando email: {e}")
        return VerifyEmailResponse(
            success=False,
            message="Error verificando email",
            verified=False,
            next_step="verify"
        )

@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification_email(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """📧 Reenviar código de verificación de email"""
    try:
        # Buscar usuario por email
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            return MessageResponse(
                success=False,
                message="Email no encontrado"
            )
        
        # Verificar si ya está verificado
        if user.is_verified:
            return MessageResponse(
                success=True,
                message="Este email ya está verificado"
            )
        
        # Verificar si puede reenviar (esperar 2 minutos entre intentos)
        if (user.email_verification_expires and 
            user.email_verification_expires > datetime.utcnow() and
            user.email_verification_attempts < 3):
            
            time_until_resend = (user.email_verification_expires - datetime.utcnow()).seconds
            if time_until_resend > 120:  # Más de 2 minutos
                return MessageResponse(
                    success=False,
                    message=f"Debes esperar {time_until_resend // 60} minutos para reenviar"
                )
        
        # Generar nuevo código
        from app.services.email_service import email_service
        new_code = email_service.generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        # Actualizar usuario
        user.email_verification_code = new_code
        user.email_verification_expires = expires_at
        user.email_verification_attempts = 0
        db.commit()
        
        # Obtener nombre del usuario
        profile = AuthService.get_user_profile(db, user.id)
        user_name = profile.nombre_completo if profile else user.email.split('@')[0]
        
        # Enviar email
        email_result = await email_service.send_verification_email(
            email=user.email,
            name=user_name,
            verification_code=new_code
        )
        
        if email_result.get("success"):
            logger.info(f"✅ Código de verificación reenviado a {request.email}")
            return MessageResponse(
                success=True,
                message="Nuevo código de verificación enviado a tu email"
            )
        else:
            logger.error(f"❌ Error enviando email: {email_result.get('message')}")
            return MessageResponse(
                success=False,
                message="Error enviando email. Intenta nuevamente."
            )
        
    except Exception as e:
        logger.error(f"❌ Error reenviando verificación: {e}")
        return MessageResponse(
            success=False,
            message="Error procesando solicitud"
        )

@router.get("/verification-status/{email}", response_model=VerificationStatusResponse)
async def get_verification_status(
    email: str,
    db: Session = Depends(get_db)
):
    """📧 Verificar estado de verificación de email"""
    try:
        # Buscar usuario por email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return VerificationStatusResponse(
                email=email,
                is_verified=False,
                verification_sent=False,
                can_resend=False,
                message="Email no encontrado"
            )
        
        # Estado actual
        if user.is_verified:
            return VerificationStatusResponse(
                email=email,
                is_verified=True,
                verification_sent=False,
                can_resend=False,
                message="Email ya verificado"
            )
        
        # Verificar si tiene código pendiente
        has_pending_code = (
            user.email_verification_code and 
            user.email_verification_expires and 
            user.email_verification_expires > datetime.utcnow()
        )
        
        # Puede reenviar si no tiene código o está expirado
        can_resend = not has_pending_code or user.email_verification_attempts < 3
        
        return VerificationStatusResponse(
            email=email,
            is_verified=False,
            verification_sent=has_pending_code,
            can_resend=can_resend,
            message="Email pendiente de verificación" if has_pending_code else "Esperando envío de código"
        )
        
    except Exception as e:
        logger.error(f"❌ Error verificando estado: {e}")
        return VerificationStatusResponse(
            email=email,
            is_verified=False,
            verification_sent=False,
            can_resend=False,
            message="Error verificando estado"
        )
