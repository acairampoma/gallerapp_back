# 🔥🔔 FIREBASE ADMIN SDK SERVICE - GALLOAPP BACKEND
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from firebase_admin import credentials, messaging, initialize_app
import firebase_admin
from pydantic import BaseModel

# Configurar logging
logger = logging.getLogger(__name__)

class NotificationData(BaseModel):
    """Modelo para datos de notificación"""
    title: str
    body: str
    data: Dict[str, Any] = {}
    tokens: List[str] = []
    topic: Optional[str] = None

class FirebaseService:
    """Servicio para enviar notificaciones push con Firebase Admin SDK"""
    
    _instance = None
    _is_initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Intentar inicializar al crear la instancia
        if not self._is_initialized:
            try:
                self._initialize_firebase()
            except Exception as e:
                logger.warning(f"⚠️ Firebase no se pudo inicializar al arrancar: {e}")
                self._is_initialized = False
    
    def _initialize_firebase(self):
        """Inicializar Firebase Admin SDK - USANDO LA LÓGICA QUE FUNCIONA"""
        try:
            # Verificar si ya está inicializado
            if firebase_admin._apps:
                logger.info("✅ Firebase Admin ya inicializado")
                self._is_initialized = True
                return
            
            # USAR LA MISMA LÓGICA QUE FUNCIONA EN test_endpoint.py
            project_id = os.getenv('FIREBASE_PROJECT_ID')
            private_key = os.getenv('FIREBASE_PRIVATE_KEY')
            client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
            
            if not all([project_id, private_key, client_email]):
                logger.error("❌ Faltan variables de Firebase")
                self._is_initialized = False
                return
            
            # Fix private key
            private_key = private_key.replace('\\n', '\n')
            
            # Crear credenciales
            cred_dict = {
                "type": "service_account",
                "project_id": project_id,
                "private_key": private_key,
                "client_email": client_email,
                "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', 'default'),
                "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            }
            
            # Inicializar
            cred = credentials.Certificate(cred_dict)
            initialize_app(cred)
            
            logger.info("🔥 Firebase Admin SDK inicializado exitosamente con lógica corregida")
            self._is_initialized = True
                    
        except Exception as e:
            logger.error(f"❌ Error inicializando Firebase: {e}")
            self._is_initialized = False
    
    def _get_firebase_config(self) -> Optional[Dict[str, Any]]:
        """Obtener configuración de Firebase desde variables de entorno"""
        try:
            from decouple import config
            
            # Intentar obtener las variables de entorno
            project_id = config('FIREBASE_PROJECT_ID', default=None)
            private_key = config('FIREBASE_PRIVATE_KEY', default=None)
            client_email = config('FIREBASE_CLIENT_EMAIL', default=None)
            client_id = config('FIREBASE_CLIENT_ID', default=None)
            private_key_id = config('FIREBASE_PRIVATE_KEY_ID', default=None)
            
            if all([project_id, private_key, client_email]):
                # Convertir la private_key (puede venir con \\n literal) - PROBLEMA MÁS COMÚN
                private_key = private_key.replace('\\n', '\n')
                
                # Verificar que la clave privada tenga el formato correcto
                if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
                    logger.error("❌ FIREBASE_PRIVATE_KEY mal formateada")
                    return None
                
                firebase_config = {
                    "type": "service_account",
                    "project_id": project_id,
                    "private_key_id": private_key_id or "default",
                    "private_key": private_key,
                    "client_email": client_email,
                    "client_id": client_id or "",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}",
                    "universe_domain": "googleapis.com"
                }
                
                logger.info("✅ Configuración Firebase obtenida desde variables de entorno")
                return firebase_config
            else:
                logger.warning("⚠️ Variables de entorno Firebase incompletas")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo config Firebase: {e}")
            return None
    
    async def send_notification_to_tokens(
        self, 
        tokens: List[str], 
        title: str, 
        body: str, 
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Enviar notificación a tokens específicos
        
        Args:
            tokens: Lista de FCM tokens
            title: Título de la notificación
            body: Cuerpo de la notificación
            data: Datos adicionales (opcional)
        
        Returns:
            Resultado del envío
        """
        # FORZAR RE-INICIALIZACIÓN PARA ASEGURAR QUE FUNCIONE
        try:
            self._initialize_firebase()
        except Exception as e:
            logger.error(f"❌ Error en re-inicialización: {e}")
            
        if not self._is_initialized:
            logger.error("❌ Firebase NO está disponible después de intentar inicializar")
            return {"success": False, "error": "Firebase no disponible"}
        
        try:
            if not tokens:
                return {"success": False, "error": "No tokens provided"}
            
            # Preparar el mensaje
            message_data = data or {}
            message_data.update({
                "timestamp": datetime.now().isoformat(),
                "source": "galloapp_backend"
            })
            
            # Enviar notificaciones una por una (más compatible)
            successful_tokens = []
            failed_tokens = []
            
            for token in tokens:
                try:
                    # Crear mensaje individual
                    message = messaging.Message(
                        notification=messaging.Notification(
                            title=title,
                            body=body
                        ),
                        data={k: str(v) for k, v in message_data.items()},  # Data debe ser strings
                        token=token
                    )
                    
                    # Enviar individual
                    response = messaging.send(message)
                    successful_tokens.append(token)
                    logger.info(f"✅ Notificación enviada exitosamente a token: {token[:20]}...")
                    
                except Exception as token_error:
                    failed_tokens.append({
                        "token": token,
                        "error": str(token_error)
                    })
                    logger.error(f"❌ Error enviando a token {token[:20]}...: {token_error}")
            
            result = {
                "success": len(successful_tokens) > 0,
                "success_count": len(successful_tokens),
                "failure_count": len(failed_tokens),
                "successful_tokens": successful_tokens,
                "failed_tokens": failed_tokens
            }
            
            logger.info(f"✅ Notificación enviada: {len(successful_tokens)}/{len(tokens)} exitosos")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error enviando notificación: {e}")
            return {
                "success": False,
                "error": str(e),
                "success_count": 0,
                "failure_count": len(tokens) if tokens else 0
            }
    
    async def send_notification_to_topic(
        self, 
        topic: str, 
        title: str, 
        body: str, 
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Enviar notificación a un topic
        
        Args:
            topic: Nombre del topic
            title: Título de la notificación
            body: Cuerpo de la notificación
            data: Datos adicionales (opcional)
        
        Returns:
            Resultado del envío
        """
        try:
            # Preparar datos
            message_data = data or {}
            message_data.update({
                "timestamp": datetime.now().isoformat(),
                "source": "galloapp_backend"
            })
            
            # Crear mensaje
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data={k: str(v) for k, v in message_data.items()},
                topic=topic
            )
            
            # Enviar
            response = messaging.send(message)
            
            logger.info(f"✅ Notificación enviada al topic '{topic}': {response}")
            return {
                "success": True,
                "message_id": response,
                "topic": topic
            }
            
        except Exception as e:
            logger.error(f"❌ Error enviando notificación al topic '{topic}': {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic
            }
    
    async def notify_admin_new_subscription(
        self,
        admin_tokens: List[str],
        user_name: str,
        user_email: str,
        plan_name: str,
        amount: float
    ) -> Dict[str, Any]:
        """
        Notificar a administradores sobre nueva suscripción
        """
        title = "💰 Nueva Suscripción"
        body = f"{user_name} se suscribió al plan {plan_name} por S/.{amount:.2f}"
        
        data = {
            "type": "new_subscription",
            "user_name": user_name,
            "user_email": user_email,
            "plan_name": plan_name,
            "amount": str(amount),
            "category": "admin_alerts"
        }
        
        return await self.send_notification_to_tokens(
            tokens=admin_tokens,
            title=title,
            body=body,
            data=data
        )
    
    async def notify_user_subscription_approved(
        self,
        user_tokens: List[str],
        plan_name: str
    ) -> Dict[str, Any]:
        """
        Notificar a usuario que su suscripción fue aprobada
        """
        title = "✅ Suscripción Activada"
        body = f"Tu suscripción al plan {plan_name} ha sido activada exitosamente"
        
        data = {
            "type": "subscription_approved",
            "plan_name": plan_name,
            "category": "user_subscriptions"
        }
        
        return await self.send_notification_to_tokens(
            tokens=user_tokens,
            title=title,
            body=body,
            data=data
        )
    
    @staticmethod
    def get_instance():
        """Obtener instancia singleton"""
        return FirebaseService()

# Instancia global
firebase_service = FirebaseService.get_instance()