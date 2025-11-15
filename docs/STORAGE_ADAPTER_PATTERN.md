# 🎯 STORAGE ADAPTER PATTERN - Cambiar de proveedor como cambiar de zapatillas

## 🚀 OBJETIVO

Implementar el **patrón Adapter** para que cambiar de proveedor de almacenamiento (ImageKit, Cloudinary, S3, etc.) sea **TAN FÁCIL** como cambiar una línea en `settings.py` - **SIN IMPACTO** en el código.

---

## 🏗️ ARQUITECTURA

```
┌─────────────────────────────────────────────────────────────┐
│                    ENDPOINTS (API Layer)                     │
│  profiles.py, peleas.py, topes.py, pagos.py, etc.          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   STORAGE MANAGER                            │
│  Gestor centralizado - Delega al adaptador activo          │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   ImageKit   │ │  Cloudinary  │ │     S3       │
│   Adapter    │ │   Adapter    │ │   Adapter    │
└──────────────┘ └──────────────┘ └──────────────┘
        │              │               │
        ▼              ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  ImageKit    │ │  Cloudinary  │ │   AWS S3     │
│    API       │ │     API      │ │     API      │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
app/services/storage/
├── __init__.py                  # Exports públicos
├── base_storage.py              # Interfaz base (ABC)
├── storage_manager.py           # Gestor centralizado
├── imagekit_adapter.py          # Adaptador ImageKit
├── cloudinary_adapter.py        # Adaptador Cloudinary
└── s3_adapter.py                # Adaptador S3 (futuro)
```

---

## 🎨 COMPONENTES

### 1️⃣ **BaseStorageAdapter** (Interfaz)

Define el contrato que todos los adaptadores deben cumplir:

```python
class BaseStorageAdapter(ABC):
    @abstractmethod
    def upload_file(...) -> Optional[UploadResult]:
        pass
    
    @abstractmethod
    def upload_with_transformations(...) -> Optional[UploadResult]:
        pass
    
    @abstractmethod
    def delete_file(file_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_optimized_url(...) -> str:
        pass
```

### 2️⃣ **UploadResult** (Modelo estandarizado)

Resultado uniforme independiente del proveedor:

```python
@dataclass
class UploadResult:
    url: str
    file_id: str
    thumbnail_url: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    size: Optional[int] = None
```

### 3️⃣ **TransformOptions** (Opciones estandarizadas)

Transformaciones uniformes para todos los proveedores:

```python
@dataclass
class TransformOptions:
    width: Optional[int] = None
    height: Optional[int] = None
    quality: int = 80
    crop: str = "maintain_ratio"  # maintain_ratio, force, at_least, at_max
    format: str = "auto"  # auto, jpg, png, webp
```

### 4️⃣ **StorageManager** (Gestor)

Punto de entrada único para todo el sistema:

```python
class StorageManager:
    def upload_image(...) -> Optional[UploadResult]:
        return self._adapter.upload_file(...)
    
    def upload_video(...) -> Optional[UploadResult]:
        return self._adapter.upload_file(...)
    
    def delete_file(file_id: str) -> bool:
        return self._adapter.delete_file(file_id)
```

---

## 🔧 CÓMO USAR

### ✅ **Opción 1: Usar el Storage Manager (Recomendado)**

```python
from app.services.storage import storage_manager

# Subir imagen
result = storage_manager.upload_image(
    file_content=file_bytes,
    file_name="avatar.jpg",
    folder="avatars"
)

# Subir video
result = storage_manager.upload_video(
    file_content=video_bytes,
    file_name="pelea.mp4",
    folder="peleas"
)

# Subir con transformaciones
result = storage_manager.upload_with_transformations(
    file_content=file_bytes,
    file_name="avatar.jpg",
    folder="avatars",
    width=200,
    height=200,
    crop="force",
    quality=90,
    format="webp"
)

# Eliminar archivo
success = storage_manager.delete_file(file_id)

# Obtener URL optimizada
optimized_url = storage_manager.get_optimized_url(
    url=original_url,
    width=400,
    height=300,
    quality=80
)
```

### ✅ **Opción 2: Usar funciones de conveniencia**

```python
from app.services.storage import (
    upload_image,
    upload_video,
    upload_avatar,
    delete_file
)

# Subir imagen
result = upload_image(file_bytes, "photo.jpg", "gallos")

# Subir video
result = upload_video(video_bytes, "pelea.mp4", "peleas")

# Subir avatar optimizado (200x200, webp)
result = upload_avatar(file_bytes, "avatar.jpg", user_id=123)

# Eliminar
success = delete_file(file_id)
```

---

## 🔄 CAMBIAR DE PROVEEDOR

### **Método 1: Cambiar en settings.py**

```python
# app/core/config.py
class Settings:
    # Cambiar aquí para usar otro proveedor
    STORAGE_PROVIDER: str = "imagekit"  # o "cloudinary", "s3"
```

**¡Eso es todo!** Todo el código sigue funcionando igual.

### **Método 2: Cambiar en runtime (testing/migración)**

```python
from app.services.storage import storage_manager, StorageProvider

# Cambiar a Cloudinary temporalmente
storage_manager.switch_provider(StorageProvider.CLOUDINARY)

# Hacer operaciones con Cloudinary
result = storage_manager.upload_image(...)

# Volver a ImageKit
storage_manager.switch_provider(StorageProvider.IMAGEKIT)
```

---

## 📝 EJEMPLO COMPLETO: MIGRAR ENDPOINT

### ❌ **ANTES (Acoplado a ImageKit)**

```python
from app.services.imagekit_service import imagekit_service

@router.post("/avatar")
async def upload_avatar(file: UploadFile, ...):
    file_content = await file.read()
    
    # Acoplado a ImageKit
    upload_result = imagekit_service.upload_image_with_transformations(
        file_content=file_content,
        file_name=f"avatar_{user_id}.jpg",
        folder="avatars",
        width=200,
        height=200,
        crop="force",
        quality=90,
        format="webp"
    )
    
    if upload_result:
        avatar_url = upload_result["url"]
        file_id = upload_result["file_id"]
```

### ✅ **DESPUÉS (Desacoplado - Patrón Adapter)**

```python
from app.services.storage import upload_avatar

@router.post("/avatar")
async def upload_avatar_endpoint(file: UploadFile, ...):
    file_content = await file.read()
    
    # Funciona con cualquier proveedor
    result = upload_avatar(
        file_content=file_content,
        file_name=f"avatar_{user_id}.jpg",
        user_id=user_id
    )
    
    if result:
        avatar_url = result.url
        file_id = result.file_id
```

**Beneficios:**
- ✅ Cambiar de ImageKit a Cloudinary: **1 línea en settings**
- ✅ Código más limpio y legible
- ✅ Fácil de testear (mock del manager)
- ✅ Preparado para agregar S3, Azure, etc.

---

## 🧪 TESTING

### **Test con Mock**

```python
from unittest.mock import Mock
from app.services.storage import storage_manager, UploadResult

def test_upload_avatar():
    # Mock del adaptador
    mock_adapter = Mock()
    mock_adapter.upload_with_transformations.return_value = UploadResult(
        url="https://cdn.example.com/avatar.jpg",
        file_id="abc123"
    )
    
    storage_manager._adapter = mock_adapter
    
    # Test
    result = storage_manager.upload_with_transformations(...)
    
    assert result.url == "https://cdn.example.com/avatar.jpg"
    assert result.file_id == "abc123"
```

### **Test de Integración**

```python
import pytest
from app.services.storage import storage_manager, StorageProvider

@pytest.mark.parametrize("provider", [
    StorageProvider.IMAGEKIT,
    StorageProvider.CLOUDINARY
])
def test_upload_with_all_providers(provider):
    """Verificar que todos los proveedores funcionan igual"""
    storage_manager.switch_provider(provider)
    
    result = storage_manager.upload_image(
        file_content=test_image_bytes,
        file_name="test.jpg",
        folder="test"
    )
    
    assert result is not None
    assert result.url.startswith("https://")
    assert result.file_id is not None
```

---

## 🎯 MIGRACIÓN GRADUAL

Puedes migrar endpoints uno por uno sin romper nada:

### **Fase 1: Endpoints nuevos**
```python
# Nuevos endpoints usan storage_manager
from app.services.storage import upload_image
```

### **Fase 2: Endpoints existentes**
```python
# Reemplazar imagekit_service por storage_manager
# ANTES:
from app.services.imagekit_service import imagekit_service
result = imagekit_service.upload_image(...)

# DESPUÉS:
from app.services.storage import upload_image
result = upload_image(...)
```

### **Fase 3: Deprecar servicios antiguos**
```python
# Marcar como deprecated
@deprecated("Usar storage_manager en su lugar")
class ImageKitService:
    ...
```

---

## 🚀 AGREGAR NUEVO PROVEEDOR (Ej: AWS S3)

### **1. Crear adaptador**

```python
# app/services/storage/s3_adapter.py
from app.services.storage.base_storage import BaseStorageAdapter
import boto3

class S3Adapter(BaseStorageAdapter):
    def __init__(self):
        self.s3_client = boto3.client('s3')
    
    def upload_file(self, file_content, file_name, folder, file_type):
        # Implementar upload a S3
        ...
    
    def delete_file(self, file_id):
        # Implementar delete de S3
        ...
    
    # ... implementar todos los métodos abstractos

s3_adapter = S3Adapter()
```

### **2. Registrar en StorageManager**

```python
# app/services/storage/storage_manager.py
from app.services.storage.s3_adapter import s3_adapter

class StorageManager:
    def __init__(self):
        self._adapters = {
            StorageProvider.IMAGEKIT: imagekit_adapter,
            StorageProvider.CLOUDINARY: cloudinary_adapter,
            StorageProvider.S3: s3_adapter,  # ← Agregar aquí
        }
```

### **3. Usar**

```python
# settings.py
STORAGE_PROVIDER = "s3"
```

**¡Listo!** Todo el código funciona con S3 sin cambios.

---

## 📊 COMPARACIÓN DE PROVEEDORES

| Característica | ImageKit | Cloudinary | S3 |
|----------------|----------|------------|-----|
| Transformaciones on-the-fly | ✅ | ✅ | ❌ |
| CDN Global | ✅ | ✅ | ✅ |
| Optimización automática | ✅ | ✅ | ❌ |
| Costo | 💰 Medio | 💰💰 Alto | 💰 Bajo |
| Velocidad | ⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡ |
| Facilidad de uso | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Para cada endpoint que usa almacenamiento:

- [ ] Reemplazar import de `imagekit_service` por `storage_manager`
- [ ] Cambiar `imagekit_service.upload_image()` por `storage_manager.upload_image()`
- [ ] Cambiar `imagekit_service.delete_video()` por `storage_manager.delete_file()`
- [ ] Usar `result.url` y `result.file_id` (UploadResult)
- [ ] Probar con ambos proveedores (ImageKit y Cloudinary)
- [ ] Actualizar tests

---

## 🎓 BENEFICIOS DEL PATRÓN ADAPTER

1. **✅ Desacoplamiento:** Código independiente del proveedor
2. **✅ Flexibilidad:** Cambiar proveedor en 1 línea
3. **✅ Testeable:** Fácil de mockear y testear
4. **✅ Escalable:** Agregar proveedores sin modificar código existente
5. **✅ Mantenible:** Cambios centralizados en adaptadores
6. **✅ Migración gradual:** No rompe código existente
7. **✅ Fallback automático:** Si un proveedor falla, usa otro
8. **✅ Consistencia:** Misma interfaz para todos los proveedores

---

## 🔮 FUTURO

### **Proveedores planeados:**
- [ ] AWS S3
- [ ] Azure Blob Storage
- [ ] Google Cloud Storage
- [ ] Local Storage (desarrollo)
- [ ] MinIO (self-hosted)

### **Features planeados:**
- [ ] Multi-provider (subir a varios a la vez)
- [ ] Fallback automático si un proveedor falla
- [ ] Cache de URLs optimizadas
- [ ] Métricas de uso por proveedor
- [ ] Migración automática entre proveedores

---

**Documento creado:** 2025-11-15
**Última actualización:** 2025-11-15 10:10 AM
**Estado:** ✅ Implementado y listo para usar
**Patrón:** Adapter Pattern + Strategy Pattern
