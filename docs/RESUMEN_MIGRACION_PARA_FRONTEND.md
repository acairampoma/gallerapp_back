# 📱 RESUMEN DE MIGRACIÓN BACKEND - PARA FRONTEND

## 🎯 QUÉ CAMBIAMOS EN EL BACKEND

**Fecha:** 2025-11-15
**Cambio principal:** Migración completa a **Storage Manager** con patrón Adapter

---

## ⚠️ IMPORTANTE PARA EL FRONTEND

### ✅ **NO HAY CAMBIOS EN LAS APIs**

**Las URLs de los endpoints NO cambiaron.**
**Los requests y responses son IGUALES.**

Lo único que cambió fue **INTERNO del backend**:
- Antes: Usábamos ImageKit directamente
- Ahora: Usamos Storage Manager (puede ser ImageKit, Cloudinary o S3)

---

## 📋 ENDPOINTS POR MÓDULO

### 1. 🐓 **GALLOS CON PEDIGRÍ**

**Base URL:** `/api/v1/gallos-con-pedigri`

#### Endpoints principales:
```
GET    /gallos-con-pedigri                    # Listar gallos
GET    /gallos-con-pedigri/{gallo_id}         # Obtener gallo
POST   /gallos-con-pedigri/con-pedigri        # Crear gallo con pedigrí
PUT    /gallos-con-pedigri/{gallo_id}         # Actualizar gallo
DELETE /gallos-con-pedigri/{gallo_id}         # Eliminar gallo
GET    /gallos-con-pedigri/{gallo_id}/pdf     # Generar PDF pedigrí
```

#### Endpoints de imágenes:
```
POST   /gallos-con-pedigri/{gallo_id}/fotos              # Subir fotos adicionales
DELETE /gallos-con-pedigri/{gallo_id}/fotos/{public_id}  # Eliminar foto
PUT    /gallos-con-pedigri/{gallo_id}/foto-principal     # Actualizar foto principal
```

**Cambios internos:**
- ✅ Ahora usa `storage_manager` + `multi_image_service`
- ✅ Optimización automática de imágenes (800x800, WebP, 85% calidad)
- ✅ Upload paralelo de múltiples fotos (más rápido)
- ✅ Guarda `file_id` para poder eliminar después

**Response incluye:**
```json
{
  "foto_principal_url": "https://ik.imagekit.io/xxx/gallo.jpg",
  "fotos_adicionales": [
    {
      "url": "https://ik.imagekit.io/xxx/foto1.jpg",
      "file_id": "abc123",
      "thumbnail_url": "https://ik.imagekit.io/xxx/foto1_thumb.jpg"
    }
  ]
}
```

---

### 2. 🥊 **PELEAS**

**Base URL:** `/api/v1/peleas`

#### Endpoints:
```
GET    /peleas                    # Listar peleas
GET    /peleas/{pelea_id}         # Obtener pelea
POST   /peleas                    # Crear pelea (con video opcional)
PUT    /peleas/{pelea_id}         # Actualizar pelea (con video opcional)
DELETE /peleas/{pelea_id}         # Eliminar pelea
GET    /peleas/estadisticas       # Estadísticas de peleas
```

**Cambios internos:**
- ✅ Ahora usa `storage_manager`
- ✅ Guarda `file_id` del video
- ✅ Al actualizar, elimina video anterior automáticamente
- ✅ Al eliminar pelea, elimina video del storage

**Request (FormData):**
```
fecha_pelea: "2025-01-15"
lugar: "Coliseo"
mi_gallo_id: 123
oponente_gallo_nombre: "Gallo Rival"
resultado: "ganada"
video: File (opcional)
```

**Response incluye:**
```json
{
  "id": 1,
  "video_url": "https://ik.imagekit.io/xxx/pelea.mp4",
  "file_id": "xyz789",
  "resultado": "ganada"
}
```

---

### 3. 🏋️ **TOPES (Entrenamientos)**

**Base URL:** `/api/v1/topes`

#### Endpoints:
```
GET    /topes                    # Listar topes
GET    /topes/{tope_id}          # Obtener tope
POST   /topes                    # Crear tope (con video opcional)
PUT    /topes/{tope_id}          # Actualizar tope (con video opcional)
DELETE /topes/{tope_id}          # Eliminar tope
GET    /topes/estadisticas       # Estadísticas de topes
```

**Cambios internos:**
- ✅ Ahora usa `storage_manager`
- ✅ Guarda `file_id` del video
- ✅ Al actualizar, elimina video anterior automáticamente
- ✅ Al eliminar tope, elimina video del storage

**Request (FormData):**
```
fecha_tope: "2025-01-15"
gallo_id: 123
tipo_entrenamiento: "resistencia"
duracion_minutos: 30
video: File (opcional)
```

**Response incluye:**
```json
{
  "id": 1,
  "video_url": "https://ik.imagekit.io/xxx/tope.mp4",
  "file_id": "abc456",
  "tipo_entrenamiento": "resistencia"
}
```

---

### 4. 🎬 **PELEAS DE EVENTO (Transmisiones)**

**Base URL:** `/api/v1/transmisiones/eventos`

#### Endpoints:
```
GET    /transmisiones/eventos/{evento_id}/peleas              # Listar peleas de evento
GET    /transmisiones/eventos/peleas/{pelea_id}               # Obtener pelea
POST   /transmisiones/eventos/{evento_id}/peleas              # Crear pelea (ADMIN)
PUT    /transmisiones/eventos/peleas/{pelea_id}               # Actualizar pelea (ADMIN)
DELETE /transmisiones/eventos/peleas/{pelea_id}               # Eliminar pelea (ADMIN)
GET    /transmisiones/eventos/videoteca                       # Videoteca pública
```

**Cambios internos:**
- ✅ Ahora usa `storage_manager`
- ✅ Guarda `file_id` del video
- ✅ Al actualizar, elimina video anterior automáticamente
- ✅ Al eliminar pelea, elimina video del storage
- ✅ Genera thumbnail automáticamente

**Request (FormData - ADMIN):**
```
numero_pelea: 1
titulo_pelea: "Final del torneo"
galpon_izquierda: "Galpón A"
gallo_izquierda_nombre: "Campeón"
galpon_derecha: "Galpón B"
gallo_derecha_nombre: "Retador"
video: File (opcional)
```

**Response incluye:**
```json
{
  "id": 1,
  "video_url": "https://ik.imagekit.io/xxx/pelea_evento.mp4",
  "file_id": "def789",
  "thumbnail_pelea_url": "https://ik.imagekit.io/xxx/thumb.jpg",
  "estado_video": "disponible"
}
```

---

### 5. 💳 **PAGOS / SUSCRIPCIONES**

**Base URL:** `/api/v1/pagos`

#### Endpoints:
```
POST   /pagos/generar-qr                      # Generar QR de pago
POST   /pagos/confirmar-pago                  # Confirmar pago (con comprobante)
POST   /pagos/{pago_id}/subir-comprobante     # Subir comprobante
GET    /pagos/mis-pagos                       # Mis pagos
GET    /pagos/{pago_id}                       # Obtener pago
```

**Cambios internos:**
- ✅ Ahora usa `storage_manager`
- ✅ Guarda `comprobante_file_id`
- ✅ Soporta base64 y archivo directo

**Request (confirmar pago):**
```json
{
  "pago_id": 123,
  "comprobante_base64": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

**O con archivo:**
```
FormData:
- comprobante: File
```

**Response incluye:**
```json
{
  "id": 123,
  "comprobante_url": "https://ik.imagekit.io/xxx/comprobante.jpg",
  "comprobante_file_id": "ghi012",
  "estado": "verificando"
}
```

---

### 6. 👤 **PROFILES (Avatar)**

**Base URL:** `/api/v1/profiles`

#### Endpoints:
```
GET    /profiles/me              # Mi perfil
PUT    /profiles/me              # Actualizar perfil
POST   /profiles/avatar          # Subir avatar
DELETE /profiles/avatar          # Eliminar avatar
```

**Cambios internos:**
- ✅ Ahora usa `storage_manager`
- ✅ Optimización automática (200x200, WebP, 90% calidad)
- ✅ Sobrescribe avatar anterior automáticamente

**Request (subir avatar):**
```
FormData:
- file: File (imagen)
```

**Response incluye:**
```json
{
  "avatar_url": "https://ik.imagekit.io/xxx/avatar.webp",
  "nombre_completo": "Juan Pérez"
}
```

---

## 🔄 CAMBIOS EN LOS RESPONSES

### ✅ **Campos NUEVOS en responses:**

#### Gallos:
```json
{
  "fotos_adicionales": [
    {
      "url": "...",
      "file_id": "abc123",           // ✨ NUEVO
      "thumbnail_url": "...",         // ✨ NUEVO
      "width": 800,                   // ✨ NUEVO
      "height": 800,                  // ✨ NUEVO
      "size": 245678                  // ✨ NUEVO
    }
  ]
}
```

#### Peleas / Topes:
```json
{
  "video_url": "...",
  "file_id": "xyz789"                // ✨ NUEVO (antes no existía)
}
```

#### Peleas de Evento:
```json
{
  "video_url": "...",
  "file_id": "def456",               // ✨ NUEVO
  "thumbnail_pelea_url": "...",      // Ya existía
  "estado_video": "disponible"       // Ya existía
}
```

#### Pagos:
```json
{
  "comprobante_url": "...",
  "comprobante_file_id": "ghi789"    // ✨ NUEVO
}
```

---

## 📊 RESUMEN DE CAMBIOS POR TIPO DE ARCHIVO

### 🖼️ **IMÁGENES:**

**Módulos afectados:**
- Gallos (fotos de gallos)
- Profiles (avatar)
- Pagos (comprobantes)

**Optimizaciones automáticas:**
- Gallos: 800x800, WebP, 85% calidad
- Avatar: 200x200, WebP, 90% calidad
- Comprobantes: Sin optimización (original)

**Nuevos campos en response:**
- `file_id` - Para poder eliminar después
- `thumbnail_url` - URL del thumbnail
- `width`, `height`, `size` - Metadatos

---

### 🎥 **VIDEOS:**

**Módulos afectados:**
- Peleas
- Topes
- Peleas de Evento

**Nuevos campos en response:**
- `file_id` - Para poder eliminar después
- `thumbnail_url` - Thumbnail del video (solo peleas_evento)

---

## 🚨 BREAKING CHANGES

### ❌ **NO HAY BREAKING CHANGES**

**Todo es retrocompatible:**
- ✅ URLs iguales
- ✅ Request format igual
- ✅ Response format igual (solo campos NUEVOS agregados)
- ✅ Autenticación igual

**El frontend NO necesita cambios obligatorios.**

---

## ✨ MEJORAS QUE PUEDE APROVECHAR EL FRONTEND

### 1. **Thumbnails automáticos**
```dart
// Antes
Image.network(gallo.fotoPrincipalUrl)

// Ahora (con thumbnail)
Image.network(
  gallo.fotosAdicionales[0].thumbnailUrl ?? gallo.fotoPrincipalUrl
)
```

### 2. **Metadatos de imágenes**
```dart
// Mostrar tamaño de imagen
Text('${foto.width}x${foto.height} - ${foto.size} bytes')
```

### 3. **file_id para eliminar**
```dart
// Ahora puedes eliminar archivos específicos
await api.delete('/gallos/$galloId/fotos/${foto.fileId}')
```

---

## 🔧 CONFIGURACIÓN DEL BACKEND

### Proveedor activo:
```
STORAGE_PROVIDER=imagekit
```

**Proveedores disponibles:**
- `imagekit` (actual)
- `cloudinary` (fallback)
- `s3` (futuro)

**El frontend NO necesita saber cuál está activo.**
Las URLs siempre funcionan igual.

---

## 📝 CHECKLIST PARA EL FRONTEND

### Cambios OPCIONALES (recomendados):

- [ ] Usar `thumbnail_url` para previews (más rápido)
- [ ] Mostrar metadatos de imágenes (`width`, `height`, `size`)
- [ ] Guardar `file_id` si necesitas eliminar archivos después
- [ ] Actualizar modelos para incluir nuevos campos opcionales

### Cambios OBLIGATORIOS:

- [ ] **NINGUNO** - Todo es retrocompatible ✅

---

## 🧪 TESTING RECOMENDADO

### Probar estos flujos:

1. **Gallos:**
   - [ ] Crear gallo con foto principal
   - [ ] Subir fotos adicionales
   - [ ] Eliminar foto específica
   - [ ] Verificar que `file_id` viene en response

2. **Peleas:**
   - [ ] Crear pelea con video
   - [ ] Actualizar video (debe eliminar anterior)
   - [ ] Eliminar pelea (debe eliminar video)
   - [ ] Verificar que `file_id` viene en response

3. **Topes:**
   - [ ] Crear tope con video
   - [ ] Actualizar video
   - [ ] Eliminar tope
   - [ ] Verificar que `file_id` viene en response

4. **Pagos:**
   - [ ] Subir comprobante base64
   - [ ] Subir comprobante archivo
   - [ ] Verificar que `comprobante_file_id` viene en response

5. **Profiles:**
   - [ ] Subir avatar
   - [ ] Verificar optimización (debe ser WebP)
   - [ ] Eliminar avatar

---

## 📞 CONTACTO

Si encuentras algún problema o tienes dudas:

1. Revisar logs del backend
2. Verificar que el `file_id` viene en el response
3. Confirmar que las URLs de imágenes/videos funcionan
4. Reportar cualquier error 500

---

## 🎯 RESUMEN EJECUTIVO

### Lo que cambió:
- ✅ Backend ahora usa Storage Manager (patrón Adapter)
- ✅ Puede cambiar entre ImageKit, Cloudinary, S3 sin afectar frontend
- ✅ Optimización automática de imágenes
- ✅ Nuevos campos en responses (`file_id`, `thumbnail_url`, metadatos)

### Lo que NO cambió:
- ✅ URLs de endpoints
- ✅ Formato de requests
- ✅ Autenticación
- ✅ Lógica de negocio

### Acción requerida del frontend:
- ✅ **NINGUNA** (todo retrocompatible)
- ⚡ Opcionalmente: aprovechar nuevos campos para mejor UX

---

**Documento creado:** 2025-11-15
**Para:** Equipo Frontend
**De:** Equipo Backend
**Estado:** ✅ Migración completada y en producción
