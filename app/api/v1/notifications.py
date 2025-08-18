# 🔔 ENDPOINTS DE NOTIFICACIONES FIREBASE - GALLOAPP
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime
import logging

from app.database import get_db
from app.models.user import User
from app.models.fcm_token import FCMToken
from app.core.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

def get_firebase_service():
    """Obtener servicio Firebase de forma lazy"""
    try:
        from app.services.firebase_service import firebase_service
        return firebase_service
    except Exception as e:
        logger.error(f"❌ Error cargando Firebase: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de notificaciones no disponible"
        )

# ==========================================
# 📊 MODELOS PYDANTIC
# ==========================================

class FCMTokenRequest(BaseModel):
    """Modelo para registrar token FCM"""
    fcm_token: str
    platform: str  # android, ios, web
    device_info: str = None

class NotificationRequest(BaseModel):
    """Modelo para enviar notificación"""
    title: str
    body: str
    data: Dict[str, Any] = {}
    user_ids: List[int] = []
    send_to_admins: bool = False

class SubscriptionNotificationRequest(BaseModel):
    """Modelo para notificación de suscripción"""
    user_name: str
    user_email: EmailStr
    plan_name: str
    amount: float

# ==========================================
# 🔔 ENDPOINTS DE TOKENS FCM
# ==========================================

@router.post("/register-fcm-token", response_model=Dict[str, Any])
async def register_fcm_token(
    token_request: FCMTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Registrar o actualizar token FCM de un usuario
    """
    try:
        # Buscar si ya existe el token
        existing_token = db.query(FCMToken).filter(
            FCMToken.fcm_token == token_request.fcm_token
        ).first()
        
        if existing_token:
            # Actualizar token existente
            existing_token.user_id = current_user.id
            existing_token.platform = token_request.platform
            existing_token.device_info = token_request.device_info
            existing_token.is_active = True
            existing_token.updated_at = datetime.now()
            db.commit()
            
            logger.info(f"✅ Token FCM actualizado para usuario {current_user.id}")
            return {
                "success": True,
                "message": "Token FCM actualizado exitosamente",
                "token_id": existing_token.id
            }
        else:
            # Crear nuevo token
            new_token = FCMToken(
                user_id=current_user.id,
                fcm_token=token_request.fcm_token,
                platform=token_request.platform,
                device_info=token_request.device_info,
                is_active=True
            )
            
            db.add(new_token)
            db.commit()
            db.refresh(new_token)
            
            logger.info(f"✅ Nuevo token FCM registrado para usuario {current_user.id}")
            return {
                "success": True,
                "message": "Token FCM registrado exitosamente",
                "token_id": new_token.id
            }
            
    except Exception as e:
        logger.error(f"❌ Error registrando token FCM: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registrando token FCM: {str(e)}"
        )

@router.get("/my-fcm-tokens", response_model=List[Dict[str, Any]])
async def get_my_fcm_tokens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener tokens FCM del usuario actual
    """
    try:
        tokens = db.query(FCMToken).filter(
            FCMToken.user_id == current_user.id,
            FCMToken.is_active == True
        ).all()
        
        return [
            {
                "id": token.id,
                "platform": token.platform,
                "device_info": token.device_info,
                "created_at": token.created_at.isoformat(),
                "updated_at": token.updated_at.isoformat()
            }
            for token in tokens
        ]
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo tokens FCM: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo tokens FCM: {str(e)}"
        )

# ==========================================
# 📤 ENDPOINTS DE ENVÍO DE NOTIFICACIONES
# ==========================================

@router.post("/send-notification", response_model=Dict[str, Any])
async def send_notification(
    notification: NotificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enviar notificación push (solo para admins)
    """
    try:
        # Verificar que el usuario sea admin
        if not current_user.es_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden enviar notificaciones"
            )
        
        tokens_to_send = []
        
        if notification.send_to_admins:
            # Enviar a todos los admins
            admin_tokens = db.query(FCMToken).join(User).filter(
                User.es_admin == True,
                FCMToken.is_active == True
            ).all()
            tokens_to_send.extend([token.fcm_token for token in admin_tokens])
            
        if notification.user_ids:
            # Enviar a usuarios específicos
            user_tokens = db.query(FCMToken).filter(
                FCMToken.user_id.in_(notification.user_ids),
                FCMToken.is_active == True
            ).all()
            tokens_to_send.extend([token.fcm_token for token in user_tokens])
        
        if not tokens_to_send:
            return {
                "success": False,
                "message": "No se encontraron tokens para enviar",
                "sent_count": 0
            }
        
        # Enviar notificación
        firebase = get_firebase_service()
        result = await firebase.send_notification_to_tokens(
            tokens=tokens_to_send,
            title=notification.title,
            body=notification.body,
            data=notification.data
        )
        
        return {
            "success": result["success"],
            "sent_count": result.get("success_count", 0),
            "failed_count": result.get("failure_count", 0),
            "message": f"Notificación enviada a {result.get('success_count', 0)} dispositivos"
        }
        
    except Exception as e:
        logger.error(f"❌ Error enviando notificación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando notificación: {str(e)}"
        )

@router.post("/notify-admin-subscription", response_model=Dict[str, Any])
async def notify_admin_new_subscription(
    subscription_data: SubscriptionNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Notificar a administradores sobre nueva suscripción
    """
    try:
        # Obtener tokens de todos los administradores
        admin_tokens_query = db.query(FCMToken).join(User).filter(
            User.es_admin == True,
            FCMToken.is_active == True
        ).all()
        
        admin_tokens = [token.fcm_token for token in admin_tokens_query]
        
        if not admin_tokens:
            logger.warning("⚠️ No se encontraron tokens de administradores")
            return {
                "success": False,
                "message": "No hay administradores con tokens FCM disponibles",
                "sent_count": 0
            }
        
        # Enviar notificación usando el servicio Firebase
        result = await firebase_service.notify_admin_new_subscription(
            admin_tokens=admin_tokens,
            user_name=subscription_data.user_name,
            user_email=subscription_data.user_email,
            plan_name=subscription_data.plan_name,
            amount=subscription_data.amount
        )
        
        logger.info(f"✅ Notificación de suscripción enviada a {result.get('success_count', 0)} admins")
        
        return {
            "success": result["success"],
            "sent_count": result.get("success_count", 0),
            "failed_count": result.get("failure_count", 0),
            "message": f"Notificación enviada a {result.get('success_count', 0)} administradores"
        }
        
    except Exception as e:
        logger.error(f"❌ Error notificando suscripción a admins: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando notificación a administradores: {str(e)}"
        )

@router.post("/notify-user-approved", response_model=Dict[str, Any])
async def notify_user_subscription_approved(
    user_id: int,
    plan_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Notificar a usuario que su suscripción fue aprobada (solo admins)
    """
    try:
        # Verificar que el usuario sea admin
        if not current_user.es_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden aprobar suscripciones"
            )
        
        # Obtener tokens del usuario específico
        user_tokens_query = db.query(FCMToken).filter(
            FCMToken.user_id == user_id,
            FCMToken.is_active == True
        ).all()
        
        user_tokens = [token.fcm_token for token in user_tokens_query]
        
        if not user_tokens:
            return {
                "success": False,
                "message": f"Usuario {user_id} no tiene tokens FCM disponibles",
                "sent_count": 0
            }
        
        # Enviar notificación
        result = await firebase_service.notify_user_subscription_approved(
            user_tokens=user_tokens,
            plan_name=plan_name
        )
        
        logger.info(f"✅ Notificación de aprobación enviada al usuario {user_id}")
        
        return {
            "success": result["success"],
            "sent_count": result.get("success_count", 0),
            "failed_count": result.get("failure_count", 0),
            "message": f"Notificación enviada al usuario {user_id}"
        }
        
    except Exception as e:
        logger.error(f"❌ Error notificando aprobación a usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando notificación al usuario: {str(e)}"
        )

# ==========================================
# 🧪 ENDPOINT DE PRUEBA
# ==========================================

@router.post("/test-notification", response_model=Dict[str, Any])
async def test_notification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enviar notificación de prueba al usuario actual
    """
    try:
        # Obtener tokens del usuario actual
        user_tokens = db.query(FCMToken).filter(
            FCMToken.user_id == current_user.id,
            FCMToken.is_active == True
        ).all()
        
        if not user_tokens:
            return {
                "success": False,
                "message": "No tienes tokens FCM registrados",
                "sent_count": 0
            }
        
        tokens = [token.fcm_token for token in user_tokens]
        
        # Enviar notificación de prueba
        result = await firebase_service.send_notification_to_tokens(
            tokens=tokens,
            title="🔥 Prueba GalloApp",
            body=f"¡Hola {current_user.email}! Las notificaciones funcionan perfectamente 🐓",
            data={
                "type": "test_notification",
                "user_id": str(current_user.id),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return {
            "success": result["success"],
            "sent_count": result.get("success_count", 0),
            "failed_count": result.get("failure_count", 0),
            "message": "Notificación de prueba enviada"
        }
        
    except Exception as e:
        logger.error(f"❌ Error enviando notificación de prueba: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando notificación de prueba: {str(e)}"
        )