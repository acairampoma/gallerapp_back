import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, PlainTextContent, HtmlContent
from app.core.config import settings
from typing import Optional

class EmailService:
    """🔥 Servicio épico de emails con SendGrid"""
    
    def __init__(self):
        self.sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        self.from_email = settings.SENDGRID_FROM_EMAIL
        self.from_name = settings.SENDGRID_FROM_NAME
    
    def send_password_reset_code(self, to_email: str, code: str, user_name: str = None) -> bool:
        """Enviar código de recuperación de contraseña"""
        
        try:
            # Nombre por defecto si no se proporciona
            display_name = user_name or "Usuario"
            
            # Contenido del email
            subject = "🔐 Código de Recuperación - Casta de Gallos"
            
            # Texto plano
            plain_text = f"""
Hola {display_name},

Has solicitado recuperar tu contraseña en Casta de Gallos.

Tu código de verificación es: {code}

Este código expira en 15 minutos.

Si no solicitaste este código, puedes ignorar este mensaje.

Saludos,
Equipo Casta de Gallos
"""
            
            # HTML bonito
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Código de Recuperación</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #2c5530, #4CAF50); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 28px;">🐓 CASTA DE GALLOS</h1>
        <p style="color: #e8f5e8; margin: 10px 0 0 0; font-size: 16px;">Sistema de Gestión Avícola</p>
    </div>
    
    <div style="background: white; padding: 40px; border: 1px solid #ddd; border-radius: 0 0 10px 10px;">
        <h2 style="color: #2c5530; margin-bottom: 20px;">🔐 Recuperación de Contraseña</h2>
        
        <p>Hola <strong>{display_name}</strong>,</p>
        
        <p>Has solicitado recuperar tu contraseña en <strong>Casta de Gallos</strong>.</p>
        
        <div style="background: #f8f9fa; border: 2px solid #2c5530; border-radius: 10px; padding: 25px; text-align: center; margin: 25px 0;">
            <p style="margin: 0; color: #666; font-size: 14px;">Tu código de verificación es:</p>
            <h1 style="margin: 10px 0; color: #2c5530; font-size: 36px; letter-spacing: 3px; font-weight: bold;">{code}</h1>
            <p style="margin: 0; color: #999; font-size: 12px;">⏰ Expira en 15 minutos</p>
        </div>
        
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
            <p style="margin: 0; color: #856404; font-size: 14px;">
                <strong>⚠️ Importante:</strong> Si no solicitaste este código, puedes ignorar este mensaje. 
                Tu cuenta permanece segura.
            </p>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 12px;">
            <p>Este email fue enviado automáticamente, por favor no responder.</p>
            <p><strong>Equipo Casta de Gallos</strong><br>
            Sistema de Gestión Avícola Profesional</p>
        </div>
    </div>
</body>
</html>
"""
            
            # Crear el mensaje
            message = Mail(
                from_email=From(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=Subject(subject),
                plain_text_content=PlainTextContent(plain_text),
                html_content=HtmlContent(html_content)
            )
            
            # Enviar email
            response = self.sg.send(message)
            
            if response.status_code == 202:
                print(f"✅ Email enviado exitosamente a {to_email}")
                return True
            else:
                print(f"❌ Error enviando email: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en EmailService: {str(e)}")
            return False
    
    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Enviar email de bienvenida"""
        # TODO: Implementar cuando sea necesario
        pass
    
    def send_vaccine_reminder(self, to_email: str, gallo_name: str, vaccine_name: str, due_date: str) -> bool:
        """Enviar recordatorio de vacuna"""
        # TODO: Implementar cuando sea necesario  
        pass

# 🔥 INSTANCIA GLOBAL DEL SERVICIO
email_service = EmailService()