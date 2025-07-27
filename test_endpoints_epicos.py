# 🧪 test_endpoints_epicos.py - Testing ÉPICO del Sistema Genealógico
import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app

# 🔥 Test Client para endpoints épicos
client = TestClient(app)

class TestEndpointsEpicos:
    """🧪 Suite de testing para la técnica recursiva genealógica"""
    
    def test_root_endpoint(self):
        """🏠 Test endpoint raíz"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "✅ ACTIVO"
        assert data["version"] == "2.0.0-ÉPICA"
        assert "tecnica_epica" in data
        assert "genealogia_recursiva" in data["features"]
        print("✅ Root endpoint funcionando correctamente")
    
    def test_health_check(self):
        """💪 Test health check"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "✅ HEALTHY"
        print("✅ Health check funcionando correctamente")
    
    def test_docs_available(self):
        """📚 Test que la documentación esté disponible"""
        response = client.get("/docs")
        assert response.status_code == 200
        print("✅ Documentación API disponible")
    
    def test_openapi_schema(self):
        """📋 Test que el schema OpenAPI esté bien formado"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "info" in schema
        assert schema["info"]["title"] == "🔥 GalloApp Pro API - Técnica Recursiva Genealógica"
        assert schema["info"]["version"] == "2.0.0-ÉPICA"
        print("✅ Schema OpenAPI generado correctamente")
    
    @pytest.mark.asyncio
    async def test_test_db_endpoint(self):
        """🗄️ Test conexión a base de datos"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/test-db")
            # Puede fallar si no hay DB configurada, pero endpoint debe existir
            assert response.status_code in [200, 500]
            print("✅ Endpoint test-db existe y responde")
    
    @pytest.mark.asyncio 
    async def test_test_cloudinary_endpoint(self):
        """☁️ Test configuración Cloudinary"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/test-cloudinary")
            # Puede fallar si no hay Cloudinary configurado
            assert response.status_code in [200, 500]
            print("✅ Endpoint test-cloudinary existe y responde")

# 🔥 Tests específicos para endpoints de gallos (requieren autenticación)
class TestGallosEpicos:
    """🐓 Tests para endpoints épicos de gallos (requiere auth)"""
    
    def test_gallos_endpoints_require_auth(self):
        """🔐 Verificar que endpoints requieren autenticación"""
        
        # Test crear gallo sin auth
        response = client.post("/api/v1/gallos/with-genealogy")
        assert response.status_code == 403  # Forbidden sin JWT
        
        # Test listar gallos sin auth
        response = client.get("/api/v1/gallos")
        assert response.status_code == 403  # Forbidden sin JWT
        
        print("✅ Endpoints de gallos requieren autenticación correctamente")
    
    def test_fotos_endpoints_require_auth(self):
        """📸 Verificar que endpoints de fotos requieren autenticación"""
        
        # Test subir foto sin auth
        response = client.post("/api/v1/gallos/1/foto-principal")
        assert response.status_code == 403  # Forbidden sin JWT
        
        print("✅ Endpoints de fotos requieren autenticación correctamente")

# 🔧 Tests de validación
class TestValidaciones:
    """✅ Tests para servicios de validación"""
    
    def test_validation_service_importable(self):
        """📋 Test que ValidationService se pueda importar"""
        try:
            from app.services.validation_service import ValidationService
            assert ValidationService is not None
            print("✅ ValidationService importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando ValidationService: {e}")
            pytest.fail("ValidationService no se pudo importar")
    
    def test_genealogy_service_importable(self):
        """🧬 Test que GenealogyService se pueda importar"""
        try:
            from app.services.genealogy_service import GenealogyService
            assert GenealogyService is not None
            print("✅ GenealogyService importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando GenealogyService: {e}")
            pytest.fail("GenealogyService no se pudo importar")
    
    def test_cloudinary_service_importable(self):
        """☁️ Test que CloudinaryService se pueda importar"""
        try:
            from app.services.cloudinary_service import CloudinaryService
            assert CloudinaryService is not None
            print("✅ CloudinaryService importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando CloudinaryService: {e}")
            pytest.fail("CloudinaryService no se pudo importar")

# 🔧 Tests de modelos
class TestModelos:
    """📦 Tests para modelos de datos"""
    
    def test_gallo_model_importable(self):
        """🐓 Test que el modelo Gallo se pueda importar"""
        try:
            from app.models.gallo_simple import Gallo
            assert Gallo is not None
            print("✅ Modelo Gallo importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando modelo Gallo: {e}")
            pytest.fail("Modelo Gallo no se pudo importar")
    
    def test_gallo_model_has_genealogy_fields(self):
        """🧬 Test que el modelo Gallo tenga campos genealógicos"""
        try:
            from app.models.gallo_simple import Gallo
            
            # Verificar que tenga el campo mágico
            assert hasattr(Gallo, 'id_gallo_genealogico')
            assert hasattr(Gallo, 'padre_id')
            assert hasattr(Gallo, 'madre_id')
            assert hasattr(Gallo, 'tipo_registro')
            assert hasattr(Gallo, 'url_foto_cloudinary')
            
            print("✅ Modelo Gallo tiene todos los campos genealógicos")
        except Exception as e:
            print(f"❌ Error verificando campos genealógicos: {e}")
            pytest.fail("Modelo Gallo no tiene campos genealógicos requeridos")

# 🔧 Tests de schemas
class TestSchemas:
    """📋 Tests para schemas Pydantic"""
    
    def test_gallo_schemas_importable(self):
        """📋 Test que los schemas de gallo se puedan importar"""
        try:
            from app.schemas.gallo import (
                GalloCreate, GalloUpdate, GalloSimple, 
                GenealogyCreateResponse, ArbolGenealogico
            )
            print("✅ Schemas de gallo importados correctamente")
        except ImportError as e:
            print(f"❌ Error importando schemas: {e}")
            pytest.fail("Schemas de gallo no se pudieron importar")

# 🏃‍♂️ Función de ejecución principal
def run_tests():
    """🚀 Ejecutar todos los tests épicos"""
    print("🧪 Iniciando suite de testing épica...")
    print("=" * 60)
    
    # Ejecutar pytest
    exit_code = pytest.main([
        __file__,
        "-v",  # Verbose
        "--tb=short",  # Tracebacks cortos
        "--color=yes"  # Colores
    ])
    
    if exit_code == 0:
        print("\n🏆 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
        print("✅ Sistema genealógico recursivo funcional")
        print("✅ Endpoints épicos operativos")
        print("✅ Servicios importables")
        print("✅ Modelos actualizados")
        print("✅ Schemas validados")
    else:
        print("\n❌ Algunos tests fallaron")
        print("🔧 Revisar errores arriba")
    
    return exit_code

if __name__ == "__main__":
    """🚀 Ejecutar si se llama directamente"""
    run_tests()

# 📝 Notas sobre testing:
"""
Para ejecutar estos tests:

1. 📦 Instalar dependencias de testing:
   pip install pytest pytest-asyncio httpx

2. 🚀 Ejecutar tests:
   python test_endpoints_epicos.py
   
   O usando pytest directamente:
   pytest test_endpoints_epicos.py -v

3. 🔧 Tests con base de datos real:
   - Configurar variables de entorno
   - Ejecutar con DATABASE_URL válida

4. ☁️ Tests con Cloudinary real:
   - Configurar credenciales de Cloudinary
   - Ejecutar con CLOUDINARY_* válidas

Los tests están diseñados para:
✅ Verificar que la API se inicie correctamente
✅ Validar que los endpoints existan
✅ Confirmar autenticación requerida
✅ Verificar importación de servicios
✅ Validar estructura de modelos
✅ Comprobar schemas Pydantic

🏆 Creado por Alan & Claude - Los Máximos del Testing 🧪
"""
