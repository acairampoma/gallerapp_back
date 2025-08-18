# 🔔 ROUTER SIMPLE PARA FCM - SIN COMPLICACIONES
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import logging

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.fcm_token import FCMToken

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register-token")
async def register_fcm_token(
    token_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registrar token FCM - SIMPLE Y DIRECTO"""
    
    logger.info(f"🔔 Registrando token para usuario {current_user.id}")
    
    try:
        fcm_token = token_data.get("fcm_token")
        platform = token_data.get("platform", "android")
        device_info = token_data.get("device_info", "")
        
        if not fcm_token:
            raise HTTPException(
                status_code=400,
                detail="fcm_token es requerido"
            )
        
        # Buscar si ya existe
        existing = db.query(FCMToken).filter(
            FCMToken.fcm_token == fcm_token
        ).first()
        
        if existing:
            # Actualizar
            existing.user_id = current_user.id
            existing.platform = platform
            existing.device_info = device_info
            existing.is_active = True
            existing.updated_at = datetime.now()
            db.commit()
            
            logger.info(f"✅ Token actualizado para usuario {current_user.id}")
            return {
                "success": True,
                "message": "Token FCM actualizado",
                "token_id": existing.id
            }
        else:
            # Crear nuevo
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
            
            logger.info(f"✅ Nuevo token registrado para usuario {current_user.id}")
            return {
                "success": True,
                "message": "Token FCM registrado",
                "token_id": new_token.id
            }
            
    except Exception as e:
        logger.error(f"❌ Error registrando token: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error registrando token: {str(e)}"
        )

@router.get("/my-tokens")
async def get_my_tokens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ver mis tokens FCM registrados"""
    
    tokens = db.query(FCMToken).filter(
        FCMToken.user_id == current_user.id,
        FCMToken.is_active == True
    ).all()
    
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "tokens": [
            {
                "id": t.id,
                "token": t.fcm_token[:20] + "...",
                "platform": t.platform,
                "device_info": t.device_info,
                "created_at": t.created_at.isoformat()
            }
            for t in tokens
        ],
        "total": len(tokens)
    }