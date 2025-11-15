# 📸 Módulos con Cloudinary - Plan de Migración a ImageKit

## 🎯 Resumen Ejecutivo

**Total de módulos identificados:** 7
**Módulos que usan Cloudinary:** 6
**Módulos sin Cloudinary:** 1 (suscripciones.py - solo lógica)
**Estado actual:** 6 módulos requieren migración
**Objetivo:** Migrar todos a ImageKit

---

## 📋 Módulos Identificados

### 1. 🐓 **GALLOS CON PEDIGRÍ** (`gallos_con_pedigri.py`)
**Prioridad:** 🔴 CRÍTICA

**Uso actual:**
- Servicio: `CloudinaryService` (línea 13)
- Tipo: Imágenes de gallos (foto principal + adicionales)
- Carpeta: `galloapp/gallos/user_{user_id}`

**Endpoints afectados:**
- POST `/gallos-con-pedigri/con-pedigri` - Crear gallo con imágenes
- PUT `/gallos-con-pedigri/{gallo_id}` - Actualizar gallo con imágenes
- DELETE - Eliminar imágenes al borrar gallo

**Características especiales:**
- Múltiples imágenes por gallo
- Foto principal destacada
- Fotos adicionales en JSON
- Pedigrí con padre/madre (pueden tener fotos)

**Campos en BD:**
- `foto_principal_url`
- `url_foto_cloudinary` (optimizada)
- `fotos_adicionales` (JSON)

---

### 2. 🥊 **PELEAS** (`peleas.py`)
**Prioridad:** 🔴 CRÍTICA

**Uso actual:**
- Import: `cloudinary.uploader` (línea 8)
- Tipo: Videos de peleas
- Carpeta: `galloapp/peleas/user_{user_id}`

**Endpoints afectados:**
- POST `/peleas` - Crear pelea con video (líneas 357-365)
- PUT `/peleas/{pelea_id}` - Actualizar video (líneas 498-506)
- DELETE `/peleas/{pelea_id}` - Eliminar video (líneas 580-588)

**Patrón actual:**
```python
# CREATE/UPDATE
video_content = await video.read()
upload_result = cloudinary.uploader.upload(
    video_content,
    resource_type="video",
    folder=f"galloapp/peleas/user_{current_user_id}"
)
pelea.video_url = upload_result.get('secure_url')

# DELETE
public_id = '/'.join(parts[-2:]).split('.')[0]
cloudinary.uploader.destroy(public_id, resource_type="video")
```

---

### 3. 🏆 **TOPES** (`topes.py`)
**Prioridad:** 🔴 CRÍTICA

**Uso actual:**
- Import: `cloudinary.uploader` (línea 8)
- Tipo: Videos de topes
- Carpeta: `galloapp/topes/user_{user_id}`

**Endpoints afectados:**
- POST `/topes` - Crear tope con video (líneas 311-319)
- PUT `/topes/{tope_id}` - Actualizar video (líneas 439-447)
- DELETE `/topes/{tope_id}` - Eliminar video (líneas 521-529)

**Patrón:** Idéntico a Peleas

---

### 4. 🎬 **PELEAS DE EVENTO** (`peleas_evento.py`)
**Prioridad:** 🟡 MEDIA (Parcialmente migrado)

**Estado:**
- ✅ CREATE: Ya usa ImageKit (líneas 228-260)
- ✅ UPDATE: Ya usa ImageKit (líneas 438-470)
- ❌ DELETE: Todavía usa Cloudinary (líneas 675-686)

**Pendiente:**
```python
# LÍNEAS 675-686 - MIGRAR A IMAGEKIT
if pelea.video_url:
    try:
        public_id = pelea.video_url.split('/')[-1].split('.')[0]
        cloudinary.uploader.destroy(
            f"peleas_evento/{pelea.evento_id}/{public_id}",
            resource_type="video"
        )
```

**Debe cambiar a:**
```python
if pelea.file_id:  # Necesita guardar file_id en BD
    success = imagekit_service.delete_video(pelea.file_id)
```

---

### 5. 👤 **PROFILES** (`profiles.py`)
**Prioridad:** 🟡 MEDIA

**Uso actual:**
- Import: `cloudinary`, `cloudinary.uploader` (líneas 8-9)
- Config: Configuración explícita (líneas 15-19)
- Tipo: Avatar de usuario (imagen única)
- Carpeta: `galloapp/avatars`

**Endpoints afectados:**
- POST `/profiles/avatar` - Subir avatar (líneas 42-70)
- DELETE `/profiles/avatar` - Eliminar avatar (líneas 89-99)

**Patrón actual:**
```python
# UPLOAD (líneas 52-60)
upload_result = cloudinary.uploader.upload(
    file.file,
    folder="galloapp/avatars",
    public_id=f"avatar_user_{current_user_id}",
    overwrite=True,
    transformation=[
        {"width": 200, "height": 200, "crop": "fill", "quality": "auto", "format": "webp"}
    ]
)

# Guardar URL
avatar_url = upload_result["secure_url"]
ProfileService.update_avatar(db, current_user_id, avatar_url)

# DELETE (líneas 96-97)
ProfileService.update_avatar(db, current_user_id, None)
# ⚠️ NO elimina de Cloudinary, solo pone None en BD
```

**Características especiales:**
- Transformaciones automáticas (200x200, crop fill, webp)
- Public ID fijo por usuario (sobrescribe anterior con `overwrite=True`)
- DELETE no elimina archivo de Cloudinary (solo BD)
- Optimización automática de calidad y formato

**Campos en BD:**
- `avatar_url` en tabla `profiles`

---

### 6. 💳 **PAGOS/SUSCRIPCIONES** (`pagos.py`)
**Prioridad:** 🟢 BAJA

**Uso actual:**
- Import: `cloudinary.uploader` (línea 9)
- Tipo: Comprobantes de pago (imágenes)
- Carpeta: `galloapp/pagos/comprobantes/user_{user_id}`

**Endpoints afectados:**
- POST `/pagos/generar-qr` - Subir comprobante base64 (líneas 170-180)
- POST `/pagos/{pago_id}/subir-comprobante` - Subir archivo (líneas 287-293)

**Patrón actual:**
```python
# Desde base64
comprobante_bytes = base64.b64decode(request.comprobante_base64)
upload_result = cloudinary.uploader.upload(
    comprobante_bytes,
    folder=f"galloapp/pagos/comprobantes/user_{current_user_id}",
    public_id=f"comprobante_pago_{pago.id}_{timestamp}"
)

# Desde archivo
content = await comprobante.read()
upload_result = cloudinary.uploader.upload(content, ...)
```

---

### 7. 🛒 **MARKETPLACE** (`marketplace.py`)
**Prioridad:** 🟢 BAJA (Solo lectura)

**Uso actual:**
- Campo: `url_foto_cloudinary` (línea 97)
- Tipo: Solo lectura de URLs existentes
- No sube imágenes directamente

**Nota:** Este módulo solo lee las URLs de Cloudinary que fueron subidas por el módulo de Gallos.

---

### ✅ **SUSCRIPCIONES** (`suscripciones.py`)
**Estado:** ✅ NO REQUIERE MIGRACIÓN

**Verificación:**
- ❌ NO usa Cloudinary
- ❌ NO sube imágenes
- ✅ Solo maneja lógica de planes y límites
- ✅ Endpoints de validación y estadísticas

**Nota:** Este módulo NO necesita migración a ImageKit porque no maneja archivos.

---

## 📊 Resumen por Tipo de Archivo

### Videos (4 módulos)
1. ✅ Peleas de Evento (parcial - falta DELETE)
2. ❌ Peleas
3. ❌ Topes
4. ❌ (Transmisiones - si existe)

### Imágenes (3 módulos)
1. ❌ Gallos con Pedigrí (múltiples imágenes)
2. ❌ Profiles (avatar único)
3. ❌ Pagos (comprobantes)

---

## 🎯 Plan de Migración Priorizado

### FASE 1: Completar Peleas de Evento (1 día)
- [x] CREATE con ImageKit (ya hecho)
- [x] UPDATE con ImageKit (ya hecho)
- [ ] Migrar DELETE a ImageKit
- [ ] Agregar campo `file_id` a modelo `PeleaEvento`

### FASE 2: Migrar Videos (3-4 días)
**Orden sugerido:**
1. [ ] **Peleas** (más usado)
   - Crear `upload_video()` en endpoints
   - Migrar CREATE, UPDATE, DELETE
   - Probar con videos existentes

2. [ ] **Topes** (similar a Peleas)
   - Copiar patrón de Peleas
   - Ajustar carpetas y nombres

### FASE 3: Migrar Imágenes (4-5 días)
**Orden sugerido:**
1. [ ] **Profiles/Avatar** (más simple)
   - Un solo archivo por usuario
   - Implementar transformaciones en ImageKit
   - Probar crop y resize

2. [ ] **Gallos con Pedigrí** (más complejo)
   - Múltiples imágenes por gallo
   - Tabla `gallo_imagenes` con orden
   - Foto principal destacada
   - Migrar fotos existentes

3. [ ] **Pagos/Comprobantes** (menos crítico)
   - Similar a avatar pero sin transformaciones
   - Soporte para base64 y archivo

### FASE 4: Actualizar Referencias (1 día)
- [ ] Marketplace (actualizar queries)
- [ ] Cualquier otro módulo que lea URLs

---

## 🔧 Cambios Necesarios en imagekit_service.py

### Métodos a agregar:

```python
class ImageKitService:
    # ✅ YA EXISTE
    def upload_video(self, file_content: bytes, file_name: str, folder: str)
    def delete_video(self, file_id: str)
    
    # 🆕 A IMPLEMENTAR
    def upload_image(self, file_content: bytes, file_name: str, folder: str)
    def upload_image_with_transformations(
        self, 
        file_content: bytes, 
        file_name: str, 
        folder: str,
        width: int = None,
        height: int = None,
        crop: str = None
    )
    def delete_image(self, file_id: str)  # Alias de delete_video
    def get_optimized_url(self, url: str, width: int, height: int, quality: int)
```

---

## 📋 Checklist General por Módulo

Para cada módulo, seguir estos pasos:

### 1. Preparación
- [ ] Revisar endpoints actuales
- [ ] Identificar campos en BD
- [ ] Documentar patrón actual

### 2. Modelo de Datos
- [ ] Agregar campo `file_id` (para eliminar)
- [ ] Agregar campo `thumbnail_url` (si aplica)
- [ ] Crear migración Alembic

### 3. Servicio
- [ ] Importar `imagekit_service`
- [ ] Reemplazar `cloudinary.uploader.upload()`
- [ ] Reemplazar `cloudinary.uploader.destroy()`

### 4. Endpoints
- [ ] Actualizar CREATE
- [ ] Actualizar UPDATE
- [ ] Actualizar DELETE
- [ ] Probar con Postman/curl

### 5. Migración de Datos
- [ ] Script para migrar archivos existentes
- [ ] Actualizar URLs en BD
- [ ] Validar migración

### 6. Testing
- [ ] Test de upload
- [ ] Test de update
- [ ] Test de delete
- [ ] Test de URLs optimizadas

---

## 🚨 Consideraciones Importantes

### Cloudinary vs ImageKit

**Diferencias clave:**
1. **Upload:**
   - Cloudinary: `cloudinary.uploader.upload(file, folder=...)`
   - ImageKit: `imagekit.upload_file(file_base64, file_name, options)`

2. **Delete:**
   - Cloudinary: `cloudinary.uploader.destroy(public_id, resource_type)`
   - ImageKit: `imagekit.delete_file(file_id)`

3. **Transformaciones:**
   - Cloudinary: En upload con `transformation=[...]`
   - ImageKit: En URL con `tr:w-400,h-300,q-80`

### Campos necesarios en BD

**Para videos:**
```python
video_url = Column(String(500))
file_id = Column(String(255))  # Para eliminar
thumbnail_url = Column(String(500))  # Generado por ImageKit
```

**Para imágenes múltiples:**
```python
class GalloImagen(Base):
    id = Column(Integer, primary_key=True)
    gallo_id = Column(Integer, ForeignKey("gallos_simples.id"))
    url = Column(String(500))
    file_id = Column(String(255))
    orden = Column(Integer, default=0)
    es_principal = Column(Boolean, default=False)
```

### Migración de archivos existentes

**Opciones:**
1. **Migración completa:** Descargar de Cloudinary y subir a ImageKit
2. **Migración gradual:** Solo nuevos archivos en ImageKit, mantener URLs antiguas
3. **Dual:** Mantener ambos temporalmente con fallback

**Recomendación:** Opción 2 (gradual) para evitar downtime

---

## 📈 Estimación de Tiempo

| Fase | Módulos | Días |
|------|---------|------|
| Fase 1 | Completar Peleas Evento | 1 |
| Fase 2 | Peleas + Topes | 3-4 |
| Fase 3 | Profiles + Gallos + Pagos | 4-5 |
| Fase 4 | Referencias | 1 |
| **TOTAL** | **7 módulos** | **9-11 días** |

---

## ✅ Criterios de Éxito

- [ ] Todos los módulos usan ImageKit
- [ ] No hay referencias a Cloudinary en código
- [ ] Archivos existentes migrados o accesibles
- [ ] Tests pasando
- [ ] Documentación actualizada
- [ ] Costos reducidos vs Cloudinary

---

**Documento creado:** 2025-11-15
**Última actualización:** 2025-11-15
**Estado:** 📋 Análisis completo - Listo para migración
