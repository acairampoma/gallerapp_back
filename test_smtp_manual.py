#!/usr/bin/env python3
"""
Script para probar envío SMTP manual
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def test_smtp_manual():
    """Probar envío manual de email SMTP"""
    
    # Configuración SMTP
    SMTP_HOST = "mail.jsinnovatech.com"
    SMTP_PORT = 587
    SMTP_USER = "sistemas@jsinnovatech.com"
    SMTP_PASSWORD = "Joa420188*"
    SMTP_FROM_EMAIL = "sistemas@jsinnovatech.com"
    SMTP_FROM_NAME = "Sistemas Gallistico"
    
    # Email de prueba
    to_email = "alancairampoma@gmail.com"
    subject = "🔐 PRUEBA SMTP - Código de Recuperación"
    code = "101960"
    
    print(f"🧪 Probando SMTP...")
    print(f"   Host: {SMTP_HOST}:{SMTP_PORT}")
    print(f"   User: {SMTP_USER}")
    print(f"   To: {to_email}")
    print(f"   Code: {code}")
    
    try:
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = to_email
        
        # Contenido HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Código de Recuperación</title>
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #2c3e50, #3498db); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">🐓 CASTO DE GALLOS</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Sistema de Recuperación</p>
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #2c3e50; margin-bottom: 20px;">🔐 Código de Recuperación</h2>
                    <p style="color: #555; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                        Has solicitado recuperar tu contraseña. Usa el siguiente código:
                    </p>
                    <div style="background-color: #f8f9fa; border: 2px dashed #3498db; border-radius: 8px; padding: 20px; text-align: center; margin: 30px 0;">
                        <span style="font-size: 32px; font-weight: bold; color: #2c3e50; letter-spacing: 5px;">{code}</span>
                    </div>
                    <p style="color: #777; font-size: 14px; margin-top: 30px;">
                        ⏱️ Este código expirará en 15 minutos<br>
                        🔒 Si no solicitaste este cambio, ignora este email
                    </p>
                </div>
                <div style="background-color: #2c3e50; color: white; padding: 20px; text-align: center;">
                    <p style="margin: 0; font-size: 14px;">© 2024 Sistemas Gallístico - Todos los derechos reservados</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        # Conectar y enviar
        print("🔌 Conectando al servidor SMTP...")
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.set_debuglevel(1)  # Debug mode
        
        print("🔒 Iniciando STARTTLS...")
        server.starttls()
        
        print("🔐 Iniciando sesión...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        
        print("📧 Enviando email...")
        server.send_message(msg)
        
        print("✅ Email enviado exitosamente!")
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False

if __name__ == "__main__":
    test_smtp_manual()
