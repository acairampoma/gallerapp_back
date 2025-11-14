# 🔧 DEBUG FIREBASE - VERIFICAR VARIABLES Y CONEXIÓN
import os
import json
from decouple import config

def debug_firebase():
    print("🔧 === DEBUG FIREBASE ===")
    print("-" * 50)
    
    # 1. Verificar variables de entorno
    print("1️⃣ VARIABLES DE ENTORNO:")
    vars_needed = {
        'FIREBASE_PROJECT_ID': None,
        'FIREBASE_CLIENT_EMAIL': None,
        'FIREBASE_PRIVATE_KEY': None,
        'FIREBASE_PRIVATE_KEY_ID': None,
        'FIREBASE_CLIENT_ID': None,
    }
    
    for var in vars_needed:
        value = os.getenv(var)
        if value:
            if var == 'FIREBASE_PRIVATE_KEY':
                # Solo mostrar inicio y fin de la clave
                if value.startswith('-----BEGIN'):
                    print(f"  ✅ {var}: [CLAVE PRIVADA PRESENTE]")
                else:
                    print(f"  ❌ {var}: [FORMATO INCORRECTO - No empieza con -----BEGIN]")
            else:
                # Mostrar primeros 30 caracteres
                display = value[:30] + "..." if len(value) > 30 else value
                print(f"  ✅ {var}: {display}")
        else:
            print(f"  ❌ {var}: NO ENCONTRADA")
    
    print("-" * 50)
    
    # 2. Intentar crear el diccionario de credenciales
    print("2️⃣ CONSTRUYENDO CREDENCIALES:")
    try:
        project_id = os.getenv('FIREBASE_PROJECT_ID')
        private_key = os.getenv('FIREBASE_PRIVATE_KEY')
        client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
        
        if all([project_id, private_key, client_email]):
            # Verificar formato de private_key
            private_key_fixed = private_key.replace('\\n', '\n')
            
            creds = {
                "type": "service_account",
                "project_id": project_id,
                "private_key": private_key_fixed,
                "client_email": client_email,
            }
            
            print("  ✅ Credenciales construidas exitosamente")
            print(f"  📧 Client Email: {client_email}")
            print(f"  📦 Project ID: {project_id}")
            
            # 3. Intentar inicializar Firebase
            print("-" * 50)
            print("3️⃣ INICIALIZANDO FIREBASE:")
            try:
                from firebase_admin import credentials, initialize_app
                import firebase_admin
                
                if firebase_admin._apps:
                    print("  ⚠️ Firebase ya estaba inicializado")
                else:
                    cred = credentials.Certificate(creds)
                    initialize_app(cred)
                    print("  ✅ FIREBASE INICIALIZADO EXITOSAMENTE!")
                    
            except Exception as e:
                print(f"  ❌ Error inicializando: {e}")
                
        else:
            print("  ❌ Faltan variables críticas")
            
    except Exception as e:
        print(f"  ❌ Error construyendo credenciales: {e}")
    
    print("-" * 50)
    print("🔧 === FIN DEBUG ===")

if __name__ == "__main__":
    debug_firebase()