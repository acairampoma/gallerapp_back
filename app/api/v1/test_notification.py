# 🔥 TEST NOTIFICATION ENDPOINT - ENVÍA A TODOS LOS DISPOSITIVOS
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.database import get_db
from app.models import User, FCMToken
from app.api.dependencies import get_current_user
from app.services.firebase_service import get_firebase_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/test-broadcast", response_model=Dict[str, Any])
async def test_broadcast_notification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🚀 ENDPOINT DE PRUEBA - Envía notificación a TODOS los tokens registrados
    Solo para admins
    """
    try:
        # Verificar que sea admin
        if not current_user.es_admin:
            raise HTTPException(status_code=403, detail="Solo admins pueden enviar broadcast")
        
        # Obtener TODOS los tokens activos
        all_tokens = db.query(FCMToken).filter(
            FCMToken.is_active == True
        ).all()
        
        if not all_tokens:
            return {
                "success": False,
                "message": "No hay tokens FCM registrados",
                "sent_count": 0
            }
        
        # Obtener servicio Firebase
        firebase = get_firebase_service()
        if not firebase:
            raise HTTPException(
                status_code=500,
                detail="Firebase no está inicializado"
            )
        
        # Preparar tokens y mensaje
        tokens_list = [token.fcm_token for token in all_tokens]
        
        # Enviar a TODOS
        success_count = 0
        failed_count = 0
        
        for token in tokens_list:
            try:
                result = await firebase.send_notification(
                    token=token,
                    title="🔥 TEST BROADCAST GALLOAPP",
                    body=f"Notificación de prueba enviada por {current_user.email}",
                    data={
                        "type": "test_broadcast",
                        "admin_id": str(current_user.id),
                        "timestamp": str(datetime.now())
                    }
                )
                if result:
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error enviando a token {token[:20]}...: {e}")
                failed_count += 1
        
        return {
            "success": True,
            "message": f"Broadcast enviado",
            "total_tokens": len(tokens_list),
            "success_count": success_count,
            "failed_count": failed_count,
            "tokens_preview": [t[:20] + "..." for t in tokens_list[:3]]  # Mostrar primeros 3
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en broadcast: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error enviando broadcast: {str(e)}"
        )

@router.post("/test-single", response_model=Dict[str, Any])
async def test_single_notification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🎯 PRUEBA INDIVIDUAL - Envía notificación solo al usuario actual
    """
    try:
        # Buscar token del usuario actual
        user_token = db.query(FCMToken).filter(
            FCMToken.user_id == current_user.id,
            FCMToken.is_active == True
        ).first()
        
        if not user_token:
            # Si no tiene token, crear uno temporal para prueba
            from datetime import datetime
            temp_token = f"test_token_{current_user.id}_{datetime.now().timestamp()}"
            
            new_token = FCMToken(
                user_id=current_user.id,
                fcm_token=temp_token,
                platform="test",
                device_info="Test desde backend",
                is_active=True
            )
            db.add(new_token)
            db.commit()
            
            return {
                "success": True,
                "message": "Token temporal creado para prueba",
                "token_preview": temp_token[:30] + "..."
            }
        
        # Enviar notificación
        firebase = get_firebase_service()
        if not firebase:
            raise HTTPException(
                status_code=500,
                detail="Firebase no está inicializado"
            )
        
        result = await firebase.send_notification(
            token=user_token.fcm_token,
            title="✅ TEST INDIVIDUAL",
            body=f"Hola {current_user.email}, tu notificación funciona!",
            data={
                "type": "test_individual",
                "user_id": str(current_user.id)
            }
        )
        
        return {
            "success": True if result else False,
            "message": "Notificación enviada" if result else "Error enviando",
            "token_preview": user_token.fcm_token[:30] + "...",
            "result": str(result)
        }
        
    except Exception as e:
        logger.error(f"Error en test individual: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )

from datetime import datetime