# 🔧 ENDPOINT DE PRUEBA DIRECTO
from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/test-vars")
async def test_variables():
    """Ver las variables de entorno TAL CUAL están"""
    
    # Solo mostrar si existen, no el contenido
    return {
        "FIREBASE_PROJECT_ID": "✅ EXISTE" if os.getenv('FIREBASE_PROJECT_ID') else "❌ NO EXISTE",
        "FIREBASE_CLIENT_EMAIL": "✅ EXISTE" if os.getenv('FIREBASE_CLIENT_EMAIL') else "❌ NO EXISTE",
        "FIREBASE_PRIVATE_KEY": "✅ EXISTE" if os.getenv('FIREBASE_PRIVATE_KEY') else "❌ NO EXISTE",
        "FIREBASE_PRIVATE_KEY_FORMAT": "✅ EMPIEZA BIEN" if os.getenv('FIREBASE_PRIVATE_KEY', '').startswith('-----BEGIN') else "❌ MAL FORMATO",
        "FIREBASE_PRIVATE_KEY_LENGTH": len(os.getenv('FIREBASE_PRIVATE_KEY', '')),
        "FIREBASE_CLIENT_ID": "✅ EXISTE" if os.getenv('FIREBASE_CLIENT_ID') else "❌ NO EXISTE",
    }

@router.get("/test-init")
async def test_init():
    """Intentar inicializar Firebase AHORA MISMO"""
    import firebase_admin
    from firebase_admin import credentials
    
    try:
        # Ver si ya está inicializado
        if firebase_admin._apps:
            return {"status": "✅ YA ESTABA INICIALIZADO"}
        
        # Obtener variables
        project_id = os.getenv('FIREBASE_PROJECT_ID')
        private_key = os.getenv('FIREBASE_PRIVATE_KEY')
        client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
        
        if not all([project_id, private_key, client_email]):
            return {
                "status": "❌ FALTAN VARIABLES",
                "project_id": "✅" if project_id else "❌",
                "private_key": "✅" if private_key else "❌",
                "client_email": "✅" if client_email else "❌"
            }
        
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
        firebase_admin.initialize_app(cred)
        
        return {"status": "✅ INICIALIZADO EXITOSAMENTE AHORA!"}
        
    except Exception as e:
        return {
            "status": "❌ ERROR",
            "error": str(e),
            "tipo_error": type(e).__name__
        }