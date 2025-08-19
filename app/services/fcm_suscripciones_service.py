# 🔔 SERVICIO DE NOTIFICACIONES FCM PARA SUSCRIPCIONES
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from firebase_admin import messaging

from app.models.user import User
from app.models.fcm_token import FCMToken

logger = logging.getLogger(__name__)

class FCMNotificationService:
    """Servicio para enviar notificaciones FCM específicas de suscripciones"""
    
    @staticmethod
    async def notificar_nueva_suscripcion_a_admins(db: Session, usuario_email: str, plan_nombre: str):
        """
        🔔 Envía notificación a todos los admins cuando hay nueva suscripción
        """
        try:
            logger.info(f"📧 Enviando notificación de nueva suscripción: {usuario_email} -> {plan_nombre}")
            
            # Obtener todos los admins activos
            admins = db.query(User).filter(
                User.es_admin == True,
                User.is_active == True,
                User.recibe_notificaciones_admin == True
            ).all()
            
            if not admins:
                logger.warning("⚠️ No hay admins activos para notificar")
                return False
            
            # Obtener tokens FCM de los admins
            admin_ids = [admin.id for admin in admins]
            tokens_fcm = db.query(FCMToken).filter(
                FCMToken.user_id.in_(admin_ids),
                FCMToken.is_active == True
            ).all()
            
            if not tokens_fcm:
                logger.warning("⚠️ No hay tokens FCM de admins disponibles")
                return False
            
            # Preparar mensaje
            title = "🆕 Nueva Suscripción Pendiente"
            body = f"Usuario {usuario_email} solicita plan {plan_nombre}"
            
            # Enviar a cada token
            tokens_enviados = 0
            for token_obj in tokens_fcm:
                try:
                    message = messaging.Message(
                        notification=messaging.Notification(
                            title=title,
                            body=body
                        ),
                        data={
                            "tipo": "nueva_suscripcion",
                            "usuario_email": usuario_email,
                            "plan_nombre": plan_nombre,
                            "accion": "revisar_suscripciones"
                        },
                        token=token_obj.fcm_token
                    )
                    
                    # Enviar mensaje
                    response = messaging.send(message)
                    logger.info(f"✅ Notificación enviada a admin {token_obj.user_id}: {response}")
                    tokens_enviados += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error enviando a admin {token_obj.user_id}: {e}")
                    # Marcar token como inactivo si es token inválido
                    if "invalid-registration-token" in str(e) or "not-registered" in str(e):
                        token_obj.is_active = False
            
            # Guardar cambios en tokens inactivos
            db.commit()
            
            logger.info(f"📊 Notificación enviada a {tokens_enviados}/{len(tokens_fcm)} tokens de admin")
            return tokens_enviados > 0
            
        except Exception as e:
            logger.error(f"❌ Error crítico enviando notificación a admins: {e}")
            return False
    
    @staticmethod
    async def notificar_suscripcion_aprobada_a_usuario(db: Session, user_id: int, plan_nombre: str):
        """
        ✅ Envía notificación al usuario cuando su suscripción es aprobada
        """
        try:
            logger.info(f"✅ Enviando notificación de aprobación a usuario {user_id}: {plan_nombre}")
            
            # Obtener tokens FCM del usuario
            tokens_fcm = db.query(FCMToken).filter(
                FCMToken.user_id == user_id,
                FCMToken.is_active == True
            ).all()
            
            if not tokens_fcm:
                logger.warning(f"⚠️ Usuario {user_id} no tiene tokens FCM activos")
                return False
            
            # Preparar mensaje
            title = "🎉 ¡Suscripción Aprobada!"
            body = f"Tu plan {plan_nombre} ha sido activado. ¡Disfruta de todas las funciones premium!"
            
            # Enviar a cada token del usuario
            tokens_enviados = 0
            for token_obj in tokens_fcm:
                try:
                    message = messaging.Message(
                        notification=messaging.Notification(
                            title=title,
                            body=body
                        ),
                        data={
                            "tipo": "suscripcion_aprobada",
                            "plan_nombre": plan_nombre,
                            "accion": "abrir_app"
                        },
                        token=token_obj.fcm_token
                    )
                    
                    # Enviar mensaje
                    response = messaging.send(message)
                    logger.info(f"✅ Notificación de aprobación enviada a usuario {user_id}: {response}")
                    tokens_enviados += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error enviando notificación a usuario {user_id}: {e}")
                    # Marcar token como inactivo si es token inválido
                    if "invalid-registration-token" in str(e) or "not-registered" in str(e):
                        token_obj.is_active = False
            
            # Guardar cambios en tokens inactivos
            db.commit()
            
            logger.info(f"📊 Notificación de aprobación enviada a {tokens_enviados}/{len(tokens_fcm)} tokens del usuario")
            return tokens_enviados > 0
            
        except Exception as e:
            logger.error(f"❌ Error crítico enviando notificación de aprobación: {e}")
            return False
    
    @staticmethod
    async def notificar_suscripcion_rechazada_a_usuario(db: Session, user_id: int, plan_nombre: str, motivo: str):
        """
        ❌ Envía notificación al usuario cuando su suscripción es rechazada
        """
        try:
            logger.info(f"❌ Enviando notificación de rechazo a usuario {user_id}: {plan_nombre}")
            
            # Obtener tokens FCM del usuario
            tokens_fcm = db.query(FCMToken).filter(
                FCMToken.user_id == user_id,
                FCMToken.is_active == True
            ).all()
            
            if not tokens_fcm:
                logger.warning(f"⚠️ Usuario {user_id} no tiene tokens FCM activos")
                return False
            
            # Preparar mensaje
            title = "📋 Revisión de Suscripción"
            body = f"Tu solicitud de plan {plan_nombre} necesita revisión. Por favor, contacta soporte."
            
            # Enviar a cada token del usuario
            tokens_enviados = 0
            for token_obj in tokens_fcm:
                try:
                    message = messaging.Message(
                        notification=messaging.Notification(
                            title=title,
                            body=body
                        ),
                        data={
                            "tipo": "suscripcion_rechazada",
                            "plan_nombre": plan_nombre,
                            "motivo": motivo,
                            "accion": "contactar_soporte"
                        },
                        token=token_obj.fcm_token
                    )
                    
                    # Enviar mensaje
                    response = messaging.send(message)
                    logger.info(f"✅ Notificación de rechazo enviada a usuario {user_id}: {response}")
                    tokens_enviados += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error enviando notificación de rechazo a usuario {user_id}: {e}")
                    # Marcar token como inactivo si es token inválido
                    if "invalid-registration-token" in str(e) or "not-registered" in str(e):
                        token_obj.is_active = False
            
            # Guardar cambios en tokens inactivos
            db.commit()
            
            logger.info(f"📊 Notificación de rechazo enviada a {tokens_enviados}/{len(tokens_fcm)} tokens del usuario")
            return tokens_enviados > 0
            
        except Exception as e:
            logger.error(f"❌ Error crítico enviando notificación de rechazo: {e}")
            return False
