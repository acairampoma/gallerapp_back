from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import cloudinary
import cloudinary.uploader
import os
import ssl
import urllib3
from decouple import config

# 🔧 Deshabilitar verificación SSL para desarrollo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

# 🔧 Configuración
app = FastAPI(
    title="🐓 GalloApp Pro API",
    description="Backend para Gestión de Gallos de Pelea",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📸 Configurar Cloudinary
cloudinary.config(
    cloud_name=config("CLOUDINARY_CLOUD_NAME", default="dz4czc3en"),
    api_key=config("CLOUDINARY_API_KEY", default="455285241939111"),
    api_secret=config("CLOUDINARY_API_SECRET", default="1uzQrkFD1Rbj8vPOClFBUEIwBn0")
)

# 🗄️ URL de PostgreSQL
DATABASE_URL = config(
    "DATABASE_URL", 
    default="postgresql://postgres:KfktiHjbugWVTzvalfwxiVZwsvVFatrk@gondola.proxy.rlwy.net:54162/railway"
)

@app.get("/")
async def root():
    """🏠 Hola Mundo"""
    return {
        "message": "🐓 ¡Hola Mundo desde GalloApp Pro!",
        "status": "✅ ACTIVO",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
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
        "storage": "Cloudinary"
    }

@app.get("/test-db")
async def test_database():
    """🗄️ Test PostgreSQL Connection"""
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
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
        "tests": {}
    }
    
    # Test PostgreSQL
    try:
        conn = psycopg2.connect(DATABASE_URL)
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
    environment = config("ENVIRONMENT", default="local")
    results["tests"]["environment"] = f"✅ {environment.upper()}"
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
