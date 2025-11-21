#!/usr/bin/env python3
"""
🔧 SERVICIO DE EMAIL CORREGIDO - OPTIMIZADO PARA HOTMAIL/OUTLOOK
Versión mejorada del email_service.py con correcciones específicas

Autor: JSALASINNOVATECH
Fecha: 2025-11-21
"""

from typing import Optional, Dict, Any
import logging
import smtplib
import time
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, make_msgid, formatdate
from app.core.config import settings

logger = logging.getLogger(__name__)

class OptimizedEmailService:
    """Servicio de email optimizado específicamente para Hotmail/Outlook"""
    
    def __init__(self):
        """Inicializar cliente de email con configuraciones optimizadas"""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT 
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        self.domain = "jsinnovatech.com"
        
        logger.info(f"🔧 [EMAIL-OPTIMIZED] Configurando servicio optimizado")
        logger.info(f"📧 [EMAIL-OPTIMIZED] Servidor: {self.smtp_host}:{self.smtp_port}")
        logger.info(f"👤 [EMAIL-OPTIMIZED] Usuario: {self.smtp_user}")

    def generate_verification_code(self) -> str:
        """Generar código de verificación de 6 dígitos"""
        return ''.join(random.choices(string.digits, k=6))

    def _create_optimized_message(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str,
        plain_content: str
    ) -> MIMEMultipart:
        """Crear mensaje optimizado para Hotmail/Outlook"""
        
        # Crear mensaje principal
        msg = MIMEMultipart('alternative')
        
        # Headers críticos para Hotmail/Outlook (SIN EMOJIS EN HEADERS)
        msg['Subject'] = subject
        msg['From'] = formataddr((self.from_name, self.from_email))
        msg['To'] = to_email
        msg['Date'] = formatdate(localtime=True)
        msg['Message-ID'] = make_msgid(domain=self.domain)
        
        # Headers adicionales para mejorar reputación
        msg['X-Mailer'] = f'Gallistico-EmailSystem/1.0 ({self.domain})'
        msg['X-Priority'] = '3'  # Normal priority
        msg['X-MSMail-Priority'] = 'Normal'  # Específico para Microsoft
        msg['Precedence'] = 'bulk'  # Indica email automatizado legítimo
        msg['List-Unsubscribe'] = f'<mailto:unsubscribe@{self.domain}>'  # RFC requerido
        
        # Contenido del mensaje
        part_plain = MIMEText(plain_content, 'plain', 'utf-8')
        part_html = MIMEText(html_content, 'html', 'utf-8')
        
        # Adjuntar en orden correcto (plain primero, luego HTML)
        msg.attach(part_plain)
        msg.attach(part_html)
        
        return msg

    def _send_via_smtp(self, msg: MIMEMultipart, to_email: str) -> Dict[str, Any]:
        """Enviar mensaje vía SMTP con manejo de errores mejorado"""
        
        try:
            logger.info(f"📡 [SMTP] Conectando a {self.smtp_host}:{self.smtp_port}")
            
            # Crear conexión SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=60) as server:
                # Habilitar debug solo en desarrollo
                if settings.ENVIRONMENT == "local":
                    server.set_debuglevel(1)
                
                # Iniciar conexión segura
                logger.info("🔒 [SMTP] Iniciando STARTTLS...")
                server.starttls()
                
                # Autenticación
                logger.info("🔐 [SMTP] Autenticando...")
                server.login(self.smtp_user, self.smtp_password)
                
                # Enviar mensaje
                logger.info(f"📧 [SMTP] Enviando email a {to_email}...")
                result = server.send_message(msg)
                
                logger.info(f"✅ [SMTP] Email enviado exitosamente a {to_email}")
                
                return {
                    "success": True,
                    "message": "Email enviado correctamente",
                    "smtp_result": str(result),
                    "delivery_status": "sent"
                }
                
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ [SMTP] Error de autenticación: {e}")
            return {
                "success": False,
                "message": "Error de autenticación SMTP",
                "error_type": "auth_error",
                "error_detail": str(e)
            }
            
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"❌ [SMTP] Destinatario rechazado: {e}")
            return {
                "success": False, 
                "message": "Destinatario rechazado por el servidor",
                "error_type": "recipient_refused",
                "error_detail": str(e)
            }
            
        except smtplib.SMTPServerDisconnected as e:
            logger.error(f"❌ [SMTP] Servidor desconectado: {e}")
            return {
                "success": False,
                "message": "Conexión al servidor perdida",
                "error_type": "connection_error", 
                "error_detail": str(e)
            }
            
        except Exception as e:
            logger.error(f"❌ [SMTP] Error general: {e}")
            return {
                "success": False,
                "message": f"Error enviando email: {str(e)}",
                "error_type": "general_error",
                "error_detail": str(e)
            }

    async def send_verification_email(
        self,
        email: str,
        name: str, 
        verification_code: str
    ) -> Dict[str, Any]:
        """
        Enviar email de verificación optimizado para Hotmail/Outlook
        """
        logger.info(f"📤 [EMAIL] Enviando verificación a {email}")
        logger.info(f"   🔐 Código: {verification_code}")
        
        try:
            # Subject SIN EMOJIS - Hotmail/Outlook los puede filtrar
            subject = f"Codigo de Verificacion: {verification_code} - Casta de Gallos"
            
            # Contenido plain text (fallback)
            plain_content = f"""
CASTA DE GALLOS - Verificacion de Cuenta

Hola {name},

Gracias por registrarte en Casta de Gallos. Para activar tu cuenta, 
necesitas verificar tu correo electronico.

Tu codigo de verificacion es: {verification_code}

Este codigo es valido por 15 minutos.

Si no solicitaste este registro, puedes ignorar este mensaje.

Saludos,
Equipo Casta de Gallos

---
Este es un correo automatico, por favor no responder.
            """.strip()
            
            # Contenido HTML optimizado (sin emojis en texto crítico)
            html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verificacion de Cuenta - Casta de Gallos</title>
    <!--[if mso]>
    <style type="text/css">
    table {{ border-collapse: collapse; }}
    </style>
    <![endif]-->
</head>
<body style="margin:0;padding:0;font-family:Arial,sans-serif;background-color:#f4f4f4;">
    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#f4f4f4;padding:20px 0;">
        <tr>
            <td align="center">
                <table cellpadding="0" cellspacing="0" border="0" width="600" style="max-width:600px;background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background:linear-gradient(135deg,#2c5530 0%,#4CAF50 100%);color:#ffffff;padding:30px 20px;text-align:center;">
                            <h1 style="margin:0;font-size:24px;font-weight:bold;">CASTA DE GALLOS</h1>
                            <p style="margin:8px 0 0 0;font-size:16px;opacity:0.9;">Verificacion de Cuenta</p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding:40px 30px;">
                            <h2 style="color:#2c3e50;margin:0 0 20px 0;font-size:20px;">Hola {name}!</h2>
                            
                            <p style="color:#555555;font-size:16px;line-height:1.6;margin:0 0 25px 0;">
                                Gracias por registrarte en <strong>Casta de Gallos</strong>. Para activar tu cuenta, 
                                necesitas verificar tu correo electronico.
                            </p>
                            
                            <div style="background-color:#f8f9fa;border:2px solid #2c5530;border-radius:8px;padding:20px;text-align:center;margin:25px 0;">
                                <p style="margin:0 0 10px 0;color:#2c5530;font-size:14px;font-weight:bold;">
                                    TU CODIGO DE VERIFICACION:
                                </p>
                                <div style="font-size:32px;font-weight:bold;color:#2c5530;letter-spacing:4px;font-family:Courier,monospace;">
                                    {verification_code}
                                </div>
                            </div>
                            
                            <div style="background-color:#fff3cd;border-left:4px solid #ffc107;padding:15px;margin:25px 0;border-radius:4px;">
                                <p style="margin:0;color:#856404;font-size:14px;">
                                    <strong>Importante:</strong> Este codigo es valido por 15 minutos.<br>
                                    Si no solicitaste este registro, puedes ignorar este mensaje.
                                </p>
                            </div>
                            
                            <p style="color:#555555;font-size:16px;line-height:1.6;margin:25px 0 0 0;">
                                Una vez verificada tu cuenta podras:
                            </p>
                            <ul style="color:#555555;font-size:14px;line-height:1.6;margin:10px 0 0 20px;">
                                <li>Gestionar tus gallos y pedigri</li>
                                <li>Organizar peleas y eventos</li>
                                <li>Participar en el marketplace</li>
                                <li>Ver reportes y estadisticas</li>
                            </ul>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color:#f8f9fa;padding:25px;text-align:center;border-top:1px solid #eee;">
                            <p style="margin:0;color:#666;font-size:14px;font-weight:bold;">
                                Casta de Gallos
                            </p>
                            <p style="margin:5px 0 0 0;color:#999;font-size:12px;">
                                Tu plataforma profesional de gestion gallistica
                            </p>
                            <p style="margin:15px 0 0 0;color:#999;font-size:11px;">
                                Este es un correo automatico, por favor no responder.
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
            """
            
            # Crear mensaje optimizado
            msg = self._create_optimized_message(
                to_email=email,
                subject=subject,
                html_content=html_content,
                plain_content=plain_content
            )
            
            # Enviar mensaje
            result = self._send_via_smtp(msg, email)
            
            if result["success"]:
                logger.info(f"✅ [EMAIL] Verificación enviada exitosamente a {email}")
                return {
                    "success": True,
                    "message": "Codigo de verificacion enviado correctamente",
                    "email": email,
                    "code": verification_code,  # Solo para debug
                    "delivery_optimized": True
                }
            else:
                logger.error(f"❌ [EMAIL] Error enviando verificación: {result}")
                return {
                    "success": False,
                    "message": result.get("message", "Error enviando email"),
                    "email": email,
                    "error_details": result
                }
                
        except Exception as e:
            logger.error(f"❌ [EMAIL] Error crítico enviando verificación: {e}")
            return {
                "success": False,
                "message": f"Error critico: {str(e)}",
                "email": email
            }

    async def send_password_reset_code(
        self,
        email: str,
        name: str,
        reset_code: str
    ) -> Dict[str, Any]:
        """
        Enviar código de recuperación de contraseña optimizado
        """
        logger.info(f"📤 [EMAIL] Enviando recuperación a {email}")
        logger.info(f"   🔐 Código: {reset_code}")
        
        try:
            # Subject SIN EMOJIS
            subject = f"Codigo de Recuperacion: {reset_code} - Casta de Gallos"
            
            # Contenido plain text
            plain_content = f"""
CASTA DE GALLOS - Recuperacion de Contraseña

Hola {name},

Recibimos una solicitud para restablecer tu contraseña en Casta de Gallos.

Tu codigo de recuperacion es: {reset_code}

Este codigo es valido por 15 minutos.

Si no solicitaste este cambio, ignora este mensaje y tu contraseña 
permanecera sin cambios.

Saludos,
Equipo Casta de Gallos

---
Este es un correo automatico, por favor no responder.
            """.strip()
            
            # HTML optimizado para recuperación
            html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recuperacion de Contraseña - Casta de Gallos</title>
</head>
<body style="margin:0;padding:0;font-family:Arial,sans-serif;background-color:#f4f4f4;">
    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#f4f4f4;padding:20px 0;">
        <tr>
            <td align="center">
                <table cellpadding="0" cellspacing="0" border="0" width="600" style="max-width:600px;background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%);color:#ffffff;padding:30px 20px;text-align:center;">
                            <h1 style="margin:0;font-size:24px;font-weight:bold;">RECUPERACION DE CONTRASEÑA</h1>
                            <p style="margin:8px 0 0 0;font-size:16px;opacity:0.9;">Casta de Gallos</p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding:40px 30px;">
                            <h2 style="color:#2c3e50;margin:0 0 20px 0;font-size:20px;">Hola {name},</h2>
                            
                            <p style="color:#555555;font-size:16px;line-height:1.6;margin:0 0 25px 0;">
                                Recibimos una solicitud para restablecer tu contraseña en <strong>Casta de Gallos</strong>. 
                                Usa el siguiente codigo:
                            </p>
                            
                            <div style="background-color:#f8f9fa;border:2px solid #f5576c;border-radius:8px;padding:20px;text-align:center;margin:25px 0;">
                                <p style="margin:0 0 10px 0;color:#f5576c;font-size:14px;font-weight:bold;">
                                    CODIGO DE RECUPERACION:
                                </p>
                                <div style="font-size:32px;font-weight:bold;color:#f5576c;letter-spacing:4px;font-family:Courier,monospace;">
                                    {reset_code}
                                </div>
                            </div>
                            
                            <div style="background-color:#fff3cd;border-left:4px solid #ffc107;padding:15px;margin:25px 0;border-radius:4px;">
                                <p style="margin:0;color:#856404;font-size:14px;">
                                    <strong>Importante:</strong> Este codigo es valido por 15 minutos.<br>
                                    Si no solicitaste este cambio, ignora este mensaje y tu contraseña permanecera sin cambios.
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color:#f8f9fa;padding:25px;text-align:center;border-top:1px solid #eee;">
                            <p style="margin:0;color:#666;font-size:14px;font-weight:bold;">
                                Casta de Gallos
                            </p>
                            <p style="margin:15px 0 0 0;color:#999;font-size:11px;">
                                Este es un correo automatico, por favor no responder.
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
            """
            
            # Crear y enviar mensaje
            msg = self._create_optimized_message(
                to_email=email,
                subject=subject, 
                html_content=html_content,
                plain_content=plain_content
            )
            
            result = self._send_via_smtp(msg, email)
            
            if result["success"]:
                logger.info(f"✅ [EMAIL] Recuperación enviada exitosamente a {email}")
                return {
                    "success": True,
                    "message": "Codigo de recuperacion enviado",
                    "email": email
                }
            else:
                logger.error(f"❌ [EMAIL] Error enviando recuperación: {result}")
                return {
                    "success": False,
                    "message": result.get("message", "Error enviando email"),
                    "email": email,
                    "error_details": result
                }
                
        except Exception as e:
            logger.error(f"❌ [EMAIL] Error crítico enviando recuperación: {e}")
            return {
                "success": False,
                "message": f"Error critico: {str(e)}",
                "email": email
            }

    # Alias para compatibilidad
    async def send_password_reset_email(self, email: str, name: str, reset_code: str):
        """Alias para send_password_reset_code"""
        return await self.send_password_reset_code(email, name, reset_code)

# Instancia global optimizada
optimized_email_service = OptimizedEmailService()
