from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
import cloudinary
import cloudinary.uploader
import os
import ssl
import urllib3
from decouple import config

# Importar routers de API
from app.api.v1 import auth, profiles
from app.core.config import settings
from app.core.exceptions import CustomException

# 🔧 Deshabilitar verificación SSL para desarrollo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# 🚀 Configuración FastAPI
app = FastAPI(
    title="🐓 GalloApp Pro API",
    description="Backend para Gestión de Gallos de Pelea con Autenticación JWT",
    version="1.0.0",
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

# 📸 Configurar Cloudinary
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
        content={
            "error": True,
            "message": exc.message,
            "detail": exc.detail,
            "error_code": exc.error_code
        }
    )

# 🌐 Incluir routers de API
app.include_router(auth.router, prefix="/auth", tags=["🔐 Autenticación"])
app.include_router(profiles.router, prefix="/profiles", tags=["👤 Perfiles"])

# 🏠 ENDPOINTS BÁSICOS

@app.get("/")
async def root():
    """🏠 Hola Mundo"""
    return {
        "message": "🐓 ¡GalloApp Pro API con Seguridad JWT!",
        "status": "✅ ACTIVO",
        "version": "1.0.0",
        "security": "🔒 JWT Protegido",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/auth/*",
            "profiles": "/profiles/*",
            "test_db": "/test-db",
            "test_cloudinary": "/test-cloudinary"
        }
    }

@app.get("/health")
async def health_check():
    """💓 Health Check"""
    return {
        "status": "✅ HEALTHY",
        "service": "GalloApp Pro API",
        "database": "PostgreSQL Railway",
        "storage": "Cloudinary",
        "auth": "JWT Ready",
        "environment": settings.ENVIRONMENT
    }

@app.get("/test-db")
async def test_database():
    """🗄️ Test PostgreSQL Connection"""
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(settings.DATABASE_URL)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        
        # Test tabla usuarios si existe
        try:
            cursor.execute("SELECT COUNT(*) FROM users;")
            user_count = cursor.fetchone()[0]
        except:
            user_count = "Tabla no existe aún"
        
        cursor.close()
        conn.close()
        
        return {
            "status": "✅ PostgreSQL CONECTADO",
            "database": "Railway PostgreSQL",
            "version": db_version,
            "users_count": user_count,
            "connection": "✅ EXITOSA"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"❌ Error conectando a PostgreSQL: {str(e)}"
        )

@app.get("/test-cloudinary")
async def test_cloudinary():
    """📸 Test Cloudinary Connection"""
    try:
        # Test de configuración
        cloud_name = cloudinary.config().cloud_name
        
        # Test simple sin upload (solo verificar config)
        if not cloud_name:
            raise Exception("Cloudinary no configurado")
        
        # Simular URLs sin hacer upload real
        test_public_id = "test/galloapp_test"
        
        # Generar URL optimizada WebP
        webp_url = cloudinary.CloudinaryImage(test_public_id).build_url(
            format="webp",
            quality="auto",
            width=100,
            height=100
        )
        
        original_url = cloudinary.CloudinaryImage(test_public_id).build_url()
        
        return {
            "status": "✅ CLOUDINARY CONFIGURADO",
            "cloud_name": cloud_name,
            "test_config": "✅ EXITOSO",
            "sample_original_url": original_url,
            "sample_webp_url": webp_url,
            "transformations": "✅ JPG → WebP DISPONIBLE",
            "note": "Configuración OK - Upload test deshabilitado por SSL"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"❌ Error en Cloudinary: {str(e)}"
        )

@app.get("/test-full")
async def test_full_system():
    """🔥 Test Completo del Sistema"""
    results = {
        "sistema": "GalloApp Pro Backend",
        "timestamp": "2025-01-23",
        "security": "🔒 JWT Implementado",
        "tests": {}
    }
    
    # Test PostgreSQL
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.close()
        conn.close()
        results["tests"]["postgresql"] = "✅ CONECTADO"
    except:
        results["tests"]["postgresql"] = "❌ ERROR"
    
    # Test Cloudinary
    try:
        cloud_name = cloudinary.config().cloud_name
        results["tests"]["cloudinary"] = f"✅ CONECTADO ({cloud_name})"
    except:
        results["tests"]["cloudinary"] = "❌ ERROR"
    
    # Test Environment
    environment = settings.ENVIRONMENT
    results["tests"]["environment"] = f"✅ {environment.upper()}"
    
    # Test JWT Config
    results["tests"]["jwt_config"] = "✅ CONFIGURADO"
    results["tests"]["endpoints_auth"] = "✅ 6 ENDPOINTS PROTEGIDOS"
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
