#!/usr/bin/env python
# 🔧 TEST FIREBASE CON VARIABLES DE RAILWAY
# Ejecutar con: railway run python test_railway_firebase.py

import os
import sys

def test_firebase_railway():
    """Verificar Firebase con variables de Railway"""
    
    print("=" * 60)
    print("🚂 RAILWAY + FIREBASE TEST")
    print("=" * 60)
    
    # 1. Verificar que estamos usando Railway
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print(f"✅ Ejecutando con Railway: {os.getenv('RAILWAY_ENVIRONMENT')}")
    else:
        print("⚠️ No detectado Railway environment")
    
    # 2. Verificar variables críticas
    print("\n📋 VARIABLES FIREBASE:")
    print("-" * 40)
    
    critical_vars = {
        'FIREBASE_PROJECT_ID': os.getenv('FIREBASE_PROJECT_ID'),
        'FIREBASE_CLIENT_EMAIL': os.getenv('FIREBASE_CLIENT_EMAIL'),
        'FIREBASE_PRIVATE_KEY': os.getenv('FIREBASE_PRIVATE_KEY'),
    }
    
    all_present = True
    for var_name, var_value in critical_vars.items():
        if var_value:
            if var_name == 'FIREBASE_PRIVATE_KEY':
                # Verificar formato
                if var_value.startswith('-----BEGIN PRIVATE KEY-----'):
                    print(f"✅ {var_name}: Formato correcto")
                    # Verificar saltos de línea
                    if '\\n' in var_value:
                        print("   ✅ Contiene \\n literales (correcto)")
                    else:
                        print("   ⚠️ No contiene \\n - puede fallar")
                else:
                    print(f"❌ {var_name}: MAL FORMATO - no empieza con -----BEGIN")
                    all_present = False
            else:
                print(f"✅ {var_name}: {var_value[:40]}...")
        else:
            print(f"❌ {var_name}: NO ENCONTRADA")
            all_present = False
    
    # 3. Intentar inicializar Firebase
    print("\n🔥 INTENTANDO INICIALIZAR FIREBASE:")
    print("-" * 40)
    
    if not all_present:
        print("❌ Faltan variables críticas - no se puede inicializar")
        return False
    
    try:
        import firebase_admin
        from firebase_admin import credentials
        
        # Construir credenciales
        private_key = os.getenv('FIREBASE_PRIVATE_KEY')
        # Fix saltos de línea
        private_key = private_key.replace('\\n', '\n')
        
        cred_dict = {
            "type": "service_account",
            "project_id": os.getenv('FIREBASE_PROJECT_ID'),
            "private_key": private_key,
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', 'default'),
            "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        }
        
        # Inicializar
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ ¡FIREBASE INICIALIZADO EXITOSAMENTE!")
            print(f"✅ Project ID: {os.getenv('FIREBASE_PROJECT_ID')}")
            return True
        else:
            print("✅ Firebase ya estaba inicializado")
            return True
            
    except Exception as e:
        print(f"❌ ERROR al inicializar: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("=" * 60)

if __name__ == "__main__":
    success = test_firebase_railway()
    sys.exit(0 if success else 1)