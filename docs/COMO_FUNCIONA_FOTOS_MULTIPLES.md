# 📸 CÓMO FUNCIONA EL SISTEMA DE FOTOS MÚLTIPLES

## 🎯 Pregunta: ¿Cómo sabe el backend cuál es foto principal, secundaria, etc.?

---

## 🔢 SISTEMA DE ORDEN

### 1. **Frontend envía con nombres específicos:**

```dart
FormData formData = FormData();
formData.files.add(MapEntry('foto_1', foto1));  // ← Primera foto
formData.files.add(MapEntry('foto_2', foto2));  // ← Segunda foto
formData.files.add(MapEntry('foto_3', foto3));  // ← Tercera foto
formData.files.add(MapEntry('foto_4', foto4));  // ← Cuarta foto
```

**Los nombres importan:**
- `foto_1` = Primera foto (será la principal)
- `foto_2` = Segunda foto
- `foto_3` = Tercera foto
- `foto_4` = Cuarta foto

---

### 2. **Backend recibe en el endpoint:**

```python
@router.post("/{gallo_id}/fotos-multiples")
async def actualizar_fotos_multiples_gallo(
    gallo_id: int,
    foto_1: Optional[UploadFile] = File(None),  # ← Foto principal
    foto_2: Optional[UploadFile] = File(None),  # ← Foto 2
    foto_3: Optional[UploadFile] = File(None),  # ← Foto 3
    foto_4: Optional[UploadFile] = File(None),  # ← Foto 4
):
```

**FastAPI hace el mapeo automático:**
- Campo `foto_1` del FormData → Parámetro `foto_1` del endpoint
- Campo `foto_2` del FormData → Parámetro `foto_2` del endpoint
- etc.

---

### 3. **Backend procesa en orden:**

```python
# Línea 1238
fotos = [foto_1, foto_2, foto_3, foto_4]

# Línea 1240
for i, foto in enumerate(fotos):
    # i = 0 → foto_1 (principal)
    # i = 1 → foto_2
    # i = 2 → foto_3
    # i = 3 → foto_4
```

---

### 4. **Backend marca la primera como principal:**

```python
# Línea 1258-1268
foto_obj = {
    "url": upload_result['url'],
    "orden": i + 1,                    # ← 1, 2, 3, 4
    "es_principal": i == 0,            # ← TRUE solo para foto_1
    "descripcion": f"Foto {i+1}",      # ← "Foto 1", "Foto 2", etc.
}
```

**Lógica:**
- `i == 0` → `es_principal: true` (foto_1)
- `i == 1` → `es_principal: false` (foto_2)
- `i == 2` → `es_principal: false` (foto_3)
- `i == 3` → `es_principal: false` (foto_4)

---

### 5. **Backend guarda la principal en campo separado:**

```python
# Línea 1274-1275
if i == 0:
    foto_principal_url = upload_result['url']
```

Luego actualiza la BD:

```python
# Línea 1291-1298
UPDATE gallos
SET fotos_adicionales = :fotos_json,        # ← Array JSON con todas
    foto_principal_url = :foto_principal,   # ← URL de foto_1
    url_foto_cloudinary = :foto_optimizada  # ← URL optimizada de foto_1
```

---

## 📊 ESTRUCTURA EN BASE DE DATOS

### Campo `fotos_adicionales` (JSON):

```json
[
  {
    "url": "https://ik.imagekit.io/xxx/foto1.jpg",
    "orden": 1,
    "es_principal": true,          // ← PRINCIPAL
    "descripcion": "Foto 1",
    "file_id": "abc123"
  },
  {
    "url": "https://ik.imagekit.io/xxx/foto2.jpg",
    "orden": 2,
    "es_principal": false,         // ← SECUNDARIA
    "descripcion": "Foto 2",
    "file_id": "def456"
  },
  {
    "url": "https://ik.imagekit.io/xxx/foto3.jpg",
    "orden": 3,
    "es_principal": false,         // ← TERCIARIA
    "descripcion": "Foto 3",
    "file_id": "ghi789"
  },
  {
    "url": "https://ik.imagekit.io/xxx/foto4.jpg",
    "orden": 4,
    "es_principal": false,         // ← CUARTA
    "descripcion": "Foto 4",
    "file_id": "jkl012"
  }
]
```

### Campo `foto_principal_url`:
```
"https://ik.imagekit.io/xxx/foto1.jpg"
```
(Siempre apunta a la primera foto)

---

## 🔄 FLUJO COMPLETO

### Ejemplo: Usuario sube 3 fotos

**1. Frontend:**
```dart
FormData:
- foto_1: gallo_frente.jpg
- foto_2: gallo_lado.jpg
- foto_3: gallo_espalda.jpg
```

**2. Backend procesa:**
```
i=0 → foto_1 (gallo_frente.jpg)
  ✅ Sube a ImageKit
  ✅ Marca es_principal: true
  ✅ Guarda en foto_principal_url
  ✅ orden: 1

i=1 → foto_2 (gallo_lado.jpg)
  ✅ Sube a ImageKit
  ✅ Marca es_principal: false
  ✅ orden: 2

i=2 → foto_3 (gallo_espalda.jpg)
  ✅ Sube a ImageKit
  ✅ Marca es_principal: false
  ✅ orden: 3

i=3 → foto_4 (None)
  ⏭️ Salta (no hay foto)
```

**3. Resultado en BD:**
```sql
UPDATE gallos SET
  foto_principal_url = 'https://.../gallo_frente.jpg',
  fotos_adicionales = '[
    {"orden": 1, "es_principal": true, "url": "...gallo_frente.jpg"},
    {"orden": 2, "es_principal": false, "url": "...gallo_lado.jpg"},
    {"orden": 3, "es_principal": false, "url": "...gallo_espalda.jpg"}
  ]'
```

---

## 🎨 FRONTEND: Cómo mostrar las fotos

### Opción 1: Usar solo `foto_principal_url`
```dart
Image.network(gallo.fotoPrincipalUrl)
```

### Opción 2: Mostrar todas las fotos
```dart
// Parsear fotos_adicionales
List<FotoGallo> fotos = (gallo.fotosAdicionales as List)
    .map((f) => FotoGallo.fromJson(f))
    .toList();

// Ordenar por campo "orden"
fotos.sort((a, b) => a.orden.compareTo(b.orden));

// Mostrar en galería
PageView.builder(
  itemCount: fotos.length,
  itemBuilder: (context, index) {
    final foto = fotos[index];
    return Column(
      children: [
        Image.network(foto.url),
        if (foto.esPrincipal) 
          Text('⭐ Principal'),
        Text('Foto ${foto.orden}'),
      ],
    );
  },
)
```

### Opción 3: Mostrar principal + thumbnails
```dart
// Principal grande
Image.network(gallo.fotoPrincipalUrl)

// Thumbnails pequeños
Row(
  children: fotos.where((f) => !f.esPrincipal).map((f) =>
    GestureDetector(
      onTap: () => cambiarPrincipal(f),
      child: Image.network(f.url, width: 60, height: 60),
    )
  ).toList(),
)
```

---

## ❓ PREGUNTAS FRECUENTES

### ¿Puedo cambiar cuál es la principal después?

**SÍ**, tienes dos opciones:

**Opción A: Endpoint específico**
```
PUT /gallos-con-pedigri/{gallo_id}/foto-principal
Body: { "foto_url": "https://..." }
```

**Opción B: Reordenar el array JSON**
Cambiar el campo `es_principal` en `fotos_adicionales`.

---

### ¿Qué pasa si solo subo 1 foto?

```
Frontend envía:
- foto_1: mi_gallo.jpg

Backend procesa:
- i=0 → foto_1 ✅ (principal)
- i=1 → foto_2 ⏭️ (None, se salta)
- i=2 → foto_3 ⏭️ (None, se salta)
- i=3 → foto_4 ⏭️ (None, se salta)

Resultado:
- foto_principal_url = "https://.../mi_gallo.jpg"
- fotos_adicionales = [{"orden": 1, "es_principal": true, ...}]
```

---

### ¿Qué pasa si subo foto_2 pero no foto_1?

**NO RECOMENDADO**, pero técnicamente:

```
Frontend envía:
- foto_2: segunda.jpg

Backend procesa:
- i=0 → foto_1 ⏭️ (None)
- i=1 → foto_2 ✅ (se marca como es_principal: false)

Resultado:
- foto_principal_url = None ❌
- fotos_adicionales = [{"orden": 2, "es_principal": false, ...}]
```

**Problema:** No hay foto principal.

**Solución:** Siempre enviar foto_1 primero.

---

### ¿Puedo subir más de 4 fotos?

**NO** con este endpoint. Máximo 4 fotos.

Si necesitas más:
1. Sube las primeras 4 con `/fotos-multiples`
2. Usa otro endpoint para agregar más

O modifica el endpoint para aceptar más parámetros:
```python
foto_5: Optional[UploadFile] = File(None),
foto_6: Optional[UploadFile] = File(None),
# etc.
```

---

## 🔑 RESUMEN

| Concepto | Explicación |
|----------|-------------|
| **Orden** | Definido por nombre del campo (`foto_1`, `foto_2`, etc.) |
| **Principal** | Siempre es `foto_1` (primera en el array) |
| **Identificación** | Campo `es_principal: true` en JSON |
| **Almacenamiento** | Array JSON + campo separado `foto_principal_url` |
| **Máximo** | 4 fotos por request |
| **Orden en BD** | Campo `orden: 1, 2, 3, 4` |

---

**Documento creado:** 2025-11-16  
**Autor:** Backend Team  
**Estado:** ✅ Documentación Completa
