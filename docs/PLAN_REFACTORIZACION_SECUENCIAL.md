# 🚀 PLAN DE REFACTORIZACIÓN SECUENCIAL - BACKEND COMPLETO

## 🎯 OBJETIVO
Refactorizar TODO el backend aplicando mejores prácticas:
- ✅ Separación de responsabilidades (API → Service → Model)
- ✅ SQLAlchemy ORM (eliminar SQL RAW)
- ✅ Type hints completos
- ✅ Testing masivo automatizado
- ✅ Documentación clara

---

## 📊 ORDEN SECUENCIAL DE REFACTORIZACIÓN

### 🔴 FASE 1: ARCHIVOS CRÍTICOS (Prioridad URGENTE)

#### 1️⃣ **marketplace.py** (808 líneas → ~200 líneas)
**Razón:** Ya está documentado, es el warm-up perfecto

**Pasos:**
1. [ ] Crear `app/services/marketplace_service.py`
2. [ ] Migrar método `listar_publicaciones_publicas()` a ORM
3. [ ] Migrar método `listar_mis_publicaciones()` a ORM
4. [ ] Migrar método `crear_publicacion()` a ORM
5. [ ] Migrar método `actualizar_publicacion()` a ORM
6. [ ] Migrar método `eliminar_publicacion()` a ORM
7. [ ] Migrar método `toggle_favorito()` a ORM
8. [ ] Migrar método `listar_favoritos()` a ORM
9. [ ] Migrar método `verificar_limites_marketplace()` a ORM
10. [ ] Migrar método `obtener_estadisticas()` a ORM
11. [ ] Actualizar todos los endpoints para usar el service
12. [ ] Tests unitarios del service
13. [ ] Tests de integración de endpoints

**Archivos a crear:**
- `app/services/marketplace_service.py` (nuevo)
- `tests/services/test_marketplace_service.py` (nuevo)
- `tests/api/test_marketplace_endpoints.py` (nuevo)

**Archivos a modificar:**
- `app/api/v1/marketplace.py` (reducir de 808 a ~200 líneas)

---

#### 2️⃣ **vacunas.py + vacunas_simple.py** (953 líneas → ~200 líneas)
**Razón:** Código duplicado, fácil de consolidar

**Pasos:**
1. [ ] Crear `app/services/vacuna_service.py`
2. [ ] Migrar método `obtener_estadisticas()` a ORM
3. [ ] Migrar método `obtener_proximas_vacunas()` a ORM
4. [ ] Migrar método `listar_vacunas()` a ORM
5. [ ] Migrar método `crear_vacuna()` a ORM
6. [ ] Migrar método `actualizar_vacuna()` a ORM
7. [ ] Migrar método `eliminar_vacuna()` a ORM
8. [ ] Migrar método `registro_masivo()` a ORM
9. [ ] Migrar método `obtener_historial_gallo()` a ORM
10. [ ] Consolidar `vacunas_simple.py` en `vacunas.py`
11. [ ] Actualizar endpoints
12. [ ] Tests completos

**Archivos a crear:**
- `app/services/vacuna_service.py` (nuevo)
- `tests/services/test_vacuna_service.py` (nuevo)

**Archivos a modificar:**
- `app/api/v1/vacunas.py` (reducir de 603 a ~150 líneas)
- `app/api/v1/vacunas_simple.py` (eliminar o consolidar)

---

#### 3️⃣ **reportes.py** (372 líneas → ~100 líneas)
**Razón:** Queries complejos pero bien definidos

**Pasos:**
1. [ ] Crear `app/services/reporte_service.py`
2. [ ] Encapsular función PostgreSQL `get_dashboard_filtrado()`
3. [ ] Migrar método `obtener_dashboard()` a service
4. [ ] Migrar método `obtener_ranking()` a service (mantener CTEs)
5. [ ] Migrar método `obtener_estadisticas_generales()` a service
6. [ ] Actualizar endpoints
7. [ ] Tests completos

**Archivos a crear:**
- `app/services/reporte_service.py` (nuevo)
- `tests/services/test_reporte_service.py` (nuevo)

**Archivos a modificar:**
- `app/api/v1/reportes.py` (reducir de 372 a ~100 líneas)

---

#### 4️⃣ **gallos_con_pedigri.py** (2,278 líneas → ~300 líneas)
**Razón:** El monstruo más grande, requiere múltiples services

**Pasos:**
1. [ ] Crear `app/services/gallo_service.py`
2. [ ] Crear `app/services/pedigri_service.py`
3. [ ] Crear `app/services/foto_gallo_service.py`
4. [ ] Migrar método `listar_gallos()` a ORM
5. [ ] Migrar método `obtener_gallo()` a ORM
6. [ ] Migrar método `crear_gallo()` a ORM
7. [ ] Migrar método `actualizar_gallo()` a ORM
8. [ ] Migrar método `eliminar_gallo()` a ORM
9. [ ] Migrar método `crear_con_pedigri()` a PedigriService
10. [ ] Migrar método `actualizar_con_pedigri()` a PedigriService
11. [ ] Migrar método `obtener_arbol_genealogico()` a PedigriService
12. [ ] Migrar método `generar_pdf_pedigri()` a PedigriService
13. [ ] Migrar método `subir_fotos()` a FotoGalloService
14. [ ] Migrar método `eliminar_fotos()` a FotoGalloService
15. [ ] Actualizar todos los endpoints
16. [ ] Tests completos

**Archivos a crear:**
- `app/services/gallo_service.py` (nuevo)
- `app/services/pedigri_service.py` (nuevo)
- `app/services/foto_gallo_service.py` (nuevo)
- `tests/services/test_gallo_service.py` (nuevo)
- `tests/services/test_pedigri_service.py` (nuevo)

**Archivos a modificar:**
- `app/api/v1/gallos_con_pedigri.py` (reducir de 2,278 a ~300 líneas)

---

### 🟡 FASE 2: ARCHIVOS MEDIANOS (Prioridad ALTA)

#### 5️⃣ **fotos_final.py** (163 líneas → ~50 líneas)
**Pasos:**
1. [ ] Migrar a ImageKit (parte del plan existente)
2. [ ] Usar `FotoGalloService` creado en paso 4
3. [ ] Actualizar endpoints
4. [ ] Tests

**Archivos a modificar:**
- `app/api/v1/fotos_final.py` (reducir y migrar a ImageKit)

---

#### 6️⃣ **admin.py** (553 líneas → ~200 líneas)
**Pasos:**
1. [ ] Crear `app/services/admin_service.py`
2. [ ] Migrar lógica de administración
3. [ ] Migrar gestión de usuarios
4. [ ] Migrar gestión de pagos
5. [ ] Actualizar endpoints
6. [ ] Tests

**Archivos a crear:**
- `app/services/admin_service.py` (nuevo)

**Archivos a modificar:**
- `app/api/v1/admin.py` (reducir de 553 a ~200 líneas)

---

#### 7️⃣ **transmisiones.py** (413 líneas → ~150 líneas)
**Pasos:**
1. [ ] Crear `app/services/transmision_service.py`
2. [ ] Migrar lógica de transmisiones
3. [ ] Actualizar endpoints
4. [ ] Tests

**Archivos a crear:**
- `app/services/transmision_service.py` (nuevo)

**Archivos a modificar:**
- `app/api/v1/transmisiones.py` (reducir de 413 a ~150 líneas)

---

### 🟢 FASE 3: ARCHIVOS BUENOS (Revisar y optimizar)

#### 8️⃣ **peleas.py** (599 líneas)
**Estado:** ✅ Ya usa ORM correctamente
**Acción:** Solo migrar a ImageKit para videos

#### 9️⃣ **topes.py** (542 líneas)
**Estado:** ✅ Ya usa ORM correctamente
**Acción:** Solo migrar a ImageKit para videos

#### 🔟 **peleas_evento.py** (592 líneas)
**Estado:** ✅ Ya usa ImageKit parcialmente
**Acción:** Completar migración (DELETE)

#### 1️⃣1️⃣ **pagos.py** (519 líneas)
**Estado:** ✅ Buena estructura
**Acción:** Migrar comprobantes a ImageKit

#### 1️⃣2️⃣ **suscripciones.py** (487 líneas)
**Estado:** ✅ Ya usa LimiteService
**Acción:** Ninguna (ya está bien)

#### 1️⃣3️⃣ **profiles.py** (92 líneas)
**Estado:** ✅ Pequeño y simple
**Acción:** Migrar avatar a ImageKit

---

## 🧪 PARTE 2: TESTING MASIVO AUTOMATIZADO

### 🐍 **OPCIONES DE TESTING EN PYTHON**

#### 1. **pytest + pytest-asyncio** (RECOMENDADO)
**Por qué:**
- ✅ Estándar de facto en Python
- ✅ Soporte async/await nativo
- ✅ Fixtures poderosos
- ✅ Plugins para FastAPI

**Instalación:**
```bash
pip install pytest pytest-asyncio httpx pytest-cov
```

**Ejemplo:**
```python
# tests/services/test_marketplace_service.py
import pytest
from app.services.marketplace_service import MarketplaceService

@pytest.mark.asyncio
async def test_listar_publicaciones(db_session):
    publicaciones = MarketplaceService.listar_publicaciones_publicas(
        db=db_session,
        filtros=None,
        skip=0,
        limit=20
    )
    assert len(publicaciones) >= 0
```

---

#### 2. **Tavern** (API Testing - Similar a Karate)
**Por qué:**
- ✅ Testing declarativo con YAML
- ✅ Similar a Karate de Java
- ✅ Ideal para APIs REST
- ✅ Validación de schemas

**Instalación:**
```bash
pip install tavern
```

**Ejemplo:**
```yaml
# tests/tavern/test_marketplace.yaml
test_name: Test listar publicaciones

stages:
  - name: Listar publicaciones públicas
    request:
      url: http://localhost:8000/api/v1/marketplace/publicaciones
      method: GET
      headers:
        Authorization: "Bearer {token}"
    response:
      status_code: 200
      json:
        success: true
        data:
          publicaciones: !anything
```

---

#### 3. **Locust** (Load Testing)
**Por qué:**
- ✅ Testing de carga
- ✅ Simula miles de usuarios
- ✅ Métricas en tiempo real

**Instalación:**
```bash
pip install locust
```

**Ejemplo:**
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class MarketplaceUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def listar_publicaciones(self):
        self.client.get("/api/v1/marketplace/publicaciones")
    
    @task(3)
    def ver_mis_publicaciones(self):
        self.client.get("/api/v1/marketplace/mis-publicaciones")
```

---

#### 4. **Schemathesis** (Property-based Testing)
**Por qué:**
- ✅ Testing automático desde OpenAPI
- ✅ Genera tests automáticamente
- ✅ Encuentra edge cases

**Instalación:**
```bash
pip install schemathesis
```

**Ejemplo:**
```python
import schemathesis

schema = schemathesis.from_uri("http://localhost:8000/openapi.json")

@schema.parametrize()
def test_api(case):
    case.call_and_validate()
```

---

### 🎯 **ESTRATEGIA DE TESTING RECOMENDADA**

```
tests/
├── unit/                          # Tests unitarios (pytest)
│   ├── services/
│   │   ├── test_marketplace_service.py
│   │   ├── test_gallo_service.py
│   │   ├── test_vacuna_service.py
│   │   └── test_reporte_service.py
│   └── models/
│       └── test_models.py
│
├── integration/                   # Tests de integración (pytest)
│   ├── api/
│   │   ├── test_marketplace_endpoints.py
│   │   ├── test_gallos_endpoints.py
│   │   └── test_vacunas_endpoints.py
│   └── database/
│       └── test_db_operations.py
│
├── e2e/                          # Tests end-to-end (Tavern)
│   ├── test_marketplace_flow.yaml
│   ├── test_gallo_creation_flow.yaml
│   └── test_subscription_flow.yaml
│
├── load/                         # Tests de carga (Locust)
│   └── locustfile.py
│
└── contract/                     # Contract testing (Schemathesis)
    └── test_openapi_contract.py
```

---

## 🔧 **CONFIGURACIÓN DE TESTING**

### 1. **pytest.ini**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = 
    -v
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --tb=short
```

### 2. **conftest.py** (Fixtures globales)
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from fastapi.testclient import TestClient

# Database de prueba
SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@localhost/test_db"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    # Login y obtener token
    response = client.post("/api/v1/auth/login", json={
        "email": "test@test.com",
        "password": "test123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

---

## 📝 **EJEMPLO COMPLETO DE TEST**

### Test Unitario (Service)
```python
# tests/unit/services/test_marketplace_service.py
import pytest
from app.services.marketplace_service import MarketplaceService
from app.models.marketplace import MarketplacePublicacion
from app.schemas.marketplace import MarketplaceFiltros

class TestMarketplaceService:
    
    def test_listar_publicaciones_sin_filtros(self, db_session):
        """Test listar todas las publicaciones sin filtros"""
        resultado = MarketplaceService.listar_publicaciones_publicas(
            db=db_session,
            filtros=MarketplaceFiltros(),
            skip=0,
            limit=20
        )
        
        assert "publicaciones" in resultado
        assert "total" in resultado
        assert isinstance(resultado["publicaciones"], list)
    
    def test_listar_publicaciones_con_filtro_precio(self, db_session):
        """Test filtrar por rango de precio"""
        filtros = MarketplaceFiltros(
            precio_min=100,
            precio_max=500
        )
        
        resultado = MarketplaceService.listar_publicaciones_publicas(
            db=db_session,
            filtros=filtros,
            skip=0,
            limit=20
        )
        
        for pub in resultado["publicaciones"]:
            assert 100 <= pub["precio"] <= 500
    
    def test_crear_publicacion_valida(self, db_session, test_user, test_gallo):
        """Test crear publicación válida"""
        from app.schemas.marketplace import MarketplacePublicacionCreate
        
        data = MarketplacePublicacionCreate(
            gallo_id=test_gallo.id,
            precio=250.00,
            estado="venta"
        )
        
        resultado = MarketplaceService.crear_publicacion(
            db=db_session,
            user_id=test_user.id,
            publicacion_data=data
        )
        
        assert resultado["publicacion_id"] is not None
        assert resultado["precio"] == 250.00
    
    def test_crear_publicacion_sin_permisos(self, db_session, test_user):
        """Test crear publicación de gallo que no es del usuario"""
        from app.schemas.marketplace import MarketplacePublicacionCreate
        
        data = MarketplacePublicacionCreate(
            gallo_id=999,  # Gallo que no existe o no es del usuario
            precio=250.00,
            estado="venta"
        )
        
        with pytest.raises(ValueError, match="Gallo no encontrado"):
            MarketplaceService.crear_publicacion(
                db=db_session,
                user_id=test_user.id,
                publicacion_data=data
            )
```

---

### Test de Integración (API)
```python
# tests/integration/api/test_marketplace_endpoints.py
import pytest
from fastapi.testclient import TestClient

class TestMarketplaceEndpoints:
    
    def test_get_publicaciones_sin_auth(self, client):
        """Las publicaciones públicas no requieren auth"""
        response = client.get("/api/v1/marketplace/publicaciones")
        
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_get_mis_publicaciones_con_auth(self, client, auth_headers):
        """Mis publicaciones requieren autenticación"""
        response = client.get(
            "/api/v1/marketplace/mis-publicaciones",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "publicaciones" in response.json()["data"]
    
    def test_crear_publicacion_completo(self, client, auth_headers, test_gallo):
        """Test flujo completo de creación"""
        data = {
            "gallo_id": test_gallo.id,
            "precio": 350.50,
            "estado": "venta"
        }
        
        response = client.post(
            "/api/v1/marketplace/publicaciones",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        publicacion_id = response.json()["data"]["publicacion_id"]
        
        # Verificar que se creó
        response = client.get(
            f"/api/v1/marketplace/publicaciones",
            headers=auth_headers
        )
        
        publicaciones = response.json()["data"]["publicaciones"]
        assert any(p["id"] == publicacion_id for p in publicaciones)
```

---

### Test E2E (Tavern)
```yaml
# tests/e2e/test_marketplace_flow.yaml
test_name: Flujo completo de marketplace

stages:
  - name: Login
    request:
      url: http://localhost:8000/api/v1/auth/login
      method: POST
      json:
        email: test@test.com
        password: test123
    response:
      status_code: 200
      save:
        json:
          access_token: access_token

  - name: Crear publicación
    request:
      url: http://localhost:8000/api/v1/marketplace/publicaciones
      method: POST
      headers:
        Authorization: "Bearer {access_token}"
      json:
        gallo_id: 1
        precio: 250.00
        estado: venta
    response:
      status_code: 200
      json:
        success: true
      save:
        json:
          publicacion_id: data.publicacion_id

  - name: Ver publicación creada
    request:
      url: http://localhost:8000/api/v1/marketplace/publicaciones
      method: GET
      headers:
        Authorization: "Bearer {access_token}"
    response:
      status_code: 200
      json:
        success: true
        data:
          publicaciones:
            - id: !int "{publicacion_id}"

  - name: Marcar como favorito
    request:
      url: "http://localhost:8000/api/v1/marketplace/publicaciones/{publicacion_id}/favorito"
      method: POST
      headers:
        Authorization: "Bearer {access_token}"
    response:
      status_code: 200
      json:
        success: true
        data:
          es_favorito: true
```

---

## 🚀 **COMANDOS DE TESTING**

### Tests Unitarios
```bash
# Todos los tests
pytest

# Solo tests unitarios
pytest tests/unit/

# Con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/unit/services/test_marketplace_service.py

# Tests con keyword
pytest -k "marketplace"

# Tests en paralelo (más rápido)
pytest -n auto
```

### Tests E2E (Tavern)
```bash
# Todos los tests E2E
pytest tests/e2e/

# Test específico
tavern-ci tests/e2e/test_marketplace_flow.yaml
```

### Tests de Carga (Locust)
```bash
# Iniciar Locust
locust -f tests/load/locustfile.py

# Headless (sin UI)
locust -f tests/load/locustfile.py --headless -u 100 -r 10 --run-time 1m
```

### Tests de Contrato (Schemathesis)
```bash
# Desde OpenAPI
schemathesis run http://localhost:8000/openapi.json

# Con checks específicos
schemathesis run http://localhost:8000/openapi.json --checks all
```

---

## 📊 **MÉTRICAS DE CALIDAD**

### Coverage Mínimo
- **Services:** 90%+
- **Endpoints:** 80%+
- **Models:** 70%+
- **Total:** 85%+

### Performance
- **Response time p95:** <500ms
- **Response time p99:** <1000ms
- **Throughput:** >100 req/s

---

## ✅ **CHECKLIST POR ARCHIVO**

Para cada archivo refactorizado:

- [ ] Service creado con lógica de negocio
- [ ] Endpoints actualizados (thin controllers)
- [ ] Tests unitarios del service (>90% coverage)
- [ ] Tests de integración de endpoints (>80% coverage)
- [ ] Test E2E del flujo principal (Tavern)
- [ ] Documentación actualizada
- [ ] Type hints completos
- [ ] Logging apropiado
- [ ] Manejo de errores consistente

---

## 🎯 **ORDEN DE EJECUCIÓN**

1. **Refactorizar archivo** (crear service, actualizar endpoints)
2. **Escribir tests** (unit + integration + e2e)
3. **Ejecutar tests** (verificar que todo pasa)
4. **Verificar coverage** (mínimo 85%)
5. **Code review** (verificar calidad)
6. **Merge** (a develop)
7. **Siguiente archivo**

---

**Documento creado:** 2025-11-15
**Estado:** 📋 Plan completo de refactorización + testing
**Prioridad:** 🔴 EJECUTAR AHORA
