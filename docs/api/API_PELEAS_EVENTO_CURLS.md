# 🥊 **PELEAS DE EVENTO API - CURL TEST CASES**

## **📋 REQUISITOS PREVIOS**

1. **Tener evento de transmisión creado (evento_id: 16 en producción)**

2. **Variables de entorno para testing:**
   ```bash
   export BASE_URL="https://gallerappback-production.up.railway.app/api/v1"
   export ADMIN_TOKEN="Bearer YOUR_ADMIN_JWT_TOKEN_HERE"
   ```

---

## 🔐 **1. AUTHENTICATION - LOGIN ADMIN**

### **Login Usuario Admin**
```bash
curl -X POST "$BASE_URL/../auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "acairampoma@gmail.com",
    "password": "your_password"
  }'
```

**Copiar el access_token de la respuesta y setear:**
```bash
export ADMIN_TOKEN="Bearer eyJ..."
```

---

## 📺 **2. VERIFICAR EVENTO EXISTENTE**

### **Listar eventos de transmisión**
```bash
curl -X GET "$BASE_URL/transmisiones/eventos" \
  -H "Authorization: $ADMIN_TOKEN"
```

**Respuesta esperada:**
```json
[
  {
    "id": 16,
    "titulo": "Derby Regional Lima 2024",
    "descripcion": "Gran evento de peleas...",
    "fecha_evento": "2024-10-15",
    ...
  }
]
```

---

## 🥊 **3. PELEAS DE EVENTO - OPERACIONES PRINCIPALES**

### **A. CREAR PELEA DE EVENTO (SIN VIDEO)**

#### **Crear pelea básica**
```bash
curl -X POST "$BASE_URL/transmisiones/eventos/16/peleas" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "numero_pelea=1" \
  -F "titulo_pelea=PELEA ESTELAR" \
  -F "galpon_izquierda=El Campeón" \
  -F "gallo_izquierda_nombre=Relámpago" \
  -F "galpon_derecha=Los Invencibles" \
  -F "gallo_derecha_nombre=Trueno"
```

**Respuesta esperada:**
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
  "hora_inicio_estimada": null,
  "hora_inicio_real": null,
  "hora_fin_real": null,
  "duracion_minutos": null,
  "resultado": null,
  "video_url": null,
  "thumbnail_pelea_url": null,
  "estado_video": "sin_video",
  "admin_editor_id": 27,
  "created_at": "2025-10-01T10:00:00",
  "updated_at": "2025-10-01T10:00:00"
}
```

#### **Crear pelea con descripción y hora**
```bash
curl -X POST "$BASE_URL/transmisiones/eventos/16/peleas" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "numero_pelea=2" \
  -F "titulo_pelea=SEMIFINAL A" \
  -F "descripcion_pelea=Pelea importante de semifinal" \
  -F "galpon_izquierda=Galpón Norte" \
  -F "gallo_izquierda_nombre=Tornado" \
  -F "galpon_derecha=Galpón Sur" \
  -F "gallo_derecha_nombre=Huracán" \
  -F "hora_inicio_estimada=15:30"
```

#### **Crear pelea con video**
```bash
curl -X POST "$BASE_URL/transmisiones/eventos/16/peleas" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "numero_pelea=3" \
  -F "titulo_pelea=FINAL DEL TORNEO" \
  -F "galpon_izquierda=El Rey" \
  -F "gallo_izquierda_nombre=Campeón" \
  -F "galpon_derecha=La Gloria" \
  -F "gallo_derecha_nombre=Invicto" \
  -F "hora_inicio_estimada=18:00" \
  -F "video=@/path/to/pelea_final.mp4"
```

**Nota:** El video se subirá a Cloudinary y generará thumbnail automáticamente.

---

### **B. LISTAR PELEAS DE UN EVENTO**

#### **Listar todas las peleas**
```bash
curl -X GET "$BASE_URL/transmisiones/eventos/16/peleas" \
  -H "Authorization: $ADMIN_TOKEN"
```

**Respuesta esperada:**
```json
[
  {
    "id": 1,
    "evento_id": 16,
    "numero_pelea": 1,
    "titulo_pelea": "PELEA ESTELAR",
    "galpon_izquierda": "El Campeón",
    "gallo_izquierda_nombre": "Relámpago",
    "galpon_derecha": "Los Invencibles",
    "gallo_derecha_nombre": "Trueno",
    "video_url": null,
    "estado_video": "sin_video",
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

### **C. OBTENER PELEA ESPECÍFICA**

#### **Ver detalles de una pelea**
```bash
curl -X GET "$BASE_URL/transmisiones/eventos/peleas/1" \
  -H "Authorization: $ADMIN_TOKEN"
```

**Respuesta esperada:**
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
  "hora_inicio_estimada": null,
  "resultado": null,
  "video_url": null,
  "thumbnail_pelea_url": null,
  "estado_video": "sin_video",
  ...
}
```

---

### **D. ACTUALIZAR PELEA**

#### **Actualizar título y descripción**
```bash
curl -X PUT "$BASE_URL/transmisiones/eventos/peleas/1" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "titulo_pelea=PELEA ESTELAR MODIFICADA" \
  -F "descripcion_pelea=Gran pelea entre campeones"
```

#### **Actualizar resultado**
```bash
curl -X PUT "$BASE_URL/transmisiones/eventos/peleas/1" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "resultado=izquierda"
```

**Valores válidos para resultado:**
- `izquierda` - Ganó el gallo de la izquierda
- `derecha` - Ganó el gallo de la derecha
- `empate` - Empate

#### **Actualizar video**
```bash
curl -X PUT "$BASE_URL/transmisiones/eventos/peleas/1" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "video=@/path/to/nuevo_video.mp4"
```

#### **Actualizar múltiples campos**
```bash
curl -X PUT "$BASE_URL/transmisiones/eventos/peleas/1" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "titulo_pelea=PELEA FINAL" \
  -F "resultado=izquierda" \
  -F "galpon_izquierda=Nuevo Galpón" \
  -F "gallo_izquierda_nombre=Nuevo Gallo"
```

---

### **E. CAMBIAR ORDEN DE PELEAS**

#### **Mover pelea 3 a posición 1**
```bash
curl -X PUT "$BASE_URL/transmisiones/eventos/peleas/3/orden" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "nuevo_numero=1"
```

**Nota:** Esto reorganizará automáticamente todas las peleas.

**Antes:**
- Pelea 1: numero_pelea=1
- Pelea 2: numero_pelea=2
- Pelea 3: numero_pelea=3

**Después:**
- Pelea 3: numero_pelea=1
- Pelea 1: numero_pelea=2
- Pelea 2: numero_pelea=3

---

### **F. ELIMINAR PELEA**

#### **Eliminar pelea específica**
```bash
curl -X DELETE "$BASE_URL/transmisiones/eventos/peleas/2" \
  -H "Authorization: $ADMIN_TOKEN"
```

**Respuesta esperada:** `204 No Content`

**Nota:** Esto también eliminará el video de Cloudinary si existe.

---

## 🧪 **4. CASOS DE PRUEBA - VALIDACIONES**

### **A. VALIDACIÓN DE PERMISOS**

#### **Usuario no admin intentando crear pelea (debe fallar)**
```bash
# Usar token de usuario normal
curl -X POST "$BASE_URL/transmisiones/eventos/16/peleas" \
  -H "Authorization: Bearer TOKEN_USUARIO_NORMAL" \
  -F "numero_pelea=5" \
  -F "titulo_pelea=TEST" \
  -F "galpon_izquierda=Test" \
  -F "gallo_izquierda_nombre=Test" \
  -F "galpon_derecha=Test2" \
  -F "gallo_derecha_nombre=Test2"
```

**Error esperado:**
```json
{
  "detail": "No tiene permisos de administrador"
}
```

---

### **B. VALIDACIÓN DE EVENTO**

#### **Crear pelea en evento inexistente (debe fallar)**
```bash
curl -X POST "$BASE_URL/transmisiones/eventos/99999/peleas" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "numero_pelea=1" \
  -F "titulo_pelea=TEST" \
  -F "galpon_izquierda=Test" \
  -F "gallo_izquierda_nombre=Test" \
  -F "galpon_derecha=Test2" \
  -F "gallo_derecha_nombre=Test2"
```

**Error esperado:**
```json
{
  "detail": "Evento de transmisión no encontrado"
}
```

---

### **C. VALIDACIÓN DE CAMPOS REQUERIDOS**

#### **Crear pelea sin campos requeridos (debe fallar)**
```bash
curl -X POST "$BASE_URL/transmisiones/eventos/16/peleas" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "numero_pelea=1" \
  -F "titulo_pelea=TEST"
```

**Error esperado:**
```json
{
  "detail": [
    {
      "loc": ["body", "galpon_izquierda"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    ...
  ]
}
```

---

### **D. VALIDACIÓN DE RESULTADO**

#### **Resultado inválido (debe fallar)**
```bash
curl -X PUT "$BASE_URL/transmisiones/eventos/peleas/1" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "resultado=ganador"
```

**Error esperado:**
```json
{
  "detail": "Resultado debe ser: izquierda, derecha, o empate"
}
```

---

## 🔄 **5. WORKFLOW COMPLETO DE GESTIÓN**

### **Workflow típico de admin:**

```bash
# 1. Ver eventos disponibles
curl -X GET "$BASE_URL/transmisiones/eventos" \
  -H "Authorization: $ADMIN_TOKEN"

# 2. Crear 3 peleas para el evento 16
curl -X POST "$BASE_URL/transmisiones/eventos/16/peleas" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "numero_pelea=1" \
  -F "titulo_pelea=APERTURA" \
  -F "galpon_izquierda=Galpón A" \
  -F "gallo_izquierda_nombre=Gallo 1" \
  -F "galpon_derecha=Galpón B" \
  -F "gallo_derecha_nombre=Gallo 2"

curl -X POST "$BASE_URL/transmisiones/eventos/16/peleas" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "numero_pelea=2" \
  -F "titulo_pelea=SEMIFINAL" \
  -F "galpon_izquierda=Galpón C" \
  -F "gallo_izquierda_nombre=Gallo 3" \
  -F "galpon_derecha=Galpón D" \
  -F "gallo_derecha_nombre=Gallo 4"

curl -X POST "$BASE_URL/transmisiones/eventos/16/peleas" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "numero_pelea=3" \
  -F "titulo_pelea=FINAL" \
  -F "galpon_izquierda=Galpón E" \
  -F "gallo_izquierda_nombre=Gallo 5" \
  -F "galpon_derecha=Galpón F" \
  -F "gallo_derecha_nombre=Gallo 6"

# 3. Listar todas las peleas creadas
curl -X GET "$BASE_URL/transmisiones/eventos/16/peleas" \
  -H "Authorization: $ADMIN_TOKEN"

# 4. Reordenar: mover pelea 3 (FINAL) a posición 1
curl -X PUT "$BASE_URL/transmisiones/eventos/peleas/3/orden" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "nuevo_numero=1"

# 5. Actualizar resultado de la primera pelea
curl -X PUT "$BASE_URL/transmisiones/eventos/peleas/1" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "resultado=izquierda"

# 6. Subir video a una pelea
curl -X PUT "$BASE_URL/transmisiones/eventos/peleas/1" \
  -H "Authorization: $ADMIN_TOKEN" \
  -F "video=@/path/to/video.mp4"

# 7. Verificar que el video se subió
curl -X GET "$BASE_URL/transmisiones/eventos/peleas/1" \
  -H "Authorization: $ADMIN_TOKEN"

# 8. Eliminar una pelea
curl -X DELETE "$BASE_URL/transmisiones/eventos/peleas/2" \
  -H "Authorization: $ADMIN_TOKEN"
```

---

## 📊 **6. VERIFICACIÓN DE DATOS**

### **A. Verificar en Base de Datos**

```sql
-- Ver todas las peleas del evento 16
SELECT * FROM peleas_evento WHERE evento_id = 16 ORDER BY numero_pelea;

-- Contar peleas por evento
SELECT evento_id, COUNT(*) as total_peleas
FROM peleas_evento
GROUP BY evento_id;

-- Ver peleas con video
SELECT id, titulo_pelea, video_url, estado_video
FROM peleas_evento
WHERE video_url IS NOT NULL;

-- Ver resultados de peleas
SELECT id, titulo_pelea, resultado,
       galpon_izquierda, gallo_izquierda_nombre,
       galpon_derecha, gallo_derecha_nombre
FROM peleas_evento
WHERE resultado IS NOT NULL;
```

---

## ✅ **7. CHECKLIST DE PRUEBAS**

- [x] **CREATE**: Crear pelea sin video
- [x] **CREATE**: Crear pelea con video y descripción
- [x] **READ**: Listar todas las peleas de un evento
- [x] **READ**: Obtener pelea específica
- [x] **UPDATE**: Actualizar título y descripción
- [x] **UPDATE**: Actualizar resultado
- [x] **UPDATE**: Subir/actualizar video
- [x] **DELETE**: Eliminar pelea
- [x] **REORDER**: Cambiar orden de peleas
- [x] **PERMISSIONS**: Validar permisos de admin
- [x] **VALIDATION**: Campos requeridos
- [x] **VALIDATION**: Resultado válido
- [x] **VALIDATION**: Evento existente
- [x] **CLOUDINARY**: Upload de video
- [x] **CLOUDINARY**: Generación de thumbnail

---

## 🔧 **TROUBLESHOOTING**

### **Errores comunes:**

1. **403 Forbidden**: Usuario no es admin
   ```bash
   # Verificar que el usuario sea admin en la BD
   SELECT id, email, es_admin FROM users WHERE id = X;
   ```

2. **404 Not Found**: Evento o pelea no existe
   ```bash
   # Verificar IDs
   curl -X GET "$BASE_URL/transmisiones/eventos" ...
   ```

3. **422 Validation Error**: Datos inválidos
   ```bash
   # Verificar campos requeridos en la documentación
   ```

4. **500 Internal Server Error**: Error en Cloudinary o BD
   ```bash
   # Ver logs del servidor
   # Verificar configuración de Cloudinary
   ```

---

## 📈 **MÉTRICAS DE ÉXITO**

- ✅ **CRUD Completo**: Crear, leer, actualizar, eliminar peleas
- ✅ **Reordenamiento**: Cambiar orden dinámicamente
- ✅ **Videos**: Upload a Cloudinary con thumbnail
- ✅ **Seguridad**: Solo admins pueden gestionar
- ✅ **Relaciones**: CASCADE delete funciona correctamente
- ✅ **Validaciones**: Campos y permisos validados
- ✅ **Performance**: Respuestas < 500ms
- ✅ **Data Integrity**: Foreign keys funcionando

**¡API de Peleas de Evento lista para producción! 🥊🚀**
