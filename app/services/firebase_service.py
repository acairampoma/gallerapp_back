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
        """Inicializar Firebase Admin SDK"""
        try:
            # Verificar si ya está inicializado
            if firebase_admin._apps:
                logger.info("✅ Firebase Admin ya inicializado")
                return
            
            # Obtener credenciales desde variables de entorno
            firebase_config = self._get_firebase_config()
            
            if firebase_config:
                # Inicializar con credenciales de las variables de entorno
                cred = credentials.Certificate(firebase_config)
                initialize_app(cred)
                logger.info("🔥 Firebase Admin SDK inicializado exitosamente desde variables de entorno")
            else:
                # Fallback: intentar desde archivo (solo desarrollo local)
                service_account_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                    'serviceAccountKey.json'
                )
                
                if os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                    initialize_app(cred)
                    logger.info("🔥 Firebase Admin SDK inicializado desde archivo local")
                else:
                    logger.warning("⚠️ No se encontraron credenciales de Firebase - continuando sin notificaciones")
                    self._is_initialized = False
                    return
                    
        except Exception as e:
            logger.error(f"❌ Error inicializando Firebase: {e}")
            # NO LANZAR ERROR - Solo loggear para que no rompa el backend
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
        # Inicializar Firebase solo cuando se use (LAZY LOADING)
        if not self._is_initialized:
            self._initialize_firebase()
            if not self._is_initialized:
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
            
            # Crear mensaje
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data={k: str(v) for k, v in message_data.items()},  # Data debe ser strings
                tokens=tokens
            )
            
            # Enviar
            response = messaging.send_multicast(message)
            
            # Procesar respuesta
            successful_tokens = []
            failed_tokens = []
            
            for idx, resp in enumerate(response.responses):
                if resp.success:
                    successful_tokens.append(tokens[idx])
                else:
                    failed_tokens.append({
                        "token": tokens[idx],
                        "error": str(resp.exception)
                    })
            
            result = {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "successful_tokens": successful_tokens,
                "failed_tokens": failed_tokens
            }
            
            logger.info(f"✅ Notificación enviada: {response.success_count}/{len(tokens)} exitosos")
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