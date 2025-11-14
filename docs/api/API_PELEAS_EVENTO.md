# 🥊 API PELEAS DE EVENTO - Documentación

## 📋 Resumen
Endpoints para gestionar peleas dentro de eventos de transmisión.

---

## 🔐 Autenticación
Todos los endpoints requieren token JWT en header:
```
Authorization: Bearer {token}
```

Los endpoints de creación, actualización y eliminación requieren **rol ADMIN**.

---

## 📡 ENDPOINTS

### 1. ➕ Crear Pelea de Evento
```http
POST /api/v1/transmisiones/eventos/{evento_id}/peleas
```

**Permisos:** Solo ADMIN

**Body:** `multipart/form-data`

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| numero_pelea | int | Sí | Número/orden de la pelea |
| titulo_pelea | string | Sí | Título de la pelea |
| galpon_izquierda | string | Sí | Galpón del gallo izquierdo |
| gallo_izquierda_nombre | string | Sí | Nombre gallo izquierdo |
| galpon_derecha | string | Sí | Galpón del gallo derecho |
| gallo_derecha_nombre | string | Sí | Nombre gallo derecho |
| descripcion_pelea | string | No | Descripción opcional |
| hora_inicio_estimada | string | No | Formato: HH:MM o HH:MM:SS |
| video | file | No | Archivo de video |

**Ejemplo cURL:**
```bash
curl -X POST "https://gallerappback-production.up.railway.app/api/v1/transmisiones/eventos/16/peleas" \
  -H "Authorization: Bearer {token}" \
  -F "numero_pelea=1" \
  -F "titulo_pelea=PELEA ESTELAR" \
  -F "galpon_izquierda=El Campeón" \
  -F "gallo_izquierda_nombre=Relámpago" \
  -F "galpon_derecha=Los Invencibles" \
  -F "gallo_derecha_nombre=Trueno" \
  -F "hora_inicio_estimada=15:00" \
  -F "video=@pelea1.mp4"
```

**Respuesta:** `201 Created`
```json
{
  "id": 1,
  "evento_id": 16,
  "numero_pelea": 1,
  "titulo_pelea": "PELEA ESTELAR",
  "descripcion_pelea": null,
  "galpon_izquierda": "El Campeón",
  "gallo_izquierda_nombre": "Relámpago",
  "galpon_derecha": "Los Invencibles",
  "gallo_derecha_nombre": "Trueno",
  "hora_inicio_estimada": "15:00:00",
  "hora_inicio_real": null,
  "hora_fin_real": null,
  "duracion_minutos": null,
  "resultado": null,
  "video_url": "https://res.cloudinary.com/.../pelea_1.mp4",
  "thumbnail_pelea_url": "https://res.cloudinary.com/.../pelea_1.jpg",
  "estado_video": "disponible",
  "admin_editor_id": 27,
  "created_at": "2025-10-01T10:00:00",
  "updated_at": "2025-10-01T10:00:00"
}
```

---

### 2. 📋 Listar Peleas de un Evento
```http
GET /api/v1/transmisiones/eventos/{evento_id}/peleas
```

**Permisos:** Usuario autenticado

**Ejemplo:**
```bash
curl "https://gallerappback-production.up.railway.app/api/v1/transmisiones/eventos/16/peleas" \
  -H "Authorization: Bearer {token}"
```

**Respuesta:** `200 OK`
```json
[
  {
    "id": 1,
    "numero_pelea": 1,
    "titulo_pelea": "PELEA ESTELAR",
    ...
  },
  {
    "id": 2,
    "numero_pelea": 2,
    "titulo_pelea": "SEMIFINAL A",
    ...
  }
]
```

---

### 3. 🔍 Obtener Pelea Específica
```http
GET /api/v1/transmisiones/eventos/peleas/{pelea_id}
```

**Permisos:** Usuario autenticado

**Ejemplo:**
```bash
curl "https://gallerappback-production.up.railway.app/api/v1/transmisiones/eventos/peleas/1" \
  -H "Authorization: Bearer {token}"
```

---

### 4. ✏️ Actualizar Pelea
```http
PUT /api/v1/transmisiones/eventos/peleas/{pelea_id}
```

**Permisos:** Solo ADMIN

**Body:** `multipart/form-data` (todos los campos son opcionales)

**Ejemplo:**
```bash
curl -X PUT "https://gallerappback-production.up.railway.app/api/v1/transmisiones/eventos/peleas/1" \
  -H "Authorization: Bearer {token}" \
  -F "titulo_pelea=PELEA MODIFICADA" \
  -F "resultado=izquierda" \
  -F "video=@nuevo_video.mp4"
```

---

### 5. 🔄 Cambiar Orden de Pelea
```http
PUT /api/v1/transmisiones/eventos/peleas/{pelea_id}/orden
```

**Permisos:** Solo ADMIN

**Body:** `multipart/form-data`

| Campo | Tipo | Requerido |
|-------|------|-----------|
| nuevo_numero | int | Sí |

**Ejemplo:**
```bash
curl -X PUT "https://gallerappback-production.up.railway.app/api/v1/transmisiones/eventos/peleas/1/orden" \
  -H "Authorization: Bearer {token}" \
  -F "nuevo_numero=3"
```

---

### 6. 🗑️ Eliminar Pelea
```http
DELETE /api/v1/transmisiones/eventos/peleas/{pelea_id}
```

**Permisos:** Solo ADMIN

**Ejemplo:**
```bash
curl -X DELETE "https://gallerappback-production.up.railway.app/api/v1/transmisiones/eventos/peleas/1" \
  -H "Authorization: Bearer {token}"
```

**Respuesta:** `204 No Content`

---

## 📊 Códigos de Estado

| Código | Descripción |
|--------|-------------|
| 200 | OK - Operación exitosa |
| 201 | Created - Pelea creada |
| 204 | No Content - Pelea eliminada |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Sin autenticación |
| 403 | Forbidden - Sin permisos de admin |
| 404 | Not Found - Pelea o evento no encontrado |
| 500 | Internal Server Error - Error del servidor |

---

## 🎥 Upload de Videos

Los videos se suben a **Cloudinary** con las siguientes configuraciones:

- **Folder:** `peleas_evento/{evento_id}/`
- **Formatos generados:**
  - HD: 1280x720
  - SD: 640x360
- **Thumbnail:** Generado automáticamente
- **Estados del video:**
  - `sin_video`: No tiene video
  - `procesando`: Subiendo a Cloudinary
  - `disponible`: Video listo

---

## 📝 Valores Permitidos

### `resultado`
- `izquierda` - Ganó el gallo de la izquierda
- `derecha` - Ganó el gallo de la derecha
- `empate` - Empate
- `null` - Sin resultado aún

### `estado_video`
- `sin_video` - No tiene video
- `procesando` - Subiendo
- `disponible` - Listo para reproducir

---

## 🔧 Testing

Para probar los endpoints localmente:

```bash
# 1. Crear pelea
curl -X POST "http://localhost:8000/api/v1/transmisiones/eventos/16/peleas" \
  -H "Authorization: Bearer eyJ..." \
  -F "numero_pelea=1" \
  -F "titulo_pelea=TEST" \
  -F "galpon_izquierda=Galpon A" \
  -F "gallo_izquierda_nombre=Gallo 1" \
  -F "galpon_derecha=Galpon B" \
  -F "gallo_derecha_nombre=Gallo 2"

# 2. Listar peleas
curl "http://localhost:8000/api/v1/transmisiones/eventos/16/peleas" \
  -H "Authorization: Bearer eyJ..."
```

---

## 📚 Archivos Creados

1. **Modelo:** `app/models/pelea_evento.py`
2. **Schemas:** `app/schemas/pelea_evento.py`
3. **Endpoints:** `app/api/v1/peleas_evento.py`
4. **Script SQL:** `scripts/002_mejora_peleas_evento.sql`

---

**Versión:** 1.0.0
**Fecha:** 2025-10-01
**Autor:** Sistema Casto de Gallos
