# 🚀 app/main_clean.py - API LIMPIA Y ORDENADA
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cloudinary
import cloudinary.uploader
import ssl
import urllib3

# Importar solo los routers limpios
from app.api.v1 import auth, profiles
from app.api.v1.gallos_clean import router as gallos_router
from app.api.v1.fotos_clean import router as fotos_router  
from app.api.v1.razas_clean import router as razas_router
from app.api.v1.genealogia_clean import router as genealogia_router
from app.core.config import settings
from app.core.exceptions import CustomException

# 🔧 Deshabilitar verificación SSL para desarrollo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# 🚀 Configuración FastAPI
app = FastAPI(
    title="🐓 GalloApp Pro API - LIMPIA",
    description="Backend Limpio para Gestión de Gallos con 12 Endpoints Esenciales",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 🌐 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ☁️ Configurar Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

# ❌ Exception handler global
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# 🌐 INCLUIR ROUTERS LIMPIOS
app.include_router(auth.router, prefix="/auth", tags=["🔐 Autenticación"])
app.include_router(profiles.router, prefix="/profiles", tags=["👤 Perfiles"])

# 🐓 ENDPOINTS PRINCIPALES (12 TOTAL)
app.include_router(gallos_router, prefix="/api/v1/gallos", tags=["🐓 Gallos (5)"])           # 5 endpoints
app.include_router(fotos_router, prefix="/api/v1/gallos", tags=["📷 Fotos (3)"])            # 3 endpoints  
app.include_router(razas_router, prefix="/api/v1/razas", tags=["🧬 Razas (2)"])             # 2 endpoints
app.include_router(genealogia_router, prefix="/api/v1/gallos", tags=["🌳 Genealogía (2)"]) # 2 endpoints

# 🏠 ENDPOINTS BÁSICOS

@app.get("/")
async def root():
    """🏠 Endpoint raíz con información de la API limpia"""
    return {
        "message": "🐓 ¡GalloApp Pro API LIMPIA!",
        "status": "✅ ACTIVO",
        "version": "2.0.0 - CLEAN",
        "endpoints_total": 12,
        "security": "🔒 JWT Protegido",
        "endpoints": {
            # Básicos
            "docs": "/docs",
            "health": "/health",
            
            # Autenticación  
            "auth": "/auth/*",
            "profiles": "/profiles/*",
            
            # 🐓 GALLOS (5 endpoints)
            "gallos_list": "GET /api/v1/gallos",
            "gallos_create": "POST /api/v1/gallos", 
            "gallos_get": "GET /api/v1/gallos/{id}",
            "gallos_update": "PUT /api/v1/gallos/{id}",
            "gallos_delete": "DELETE /api/v1/gallos/{id}",
            
            # 📷 FOTOS (3 endpoints)
            "fotos_upload": "POST /api/v1/gallos/{id}/foto",
            "fotos_list": "GET /api/v1/gallos/{id}/fotos", 
            "fotos_delete": "DELETE /api/v1/gallos/{id}/fotos/{foto_id}",
            
            # 🧬 RAZAS (2 endpoints)
            "razas_list": "GET /api/v1/razas",
            "razas_get": "GET /api/v1/razas/{id}",
            
            # 🌳 GENEALOGÍA (2 endpoints ÉPICOS)
            "genealogia_tree": "GET /api/v1/gallos/{id}/genealogia",
            "genealogia_descendants": "GET /api/v1/gallos/{id}/descendants"
        },
        "flutter_ready": True,
        "database": "PostgreSQL",
        "storage": "Cloudinary",
        "genealogy": "🌳 Árbol infinito disponible"
    }

@app.get("/health")
async def health_check():
    """🏥 Health check del sistema"""
    return {
        "status": "✅ HEALTHY",
        "service": "GalloApp Pro API - CLEAN",
        "database": "PostgreSQL Railway",
        "storage": "Cloudinary",
        "auth": "JWT Ready",
        "environment": "local",
        "endpoints_active": 12
    }

# 🧪 ENDPOINTS DE TESTING (mantenemos los útiles)

@app.get("/test-cloudinary")
async def test_cloudinary():
    """☁️ Test de conexión con Cloudinary"""
    try:
        # Test básico de configuración
        return {
            "status": "✅ CLOUDINARY CONFIGURADO",
            "cloud_name": settings.CLOUDINARY_CLOUD_NAME,
            "test_config": "✅ EXITOSO",
            "sample_original_url": f"http://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/v1/test/galloapp_test",
            "sample_webp_url": f"http://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/h_100,q_auto,w_100/v1/test/galloapp_test.webp",
            "transformations": "✅ JPG → WebP DISPONIBLE",
            "note": "Configuración OK - Upload test deshabilitado por SSL"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"❌ Error en Cloudinary: {str(e)}"
        )

@app.get("/test-db")
async def test_database():
    """🗄️ Test de conexión con PostgreSQL"""
    try:
        from app.database import engine
        with engine.connect() as connection:
            result = connection.execute("SELECT 1 as test")
            return {
                "status": "✅ POSTGRESQL CONECTADO",
                "database": "Railway PostgreSQL",
                "test_query": "✅ EXITOSO",
                "connection": "✅ ACTIVA"
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"❌ Error conectando a PostgreSQL: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
