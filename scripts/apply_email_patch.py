#!/usr/bin/env python3
"""
🚀 PARCHE INMEDIATO - APLICAR SERVICIO OPTIMIZADO
Reemplaza temporalmente el servicio de email para mejor entrega

Autor: JSALASINNOVATECH
Fecha: 2025-11-21
"""

import os
import shutil
from datetime import datetime

def apply_email_patch():
    """Aplicar parche de email optimizado"""
    
    print("🚀 APLICANDO PARCHE DE EMAIL OPTIMIZADO")
    print("=" * 50)
    
    # Rutas de archivos
    original_service = "app/services/email_service.py"
    optimized_service = "app/services/email_service_optimized.py" 
    backup_service = f"app/services/email_service_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    try:
        # 1. Crear backup del servicio original
        if os.path.exists(original_service):
            print(f"📦 Creando backup: {backup_service}")
            shutil.copy2(original_service, backup_service)
            print("✅ Backup creado exitosamente")
        
        # 2. Verificar que el servicio optimizado existe
        if not os.path.exists(optimized_service):
            print(f"❌ ERROR: No se encuentra {optimized_service}")
            return False
            
        # 3. Reemplazar el servicio original con el optimizado
        print(f"🔄 Reemplazando {original_service} con versión optimizada...")
        
        # Leer contenido optimizado
        with open(optimized_service, 'r', encoding='utf-8') as f:
            optimized_content = f.read()
        
        # Modificar imports para mantener compatibilidad
        optimized_content = optimized_content.replace(
            'class OptimizedEmailService:', 
            'class EmailService:'
        )
        optimized_content = optimized_content.replace(
            'optimized_email_service = OptimizedEmailService()',
            'email_service = EmailService()'
        )
        
        # Escribir al archivo original
        with open(original_service, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
            
        print("✅ Servicio reemplazado exitosamente")
        
        # 4. Actualizar imports en auth.py si es necesario
        auth_file = "app/api/v1/auth.py"
        if os.path.exists(auth_file):
            print("🔄 Verificando imports en auth.py...")
            
            with open(auth_file, 'r', encoding='utf-8') as f:
                auth_content = f.read()
            
            # No necesita cambios, ya usa 'from app.services.email_service import email_service'
            print("✅ Auth.py no requiere cambios")
        
        print("\n🎉 PARCHE APLICADO EXITOSAMENTE!")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. 🔧 Configura los registros DNS según docs/EMAIL_DNS_SETUP.md") 
        print("2. 🧪 Ejecuta scripts/fix_email_delivery.py para diagnóstico")
        print("3. 📧 Prueba envío de correos a Hotmail/Outlook")
        print(f"4. 🔄 Para revertir: cp {backup_service} {original_service}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR aplicando parche: {e}")
        
        # Intentar revertir si hay backup
        if os.path.exists(backup_service):
            print("🔄 Intentando revertir cambios...")
            shutil.copy2(backup_service, original_service)
            print("✅ Cambios revertidos")
            
        return False

def show_current_status():
    """Mostrar estado actual del servicio de email"""
    
    print("\n📊 ESTADO ACTUAL DEL SERVICIO DE EMAIL")
    print("=" * 50)
    
    service_file = "app/services/email_service.py"
    
    if os.path.exists(service_file):
        with open(service_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar qué versión está activa
        if 'OptimizedEmailService' in content:
            print("🔧 ESTADO: Servicio optimizado NO aplicado")
            print("   El archivo contiene OptimizedEmailService como clase separada")
        elif '📧 [EMAIL-OPTIMIZED]' in content:
            print("✅ ESTADO: Servicio optimizado APLICADO") 
            print("   El servicio está usando la versión optimizada")
        else:
            print("📧 ESTADO: Servicio original")
            print("   Usando versión original del servicio")
            
        # Verificar configuración SMTP
        if 'USE_SMTP' in content and 'SMTP_HOST' in content:
            print("✅ SMTP: Configuración SMTP encontrada")
        else:
            print("⚠️ SMTP: Configuración SMTP no encontrada")
            
        # Verificar si quita emojis
        if '🔐' in content or '📧' in content:
            print("⚠️ EMOJIS: El servicio aún contiene emojis en content")
        else:
            print("✅ EMOJIS: Servicio sin emojis en content")
            
    else:
        print("❌ ERROR: No se encuentra app/services/email_service.py")

def main():
    """Función principal"""
    
    print("🔧 HERRAMIENTA DE PARCHE DE EMAIL - GALLISTICO")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("app/services"):
        print("❌ ERROR: Ejecuta este script desde el directorio raíz del proyecto")
        return
    
    # Mostrar estado actual
    show_current_status()
    
    # Preguntar si aplicar parche
    response = input("\n¿Aplicar parche optimizado? (s/N): ").lower().strip()
    
    if response in ['s', 'si', 'y', 'yes']:
        if apply_email_patch():
            print("\n🎯 RECOMENDACIONES POST-PARCHE:")
            print("1. 📋 Lee docs/EMAIL_DNS_SETUP.md para configurar DNS")
            print("2. 🧪 Ejecuta: python scripts/fix_email_delivery.py") 
            print("3. 🚀 Despliega en Railway para probar")
            print("4. 📧 Envía email de prueba a alancairampoma@hotmail.com")
        else:
            print("\n❌ Error aplicando parche. Revisa los logs.")
    else:
        print("\n⏹️ Parche no aplicado. El servicio permanece sin cambios.")
        
    print("\n📚 DOCUMENTACIÓN ADICIONAL:")
    print("   - docs/EMAIL_DNS_SETUP.md: Configuración DNS completa")
    print("   - scripts/fix_email_delivery.py: Diagnóstico automático")
    print("   - app/services/email_service_optimized.py: Versión optimizada")

if __name__ == "__main__":
    main()
