# 🚀 MIGRACIÓN A IMAGEKIT - PROGRESO

## ✅ COMPLETADO (86%)

### 1️⃣ **imagekit_service.py** - EXPANDIDO ✅
**Archivo:** `app/services/imagekit_service.py`

**Métodos agregados:**
- ✅ `upload_image()` - Subir imágenes con optimización opcional
- ✅ `upload_image_with_transformations()` - Subir con transformaciones específicas (avatares, thumbnails)
- ✅ `delete_image()` - Eliminar imágenes (alias de delete_video)
- ✅ `get_optimized_url()` - Generar URLs optimizadas con transformaciones
- ✅ `get_thumbnail_url()` - Generar URLs de thumbnails

**Características:**
- Soporte completo para imágenes y videos
- Transformaciones on-the-fly (width, height, quality, crop, format)
- URLs optimizadas con parámetros de ImageKit
- Logging detallado

---

### 2️⃣ **profiles.py** - MIGRADO ✅
**Archivo:** `app/api/v1/profiles.py`

**Cambios:**
- ✅ Eliminado import de Cloudinary
- ✅ Agregado import de `imagekit_service`
- ✅ Endpoint `/avatar` migrado a ImageKit
- ✅ Usa `upload_image_with_transformations()` con:
  - Width: 200px
  - Height: 200px
  - Crop: force
  - Quality: 90
  - Format: webp

**Resultado:**
- Avatar optimizado automáticamente
- Mejor performance (webp)
- Menor tamaño de archivo

---

### 3️⃣ **peleas_evento.py** - COMPLETADO ✅
**Archivo:** `app/api/v1/peleas_evento.py`

**Cambios:**
- ✅ Eliminado imports de Cloudinary
- ✅ CREATE: Ya usaba ImageKit, ahora guarda `file_id`
- ✅ UPDATE: Ya usaba ImageKit, ahora guarda `file_id` y elimina video anterior
- ✅ DELETE: Migrado de Cloudinary a ImageKit usando `file_id`

**Modelo actualizado:**
- ✅ `app/models/pelea_evento.py` - Agregado campo `file_id`

**Resultado:**
- Migración 100% completa para peleas de evento
- Eliminación correcta de videos al actualizar/eliminar

---

### 4️⃣ **peleas.py** - MIGRADO ✅
**Archivo:** `app/api/v1/peleas.py`

**Cambios:**
- ✅ Agregado campo `file_id` al modelo `Pelea`
- ✅ Eliminado import de Cloudinary
- ✅ CREATE: Migrado a ImageKit, guarda `file_id`
- ✅ UPDATE: Migrado a ImageKit, elimina video anterior
- ✅ DELETE: Migrado a ImageKit usando `file_id`

**Resultado:**
- Videos de peleas 100% en ImageKit
- Eliminación correcta de videos

---

### 5️⃣ **topes.py** - MIGRADO ✅
**Archivo:** `app/api/v1/topes.py`

**Cambios:**
- ✅ Agregado campo `file_id` al modelo `Tope`
- ✅ Eliminado import de Cloudinary
- ✅ CREATE: Migrado a ImageKit, guarda `file_id`
- ✅ UPDATE: Migrado a ImageKit, elimina video anterior
- ✅ DELETE: Migrado a ImageKit usando `file_id`

**Resultado:**
- Videos de topes 100% en ImageKit
- Mismo patrón que peleas

---

### 6️⃣ **pagos.py** - MIGRADO ✅
**Archivo:** `app/api/v1/pagos.py`

**Cambios:**
- ✅ Agregado campo `comprobante_file_id` al modelo `PagoPendiente`
- ✅ Eliminado import de Cloudinary
- ✅ Upload comprobante base64: Migrado a ImageKit
- ✅ Upload comprobante archivo: Migrado a ImageKit
- ✅ Guarda `comprobante_file_id` en ambos casos

**Resultado:**
- Comprobantes de pago 100% en ImageKit

---

## 🔄 EN PROGRESO

---

### 7️⃣ **gallos_con_pedigri.py** - Imágenes de gallos
**Prioridad:** 🔴 CRÍTICA
**Estimado:** 45 minutos

**Tareas:**
- [ ] Crear tabla `gallo_imagenes` con campos:
  - `id`, `gallo_id`, `url`, `file_id`, `orden`, `es_principal`
- [ ] Migrar `CloudinaryService` a `imagekit_service`
- [ ] Actualizar CREATE para múltiples imágenes
- [ ] Actualizar UPDATE para múltiples imágenes
- [ ] Actualizar DELETE para eliminar todas las imágenes
- [ ] Migrar fotos de padre/madre

---

## 📊 ESTADÍSTICAS

### Archivos Migrados: 6/7 (86%)
- ✅ imagekit_service.py (expandido)
- ✅ profiles.py (avatar)
- ✅ peleas_evento.py (videos)
- ✅ peleas.py (videos)
- ✅ topes.py (videos)
- ✅ pagos.py (comprobantes)

### Archivos Pendientes: 1/7 (14%)
- ⏳ gallos_con_pedigri.py (imágenes múltiples - el más complejo)

### Tiempo Estimado Restante: ~45 minutos

---

## 🎯 PRÓXIMOS PASOS

### Orden de Ejecución:
1. **peleas.py** (15 min) - Mismo patrón que peleas_evento
2. **topes.py** (15 min) - Mismo patrón que peleas_evento
3. **pagos.py** (20 min) - Comprobantes de pago
4. **gallos_con_pedigri.py** (45 min) - El más complejo (múltiples imágenes)

---

## 🧪 TESTING NECESARIO

Después de completar la migración, probar:

### Tests Manuales:
```bash
# 1. Profiles - Avatar
curl -X POST http://localhost:8000/api/v1/profiles/avatar \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@avatar.jpg"

# 2. Peleas Evento - Video
curl -X POST http://localhost:8000/api/v1/peleas-evento/1/peleas \
  -H "Authorization: Bearer TOKEN" \
  -F "video=@pelea.mp4" \
  -F "numero_pelea=1" \
  -F "titulo_pelea=Test"

# 3. Peleas - Video
curl -X POST http://localhost:8000/api/v1/peleas \
  -H "Authorization: Bearer TOKEN" \
  -F "video=@pelea.mp4" \
  -F "gallo_id=1"

# 4. Topes - Video
curl -X POST http://localhost:8000/api/v1/topes \
  -H "Authorization: Bearer TOKEN" \
  -F "video=@tope.mp4" \
  -F "gallo_id=1"

# 5. Pagos - Comprobante
curl -X POST http://localhost:8000/api/v1/pagos/1/subir-comprobante \
  -H "Authorization: Bearer TOKEN" \
  -F "comprobante=@comprobante.jpg"

# 6. Gallos - Imágenes
curl -X POST http://localhost:8000/api/v1/gallos-con-pedigri/con-pedigri \
  -H "Authorization: Bearer TOKEN" \
  -F "foto_principal=@gallo.jpg" \
  -F "nombre=Test Gallo"
```

### Tests Automatizados:
```python
# tests/integration/test_imagekit_migration.py
import pytest
from fastapi.testclient import TestClient

def test_upload_avatar(client, auth_headers):
    """Test subir avatar a ImageKit"""
    with open("test_avatar.jpg", "rb") as f:
        response = client.post(
            "/api/v1/profiles/avatar",
            headers=auth_headers,
            files={"file": f}
        )
    assert response.status_code == 200
    assert "avatar_url" in response.json()

def test_upload_pelea_video(client, auth_headers):
    """Test subir video de pelea a ImageKit"""
    with open("test_video.mp4", "rb") as f:
        response = client.post(
            "/api/v1/peleas",
            headers=auth_headers,
            files={"video": f},
            data={"gallo_id": 1}
        )
    assert response.status_code == 200
    assert response.json()["video_url"] is not None
```

---

## ✅ CHECKLIST DE MIGRACIÓN

### Por cada archivo:
- [ ] Agregar campo `file_id` al modelo (si no existe)
- [ ] Crear migración Alembic para agregar columna
- [ ] Eliminar imports de Cloudinary
- [ ] Agregar import de `imagekit_service`
- [ ] Migrar CREATE a ImageKit
- [ ] Migrar UPDATE a ImageKit
- [ ] Migrar DELETE a ImageKit
- [ ] Guardar `file_id` en todos los uploads
- [ ] Usar `file_id` para eliminar archivos
- [ ] Probar con curl/Postman
- [ ] Verificar logs de ImageKit
- [ ] Confirmar que archivos se suben correctamente
- [ ] Confirmar que archivos se eliminan correctamente

---

## 🔧 MIGRACIONES ALEMBIC NECESARIAS

### 1. Pelea (peleas)
```sql
ALTER TABLE peleas ADD COLUMN file_id VARCHAR(255);
```

### 2. Tope (topes)
```sql
ALTER TABLE topes ADD COLUMN file_id VARCHAR(255);
```

### 3. PagoPendiente (pagos_pendientes)
```sql
ALTER TABLE pagos_pendientes ADD COLUMN comprobante_file_id VARCHAR(255);
```

### 4. GalloImagen (nueva tabla)
```sql
CREATE TABLE gallo_imagenes (
    id SERIAL PRIMARY KEY,
    gallo_id INTEGER REFERENCES gallos_simples(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    file_id VARCHAR(255) NOT NULL,
    orden INTEGER DEFAULT 0,
    es_principal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📝 NOTAS IMPORTANTES

### Diferencias Cloudinary vs ImageKit:

**Cloudinary:**
```python
# Upload
upload_result = cloudinary.uploader.upload(
    file.file,
    folder="galloapp/avatars",
    public_id=f"avatar_{user_id}",
    transformation=[{"width": 200, "height": 200}]
)
url = upload_result["secure_url"]

# Delete
cloudinary.uploader.destroy(public_id, resource_type="video")
```

**ImageKit:**
```python
# Upload
file_content = await file.read()
upload_result = imagekit_service.upload_image_with_transformations(
    file_content=file_content,
    file_name=f"avatar_{user_id}_{file.filename}",
    folder="galloapp/avatars",
    width=200,
    height=200,
    crop="force",
    format="webp"
)
url = upload_result["url"]
file_id = upload_result["file_id"]  # ¡IMPORTANTE GUARDAR!

# Delete
imagekit_service.delete_image(file_id)
```

### Ventajas de ImageKit:
- ✅ Transformaciones on-the-fly en URL
- ✅ Mejor performance con CDN global
- ✅ Soporte nativo para webp
- ✅ Optimización automática
- ✅ Menor costo que Cloudinary

---

**Documento creado:** 2025-11-15
**Última actualización:** 2025-11-15 09:50 AM
**Estado:** 🔄 En progreso - 43% completado
