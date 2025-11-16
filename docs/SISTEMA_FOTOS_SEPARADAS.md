# 🎯 SISTEMA DE FOTOS SEPARADAS - DOCUMENTACIÓN

## 📋 RESUMEN

El sistema de fotos ahora **separa completamente** la foto principal de las fotos adicionales para evitar que se mezclen o se corran de posición.

---

## 🏗️ ESTRUCTURA

### Base de Datos (tabla `gallos`):

```sql
gallos
├── foto_principal_url      VARCHAR  -- URL de la foto principal (1 sola)
├── url_foto_cloudinary     VARCHAR  -- Copia optimizada (legacy)
└── fotos_adicionales       JSONB    -- Array de fotos adicionales (máx 3)
```

### Endpoint de Actualización:

```
POST /api/v1/gallos-con-pedigri/{id}/fotos-multiples
```

**Parámetros:**
- `foto_1`: File (opcional) → Va a `foto_principal_url`
- `foto_2`: File (opcional) → Va a `fotos_adicionales[0]`
- `foto_3`: File (opcional) → Va a `fotos_adicionales[1]`
- `foto_4`: File (opcional) → Va a `fotos_adicionales[2]`
- `actualizar_principal`: bool (opcional) → Forzar actualización de foto principal

---

## 🔄 LÓGICA DE ACTUALIZACIÓN

### Paso 1: Subir Fotos por Separado

```python
# 2.1 SUBIR FOTO PRINCIPAL (foto_1)
if foto_1:
    foto_principal_subida = await multi_image_service.upload_single_image(
        file=foto_1,
        file_name=f"gallo_{codigo}_principal_{foto_1.filename}"
    )

# 2.2 SUBIR FOTOS ADICIONALES (foto_2, foto_3, foto_4)
fotos_adicionales = [foto_2, foto_3, foto_4]
fotos_adicionales_json = []

for i, foto in enumerate(fotos_adicionales):
    if foto:
        foto_numero = i + 2  # 2, 3, 4
        upload_result = await multi_image_service.upload_single_image(
            file=foto,
            file_name=f"gallo_{codigo}_foto_{foto_numero}_{foto.filename}"
        )
        fotos_adicionales_json.append({
            "url": upload_result['url'],
            "orden": foto_numero,
            "es_principal": False
        })
```

### Paso 2: Decidir Qué Actualizar

```python
debe_actualizar_principal = (
    not gallo.foto_principal_url or      # No tiene foto principal
    es_cloudinary or                     # Es foto de Cloudinary (legacy)
    actualizar_principal                 # Usuario fuerza actualización
)
```

### Paso 3: Actualizar Base de Datos

#### Caso 1: Solo Foto Principal

```sql
UPDATE gallos
SET foto_principal_url = :foto_principal,
    url_foto_cloudinary = :foto_optimizada
WHERE id = :gallo_id
```

**Resultado:**
- ✅ `foto_principal_url` actualizada
- ✅ `fotos_adicionales` NO cambian

#### Caso 2: Solo Fotos Adicionales

```sql
UPDATE gallos
SET fotos_adicionales = :fotos_json
WHERE id = :gallo_id
```

**Resultado:**
- ✅ `fotos_adicionales` actualizadas
- ✅ `foto_principal_url` NO cambia

#### Caso 3: Foto Principal + Adicionales

```sql
UPDATE gallos
SET foto_principal_url = :foto_principal,
    url_foto_cloudinary = :foto_optimizada,
    fotos_adicionales = :fotos_json
WHERE id = :gallo_id
```

**Resultado:**
- ✅ `foto_principal_url` actualizada
- ✅ `fotos_adicionales` actualizadas
- ✅ Cada foto en su posición correcta

---

## 🗑️ ELIMINACIÓN DE FOTOS

### Endpoint:

```
DELETE /api/v1/gallos-con-pedigri/{gallo_id}/fotos/{public_id}
```

### Lógica:

```python
# 1. Obtener fotos actuales
fotos_adicionales = json.loads(gallo.fotos_adicionales)

# 2. Filtrar la foto eliminada
fotos_adicionales = [
    foto for foto in fotos_adicionales
    if foto.get('cloudinary_public_id') != public_id
]

# 3. Actualizar SOLO fotos_adicionales
UPDATE gallos
SET fotos_adicionales = :fotos_json
WHERE id = :gallo_id
```

**Resultado:**
- ✅ Foto eliminada de `fotos_adicionales`
- ✅ `foto_principal_url` NO se toca
- ✅ Las demás fotos mantienen su posición

---

## 📊 EJEMPLOS DE USO

### Ejemplo 1: Crear Gallo con 4 Fotos

**Request:**
```bash
POST /api/v1/gallos-con-pedigri/{id}/fotos-multiples
Content-Type: multipart/form-data

foto_1: [archivo1.jpg]  # Foto principal
foto_2: [archivo2.jpg]  # Adicional 1
foto_3: [archivo3.jpg]  # Adicional 2
foto_4: [archivo4.jpg]  # Adicional 3
```

**Resultado en BD:**
```json
{
  "foto_principal_url": "https://imagekit.io/.../principal_archivo1.jpg",
  "fotos_adicionales": [
    {
      "url": "https://imagekit.io/.../foto_2_archivo2.jpg",
      "orden": 2,
      "es_principal": false
    },
    {
      "url": "https://imagekit.io/.../foto_3_archivo3.jpg",
      "orden": 3,
      "es_principal": false
    },
    {
      "url": "https://imagekit.io/.../foto_4_archivo4.jpg",
      "orden": 4,
      "es_principal": false
    }
  ]
}
```

### Ejemplo 2: Actualizar Solo Foto Principal

**Request:**
```bash
POST /api/v1/gallos-con-pedigri/{id}/fotos-multiples
Content-Type: multipart/form-data

foto_1: [nueva_principal.jpg]  # Nueva foto principal
actualizar_principal: true
```

**Resultado:**
```json
{
  "foto_principal_url": "https://imagekit.io/.../principal_nueva_principal.jpg",  // ✅ Actualizada
  "fotos_adicionales": [
    // ✅ Mantienen las mismas 3 fotos anteriores
  ]
}
```

### Ejemplo 3: Actualizar Solo Fotos Adicionales

**Request:**
```bash
POST /api/v1/gallos-con-pedigri/{id}/fotos-multiples
Content-Type: multipart/form-data

foto_2: [nueva_adicional1.jpg]
foto_3: [nueva_adicional2.jpg]
foto_4: [nueva_adicional3.jpg]
```

**Resultado:**
```json
{
  "foto_principal_url": "https://imagekit.io/.../principal_anterior.jpg",  // ✅ NO cambia
  "fotos_adicionales": [
    {
      "url": "https://imagekit.io/.../foto_2_nueva_adicional1.jpg",  // ✅ Actualizada
      "orden": 2
    },
    {
      "url": "https://imagekit.io/.../foto_3_nueva_adicional2.jpg",  // ✅ Actualizada
      "orden": 3
    },
    {
      "url": "https://imagekit.io/.../foto_4_nueva_adicional3.jpg",  // ✅ Actualizada
      "orden": 4
    }
  ]
}
```

### Ejemplo 4: Eliminar Foto Adicional

**Request:**
```bash
DELETE /api/v1/gallos-con-pedigri/{id}/fotos/{public_id}
```

**Resultado:**
```json
{
  "foto_principal_url": "https://imagekit.io/.../principal.jpg",  // ✅ NO cambia
  "fotos_adicionales": [
    // ✅ Solo quedan 2 fotos (la eliminada ya no está)
    {
      "url": "https://imagekit.io/.../foto_2.jpg",
      "orden": 2
    },
    {
      "url": "https://imagekit.io/.../foto_4.jpg",
      "orden": 4
    }
  ]
}
```

---

## ✅ VENTAJAS DEL SISTEMA

1. **Separación Clara**: Foto principal y adicionales nunca se mezclan
2. **Posiciones Fijas**: Cada foto mantiene su posición (no se corren)
3. **Actualización Independiente**: Puedes actualizar solo principal, solo adicionales, o ambas
4. **Eliminación Segura**: Eliminar una foto adicional no afecta la principal
5. **Migración de Cloudinary**: Detecta fotos legacy y las migra automáticamente

---

## 🐛 PROBLEMAS RESUELTOS

### ❌ ANTES (Problema):

```python
# Todas las fotos en un solo array
fotos = [foto_1, foto_2, foto_3, foto_4]
primera_foto_subida = None

for foto in fotos:
    if primera_foto_subida is None:
        primera_foto_subida = foto  # ❌ Podía ser foto_2 si foto_1 era None

# Resultado: Las fotos se corrían de posición
```

### ✅ AHORA (Solución):

```python
# Foto principal separada
if foto_1:
    foto_principal_subida = subir(foto_1)  # ✅ SOLO foto_1

# Fotos adicionales separadas
fotos_adicionales = [foto_2, foto_3, foto_4]
for foto in fotos_adicionales:
    fotos_adicionales_json.append(subir(foto))  # ✅ NO se mezclan

# Resultado: Cada foto en su posición correcta
```

---

## 📝 NOTAS IMPORTANTES

1. **foto_1** siempre va a `foto_principal_url`
2. **foto_2, foto_3, foto_4** siempre van a `fotos_adicionales`
3. **NUNCA** se mezclan entre sí
4. **Eliminar** una foto adicional NO afecta la principal
5. **Actualizar** la principal NO afecta las adicionales (a menos que se fuerce con `actualizar_principal=true`)

---

## 🔧 MANTENIMIENTO

### Para agregar más fotos adicionales:

1. Agregar parámetro `foto_5` en el endpoint
2. Agregar al array `fotos_adicionales = [foto_2, foto_3, foto_4, foto_5]`
3. Actualizar el límite en el frontend

### Para cambiar el comportamiento:

Modificar la lógica en `debe_actualizar_principal`:

```python
debe_actualizar_principal = (
    not gallo.foto_principal_url or  # Agregar/quitar condiciones aquí
    es_cloudinary or
    actualizar_principal
)
```

---

**Última actualización:** 2025-01-16  
**Versión:** 2.0 (Sistema de Fotos Separadas)
