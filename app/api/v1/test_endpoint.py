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

@router.post("/test-broadcast")
async def test_broadcast(notification_data: dict = None):
    """Enviar notificación a TODOS los dispositivos registrados"""
    try:
        from app.database import get_db
        from app.models.fcm_token import FCMToken
        from app.services.firebase_service import firebase_service
        
        # Obtener sesión de BD
        db = next(get_db())
        
        # Obtener TODOS los tokens activos
        all_tokens = db.query(FCMToken).filter(
            FCMToken.is_active == True
        ).all()
        
        if not all_tokens:
            return {
                "success": False,
                "message": "No hay tokens FCM registrados",
                "sent_count": 0
            }
        
        tokens_list = [token.fcm_token for token in all_tokens]
        
        # Usar datos del request o valores por defecto
        title = notification_data.get("title", "🔥 Test Broadcast GalloApp") if notification_data else "🔥 Test Broadcast GalloApp"
        body = notification_data.get("body", f"Notificación enviada a {len(tokens_list)} dispositivos") if notification_data else f"Notificación enviada a {len(tokens_list)} dispositivos"
        data = notification_data.get("data", {}) if notification_data else {}
        
        # Agregar datos adicionales
        data.update({
            "type": "test_broadcast",
            "total_devices": str(len(tokens_list))
        })
        
        print(f"🔔 === ENVIANDO NOTIFICACIÓN ===")
        print(f"📱 Tokens encontrados: {len(tokens_list)}")
        print(f"📱 Primer token: {tokens_list[0][:20]}...")
        print(f"📧 Título: {title}")
        print(f"📧 Cuerpo: {body}")
        
        # Enviar notificación de broadcast
        result = await firebase_service.send_notification_to_tokens(
            tokens=tokens_list,
            title=title,
            body=body,
            data=data
        )
        
        print(f"📊 Resultado: {result}")
        
        return {
            "success": result["success"],
            "sent_count": result.get("success_count", 0),
            "failed_count": result.get("failure_count", 0),
            "total_tokens": len(tokens_list),
            "message": f"Broadcast enviado a {result.get('success_count', 0)} de {len(tokens_list)} dispositivos",
            "debug_info": {
                "tokens_found": len(tokens_list),
                "firebase_result": result
            }
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ ERROR COMPLETO: {error_trace}")
        
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "Error enviando broadcast",
            "traceback": error_trace
        }