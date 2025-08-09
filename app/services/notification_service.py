# 🔔 Servicio de Notificaciones Push - Admin System
import logging
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

# Para notificaciones push reales, usar:
# - FCM (Firebase Cloud Messaging) para Flutter
# - SendGrid/Mailgun para email
# - Twilio para SMS
# - WebSockets para notificaciones en tiempo real

logger = logging.getLogger(__name__)

class NotificationService:
    """Servicio para enviar notificaciones push a administradores"""
    
    def __init__(self):
        self.fcm_enabled = False  # Configurar en producción
        self.email_enabled = False  # Configurar en producción
        self.websocket_enabled = False  # Para tiempo real
    
    # ========================================
    # NOTIFICACIONES PUSH FCM
    # ========================================
    
    async def enviar_push_admin(
        self,
        admin_emails: List[str],
        titulo: str,
        mensaje: str,
        data: Optional[Dict] = None,
        prioridad: str = "normal"
    ) -> bool:
        """
        Envía notificación push a administradores via FCM
        
        En producción, integrar con Firebase Cloud Messaging:
        - Configurar firebase-admin-python
        - Obtener tokens FCM de dispositivos admin
        - Enviar mensajes por lotes
        """
        try:
            if not self.fcm_enabled:
                logger.info(f"📱 [DEMO] Push notification: {titulo} -> {admin_emails}")
                logger.info(f"📱 [DEMO] Mensaje: {mensaje}")
                if data:
                    logger.info(f"📱 [DEMO] Data: {json.dumps(data, indent=2)}")
                return True
            
            # TODO: Implementar FCM real
            # from firebase_admin import messaging
            # 
            # # Construir mensaje
            # message = messaging.MulticastMessage(
            #     notification=messaging.Notification(
            #         title=titulo,
            #         body=mensaje
            #     ),
            #     data=data or {},
            #     tokens=admin_fcm_tokens,  # Obtener de BD
            #     android=messaging.AndroidConfig(
            #         priority='high' if prioridad == 'alta' else 'normal'
            #     ),
            #     apns=messaging.APNSConfig(
            #         payload=messaging.APNSPayload(
            #             aps=messaging.Aps(
            #                 alert=messaging.ApsAlert(
            #                     title=titulo,
            #                     body=mensaje
            #                 ),
            #                 sound='default'
            #             )
            #         )
            #     )
            # )
            # 
            # response = messaging.send_multicast(message)
            # logger.info(f"FCM enviado: {response.success_count}/{len(admin_fcm_tokens)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando push notification: {e}")
            return False
    
    # ========================================
    # NOTIFICACIONES EMAIL
    # ========================================
    
    async def enviar_email_admin(
        self,
        admin_emails: List[str],
        asunto: str,
        mensaje: str,
        html_content: Optional[str] = None
    ) -> bool:
        """
        Envía email a administradores
        
        En producción, integrar con SendGrid/Mailgun:
        """
        try:
            if not self.email_enabled:
                logger.info(f"📧 [DEMO] Email: {asunto} -> {admin_emails}")
                logger.info(f"📧 [DEMO] Mensaje: {mensaje}")
                return True
            
            # TODO: Implementar email real
            # import sendgrid
            # from sendgrid.helpers.mail import Mail
            # 
            # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            # 
            # for email in admin_emails:
            #     message = Mail(
            #         from_email='noreply@galloapp.com',
            #         to_emails=email,
            #         subject=asunto,
            #         plain_text_content=mensaje,
            #         html_content=html_content
            #     )
            #     
            #     response = sg.send(message)
            #     logger.info(f"Email enviado a {email}: {response.status_code}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    # ========================================
    # WEBSOCKET TIEMPO REAL
    # ========================================
    
    async def enviar_websocket_admin(
        self,
        mensaje_tipo: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Envía notificación en tiempo real via WebSocket
        
        Para implementar en producción:
        - FastAPI WebSocket endpoints
        - Redis pub/sub para escalabilidad
        - Conectar Flutter con WebSocket
        """
        try:
            if not self.websocket_enabled:
                logger.info(f"🔄 [DEMO] WebSocket: {mensaje_tipo}")
                logger.info(f"🔄 [DEMO] Data: {json.dumps(data, indent=2)}")
                return True
            
            # TODO: Implementar WebSocket real
            # websocket_data = {
            #     "type": mensaje_tipo,
            #     "data": data,
            #     "timestamp": datetime.utcnow().isoformat(),
            #     "target": "admins"
            # }
            # 
            # # Enviar a todos los administradores conectados
            # await websocket_manager.broadcast_to_admins(websocket_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando WebSocket: {e}")
            return False

# ========================================
# TEMPLATES DE NOTIFICACIONES
# ========================================

class NotificationTemplates:
    """Templates para diferentes tipos de notificaciones"""
    
    @staticmethod
    def nuevo_pago_pendiente(user_email: str, monto: float, plan: str) -> Dict[str, str]:
        return {
            "titulo": "🔔 Nuevo Pago Pendiente",
            "mensaje": f"Usuario {user_email} solicita verificar pago de S/.{monto} para plan {plan}",
            "email_asunto": "Gallo App - Nuevo Pago para Verificar",
            "email_html": f"""
            <h2>🐓 Gallo App - Nuevo Pago Pendiente</h2>
            <p><strong>Usuario:</strong> {user_email}</p>
            <p><strong>Plan:</strong> {plan}</p>
            <p><strong>Monto:</strong> S/.{monto}</p>
            <p><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <hr>
            <p>Accede al panel admin para verificar el pago.</p>
            <a href="https://tu-app.com/admin" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Ver Panel Admin
            </a>
            """
        }
    
    @staticmethod
    def pago_vencido(cantidad_pagos: int, horas_vencidas: int) -> Dict[str, str]:
        return {
            "titulo": "⚠️ Pagos Vencidos",
            "mensaje": f"{cantidad_pagos} pagos llevan más de {horas_vencidas} horas sin verificar",
            "email_asunto": "Gallo App - Pagos Vencidos Requieren Atención",
            "email_html": f"""
            <h2>⚠️ Pagos Vencidos - Atención Requerida</h2>
            <p>Hay <strong>{cantidad_pagos} pagos</strong> que llevan más de {horas_vencidas} horas sin verificar.</p>
            <p>Los usuarios están esperando la activación de sus planes premium.</p>
            <hr>
            <a href="https://tu-app.com/admin/pagos" style="background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Verificar Pagos Ahora
            </a>
            """
        }
    
    @staticmethod
    def nuevo_usuario_registrado(user_email: str) -> Dict[str, str]:
        return {
            "titulo": "👤 Nuevo Usuario",
            "mensaje": f"Nuevo registro: {user_email}",
            "email_asunto": "Gallo App - Nuevo Usuario Registrado",
            "email_html": f"""
            <h2>👤 Nuevo Usuario Registrado</h2>
            <p><strong>Email:</strong> {user_email}</p>
            <p><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <p>El usuario ha sido registrado con plan gratuito automáticamente.</p>
            """
        }
    
    @staticmethod
    def limite_alcanzado_frecuente(user_email: str, recurso: str, cantidad: int) -> Dict[str, str]:
        return {
            "titulo": "📊 Usuario Activo",
            "mensaje": f"Usuario {user_email} ha alcanzado límites de {recurso} {cantidad} veces",
            "email_asunto": "Gallo App - Usuario Potencial para Upgrade",
            "email_html": f"""
            <h2>📊 Usuario con Alto Engagement</h2>
            <p><strong>Usuario:</strong> {user_email}</p>
            <p><strong>Recurso:</strong> {recurso}</p>
            <p><strong>Veces alcanzado límite:</strong> {cantidad}</p>
            <p>Este usuario muestra alto engagement y podría ser candidato para upgrade.</p>
            """
        }

# ========================================
# FUNCIONES HELPER
# ========================================

# Instancia global del servicio
notification_service = NotificationService()

async def notificar_nuevo_pago(user_email: str, monto: float, plan: str, admin_emails: List[str]):
    """Notifica a admins sobre nuevo pago pendiente"""
    template = NotificationTemplates.nuevo_pago_pendiente(user_email, monto, plan)
    
    # Enviar push
    await notification_service.enviar_push_admin(
        admin_emails=admin_emails,
        titulo=template["titulo"],
        mensaje=template["mensaje"],
        data={"tipo": "nuevo_pago", "user_email": user_email, "monto": monto},
        prioridad="alta"
    )
    
    # Enviar email
    await notification_service.enviar_email_admin(
        admin_emails=admin_emails,
        asunto=template["email_asunto"],
        mensaje=template["mensaje"],
        html_content=template["email_html"]
    )
    
    # WebSocket tiempo real
    await notification_service.enviar_websocket_admin(
        mensaje_tipo="nuevo_pago_pendiente",
        data={"user_email": user_email, "monto": monto, "plan": plan}
    )

async def notificar_pagos_vencidos(cantidad_pagos: int, horas_vencidas: int, admin_emails: List[str]):
    """Notifica sobre pagos vencidos"""
    template = NotificationTemplates.pago_vencido(cantidad_pagos, horas_vencidas)
    
    await notification_service.enviar_push_admin(
        admin_emails=admin_emails,
        titulo=template["titulo"],
        mensaje=template["mensaje"],
        data={"tipo": "pagos_vencidos", "cantidad": cantidad_pagos},
        prioridad="alta"
    )
    
    await notification_service.enviar_email_admin(
        admin_emails=admin_emails,
        asunto=template["email_asunto"],
        mensaje=template["mensaje"],
        html_content=template["email_html"]
    )

async def notificar_nuevo_usuario(user_email: str, admin_emails: List[str]):
    """Notifica sobre nuevo usuario registrado"""
    template = NotificationTemplates.nuevo_usuario_registrado(user_email)
    
    await notification_service.enviar_push_admin(
        admin_emails=admin_emails,
        titulo=template["titulo"],
        mensaje=template["mensaje"],
        data={"tipo": "nuevo_usuario", "user_email": user_email},
        prioridad="normal"
    )

async def obtener_emails_admin_notificaciones() -> List[str]:
    """Obtiene emails de admins que reciben notificaciones"""
    # TODO: Consultar base de datos
    # En tu caso específico, sabemos que es juan.salas.nuevo@galloapp.com
    return ["juan.salas.nuevo@galloapp.com"]