# 🐛 DIAGNÓSTICO: Problema con Fotos en Formulario de Pedigrí

## 📅 Fecha: 2025-11-16

---

## 🎯 PROBLEMA REPORTADO POR EL USUARIO

### Escenario actual:

1. **Frontend tiene formulario con:**
   - 1 casilla para foto principal
   - 3 casillas para fotos adicionales

2. **Problema al editar gallo existente:**
   - ✅ Foto principal de Cloudinary se recupera y muestra en el cuadro
   - ❌ Al presionar "editar", la foto principal NO se sube (pero dice que sí)
   - ❌ Si subo foto nueva en casilla de foto adicional, actualiza la foto principal (NO RESPETA la casilla adicional 1)
   - ❌ Si subo foto en casilla 2 o 3, sale ERROR

---

## 🔍 ANÁLISIS DE LA BASE DE DATOS

### Gallos con URLs de Cloudinary (Legacy):

```sql
SELECT id, nombre, foto_principal_url, fotos_adicionales
FROM gallos
WHERE foto_principal_url LIKE '%cloudinary%'
LIMIT 5;
```

**Resultado:**
- 10+ gallos tienen URLs de Cloudinary en `foto_principal_url`
- Algunos tienen `fotos_adicionales` con estructura JSON antigua
- Estos gallos fueron creados ANTES de la migración a ImageKit

**Ejemplo de gallo #276:**
```json
{
  "id": 276,
  "nombre": "el obediente",
  "foto_principal_url": "https://res.cloudinary.com/dz4czc3en/...",
  "fotos_adicionales": "[{
    \"url\": \"https://res.cloudinary.com/...\",
    \"orden\": 1,
    \"es_principal\": true,
    \"cloudinary_public_id\": \"galloapp/user_107/...\"
  }]"
}
```

---

## 🔧 ANÁLISIS DEL CÓDIGO BACKEND

### 1. **Endpoint PUT (Actualizar Gallo)** - Línea 1050-1181

**Problema identificado:**
```python
# Línea 1110-1146
if foto_principal:
    # Solo actualiza si SE SUBE una nueva foto
    upload_result = await multi_image_service.upload_single_image(...)
    
    if upload_result:
        foto_url = upload_result['url']
        # Actualiza foto_principal_url
else:
    # Si NO se sube foto, mantiene la anterior
    foto_url = gallo_actual.foto_principal_url  # ← CLOUDINARY URL
```

**✅ ESTE ENDPOINT ESTÁ BIEN** - Solo actualiza si hay archivo nuevo.

---

### 2. **Endpoint POST /fotos-multiples** - Línea 1193-1349

**Problema identificado:**

```python
# Línea 1294-1331
if gallo_result.foto_principal_url:
    # YA TIENE FOTO PRINCIPAL - Solo actualizar fotos_adicionales
    update_fotos = text("""
        UPDATE gallos
        SET fotos_adicionales = :fotos_json,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :id AND user_id = :user_id
    """)
    # ❌ NO actualiza foto_principal_url
    
else:
    # NO TIENE FOTO PRINCIPAL - Usar la primera como principal
    update_fotos = text("""
        UPDATE gallos
        SET fotos_adicionales = :fotos_json,
            foto_principal_url = :foto_principal,
            url_foto_cloudinary = :foto_optimizada,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :id AND user_id = :user_id
    """)
```

**🚨 PROBLEMA ENCONTRADO:**

El endpoint `/fotos-multiples` tiene lógica que:
- Si el gallo YA tiene `foto_principal_url` (Cloudinary), **NO la actualiza**
- Solo actualiza `fotos_adicionales`
- Esto causa que la primera foto subida NO se convierta en principal

**Pero hay otro problema:**

```python
# Línea 1258-1268
foto_obj = {
    "url": upload_result['url'],
    "url_optimized": upload_result['url'],
    "orden": i + 1,
    "es_principal": i == 0,  # ← Primera foto SIEMPRE es principal
    ...
}
```

**🚨 PROBLEMA 2:**
- La primera foto SIEMPRE se marca como `es_principal: true`
- Pero si el gallo ya tiene foto principal, NO se actualiza en la BD
- Esto causa inconsistencia entre el JSON y la foto_principal_url

---

## 🎯 ESCENARIO DEL PROBLEMA

### Caso 1: Gallo con foto de Cloudinary (Legacy)

**Estado inicial:**
```json
{
  "foto_principal_url": "https://cloudinary.com/foto_vieja.jpg",
  "fotos_adicionales": null
}
```

**Usuario sube 3 fotos en el formulario:**
- Casilla 1 (adicional): foto1.jpg
- Casilla 2 (adicional): foto2.jpg
- Casilla 3 (adicional): foto3.jpg

**Lo que pasa en el backend:**
```python
# Se suben las 3 fotos
fotos_json = [
  {"url": "imagekit.com/foto1.jpg", "orden": 1, "es_principal": true},  # ← Marcada como principal
  {"url": "imagekit.com/foto2.jpg", "orden": 2, "es_principal": false},
  {"url": "imagekit.com/foto3.jpg", "orden": 3, "es_principal": false}
]

# Pero como YA tiene foto_principal_url, solo actualiza fotos_adicionales
UPDATE gallos SET fotos_adicionales = '[...]'
# NO actualiza foto_principal_url

# Resultado:
{
  "foto_principal_url": "https://cloudinary.com/foto_vieja.jpg",  # ← Sigue siendo Cloudinary
  "fotos_adicionales": "[{es_principal: true, url: imagekit...}, ...]"  # ← Inconsistente
}
```

**🚨 PROBLEMA:**
- La foto principal sigue siendo de Cloudinary
- Pero en `fotos_adicionales` hay una foto marcada como `es_principal: true`
- El frontend se confunde y muestra la foto incorrecta

---

### Caso 2: Usuario sube foto en casilla 2 o 3

**Lo que pasa:**
```python
# Usuario sube solo en casilla 2
fotos = [None, foto_2, None, None]

# Backend procesa:
for i, foto in enumerate(fotos):
    if foto:
        foto_obj = {
            "orden": i + 1,  # orden = 2
            "es_principal": i == 0  # es_principal = False (porque i=1, no 0)
        }
```

**🚨 PROBLEMA:**
- Si solo se sube foto en casilla 2 o 3, NINGUNA se marca como principal
- Pero el código en línea 1294 verifica si `gallo_result.foto_principal_url` existe
- Si existe (Cloudinary), NO actualiza
- Si NO existe, usa `fotos_json[0]` como principal, pero puede estar vacío

**Resultado: ERROR o comportamiento inconsistente**

---

## 🔧 SOLUCIÓN PROPUESTA

### Opción 1: Limpiar data de Cloudinary (Recomendado)

**Script SQL para migrar URLs:**

```sql
-- 1. Identificar gallos con Cloudinary
SELECT id, nombre, foto_principal_url, fotos_adicionales
FROM gallos
WHERE foto_principal_url LIKE '%cloudinary%'
   OR url_foto_cloudinary LIKE '%cloudinary%'
   OR fotos_adicionales::text LIKE '%cloudinary%';

-- 2. Opción A: Limpiar fotos de Cloudinary (forzar re-upload)
UPDATE gallos
SET foto_principal_url = NULL,
    url_foto_cloudinary = NULL,
    fotos_adicionales = NULL
WHERE foto_principal_url LIKE '%cloudinary%'
   OR url_foto_cloudinary LIKE '%cloudinary%';

-- 3. Opción B: Mantener URLs pero marcar para migración
ALTER TABLE gallos ADD COLUMN IF NOT EXISTS necesita_migracion_foto BOOLEAN DEFAULT FALSE;

UPDATE gallos
SET necesita_migracion_foto = TRUE
WHERE foto_principal_url LIKE '%cloudinary%'
   OR url_foto_cloudinary LIKE '%cloudinary%';
```

---

### Opción 2: Mejorar lógica del endpoint /fotos-multiples

**Cambio en línea 1294-1331:**

```python
# ANTES (línea 1294)
if gallo_result.foto_principal_url:
    # YA TIENE FOTO PRINCIPAL - Solo actualizar fotos_adicionales
    update_fotos = text("""
        UPDATE gallos
        SET fotos_adicionales = :fotos_json,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :id AND user_id = :user_id
    """)

# DESPUÉS (MEJORADO)
# Verificar si la foto principal es de Cloudinary (legacy)
es_cloudinary = 'cloudinary' in (gallo_result.foto_principal_url or '')

if gallo_result.foto_principal_url and not es_cloudinary:
    # TIENE FOTO PRINCIPAL DE IMAGEKIT - Preservarla
    update_fotos = text("""
        UPDATE gallos
        SET fotos_adicionales = :fotos_json,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :id AND user_id = :user_id
    """)
    print(f"✅ Foto principal de ImageKit preservada")
    
else:
    # NO TIENE FOTO O ES DE CLOUDINARY - Actualizar con nueva
    update_fotos = text("""
        UPDATE gallos
        SET fotos_adicionales = :fotos_json,
            foto_principal_url = :foto_principal,
            url_foto_cloudinary = :foto_optimizada,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :id AND user_id = :user_id
    """)
    print(f"✅ Foto principal actualizada (era Cloudinary o no existía)")
```

---

### Opción 3: Agregar parámetro para forzar actualización

**Cambio en endpoint:**

```python
@router.post("/{gallo_id}/fotos-multiples", response_model=dict)
async def actualizar_fotos_multiples_gallo(
    gallo_id: int,
    foto_1: Optional[UploadFile] = File(None),
    foto_2: Optional[UploadFile] = File(None),
    foto_3: Optional[UploadFile] = File(None),
    foto_4: Optional[UploadFile] = File(None),
    actualizar_principal: bool = Form(False),  # ← NUEVO PARÁMETRO
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # ...
    
    # Lógica mejorada
    debe_actualizar_principal = (
        not gallo_result.foto_principal_url or  # No tiene foto
        'cloudinary' in gallo_result.foto_principal_url or  # Es Cloudinary
        actualizar_principal  # Usuario fuerza actualización
    )
    
    if debe_actualizar_principal and foto_principal_url:
        # Actualizar foto principal
        update_fotos = text("""
            UPDATE gallos
            SET fotos_adicionales = :fotos_json,
                foto_principal_url = :foto_principal,
                url_foto_cloudinary = :foto_optimizada,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :id AND user_id = :user_id
        """)
    else:
        # Solo actualizar fotos adicionales
        update_fotos = text("""
            UPDATE gallos
            SET fotos_adicionales = :fotos_json,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :id AND user_id = :user_id
        """)
```

---

## 🎯 RECOMENDACIÓN FINAL

### **SOLUCIÓN COMBINADA (Mejor enfoque):**

1. **Limpiar data de Cloudinary en BD** (Opción 1)
   - Ejecutar UPDATE para poner NULL en fotos de Cloudinary
   - Esto fuerza a los usuarios a re-subir fotos con ImageKit

2. **Mejorar lógica del endpoint** (Opción 2)
   - Detectar si foto_principal_url es de Cloudinary
   - Si es Cloudinary, permitir actualización
   - Si es ImageKit, preservar

3. **Agregar flag en frontend** (Opción 3)
   - Permitir al usuario decidir si quiere actualizar la foto principal
   - Checkbox: "Actualizar foto principal" en el formulario

---

## 📋 SCRIPT DE MIGRACIÓN

### Paso 1: Backup de datos

```sql
-- Crear tabla de respaldo
CREATE TABLE gallos_backup_cloudinary AS
SELECT id, nombre, foto_principal_url, url_foto_cloudinary, fotos_adicionales
FROM gallos
WHERE foto_principal_url LIKE '%cloudinary%'
   OR url_foto_cloudinary LIKE '%cloudinary%'
   OR fotos_adicionales::text LIKE '%cloudinary%';

-- Verificar backup
SELECT COUNT(*) FROM gallos_backup_cloudinary;
```

### Paso 2: Limpiar URLs de Cloudinary

```sql
-- Opción A: Limpiar completamente (forzar re-upload)
UPDATE gallos
SET foto_principal_url = NULL,
    url_foto_cloudinary = NULL,
    fotos_adicionales = NULL
WHERE foto_principal_url LIKE '%cloudinary%'
   OR url_foto_cloudinary LIKE '%cloudinary%'
   OR fotos_adicionales::text LIKE '%cloudinary%';

-- Verificar cambios
SELECT id, nombre, foto_principal_url, fotos_adicionales
FROM gallos
WHERE id IN (SELECT id FROM gallos_backup_cloudinary);
```

### Paso 3: Notificar a usuarios

```sql
-- Crear notificación para usuarios afectados
INSERT INTO notificaciones (user_id, mensaje, tipo, created_at)
SELECT DISTINCT user_id,
       'Tus fotos de gallos fueron migradas. Por favor, vuelve a subir las fotos de tus gallos.',
       'info',
       NOW()
FROM gallos
WHERE id IN (SELECT id FROM gallos_backup_cloudinary);
```

---

## 🧪 TESTING

### Test 1: Gallo sin foto

```bash
# Subir 3 fotos
curl -X POST "http://localhost:8000/api/v1/gallos-con-pedigri/123/fotos-multiples" \
  -H "Authorization: Bearer $TOKEN" \
  -F "foto_1=@foto1.jpg" \
  -F "foto_2=@foto2.jpg" \
  -F "foto_3=@foto3.jpg"

# Verificar que foto_1 se convierte en principal
```

### Test 2: Gallo con foto de Cloudinary

```bash
# 1. Verificar estado actual
curl -X GET "http://localhost:8000/api/v1/gallos-con-pedigri/276" \
  -H "Authorization: Bearer $TOKEN"

# 2. Subir nueva foto
curl -X POST "http://localhost:8000/api/v1/gallos-con-pedigri/276/fotos-multiples" \
  -H "Authorization: Bearer $TOKEN" \
  -F "foto_1=@nueva_foto.jpg"

# 3. Verificar que se actualizó a ImageKit
curl -X GET "http://localhost:8000/api/v1/gallos-con-pedigri/276" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.foto_principal_url'
```

### Test 3: Subir solo en casilla 2

```bash
# Subir solo foto_2
curl -X POST "http://localhost:8000/api/v1/gallos-con-pedigri/123/fotos-multiples" \
  -H "Authorization: Bearer $TOKEN" \
  -F "foto_2=@foto2.jpg"

# Verificar que NO da error
```

---

## 📊 RESUMEN EJECUTIVO

### Problema raíz:
1. Gallos antiguos tienen URLs de Cloudinary
2. Endpoint `/fotos-multiples` NO actualiza foto_principal_url si ya existe
3. Esto causa inconsistencia entre foto_principal_url y fotos_adicionales

### Solución:
1. **Limpiar data de Cloudinary** → Forzar re-upload con ImageKit
2. **Mejorar lógica del endpoint** → Detectar Cloudinary y permitir actualización
3. **Agregar parámetro opcional** → Permitir forzar actualización

### Impacto:
- ✅ Usuarios con fotos de Cloudinary tendrán que re-subirlas
- ✅ Nuevas fotos se subirán correctamente con ImageKit
- ✅ Consistencia entre foto_principal_url y fotos_adicionales

---

**¿Quieres que ejecute la limpieza de Cloudinary o prefieres revisar primero?**
