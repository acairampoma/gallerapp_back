# 🔍 DEBUG: Fotos Múltiples No Se Suben

## 📅 Fecha: 2025-11-16

---

## 🎯 PROBLEMA IDENTIFICADO

**Antes:** Funcionaba con Cloudinary directo
**Ahora:** NO funciona con Storage Manager (migración)

**Error del frontend:**
```
📡 Response /fotos-multiples: 400
❌ Error subiendo fotos: No se pudo subir ninguna foto. Verifica que los archivos sean válidos.
```

---

## 🔍 ANÁLISIS DEL FLUJO

### 1. Frontend envía correctamente:
```
📸 Foto WEB agregada: scaled_edificio.png (112326 bytes)
✅ Foto adicional agregada como foto_2
📦 Request preparado con 1 fotos
```

### 2. Backend recibe en `/fotos-multiples`:
```python
@router.post("/{gallo_id}/fotos-multiples")
async def actualizar_fotos_multiples_gallo(
    foto_1: Optional[UploadFile] = File(None),
    foto_2: Optional[UploadFile] = File(None),
    foto_3: Optional[UploadFile] = File(None),
    foto_4: Optional[UploadFile] = File(None),
):
```

### 3. Validación en línea 1249:
```python
if foto and foto.filename and foto.size > 0:
```

### 4. Si pasa, llama a `multi_image_service.upload_single_image()`

### 5. Dentro del servicio, valida en línea 38:
```python
if file.content_type not in MultiImageService.ALLOWED_TYPES:
    raise HTTPException(400, "Tipo no permitido")
```

**ALLOWED_TYPES:**
```python
['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
```

---

## 🐛 POSIBLES CAUSAS

### Causa 1: `content_type` incorrecto
El frontend puede estar enviando:
- `application/octet-stream` (genérico)
- `image/jpg` vs `image/jpeg` (inconsistencia)
- `null` o vacío

### Causa 2: `filename` vacío o None
```python
if foto and foto.filename and foto.size > 0:
```

### Causa 3: `size` es 0 o None
El archivo llega pero sin tamaño válido.

---

## 🔧 CAMBIOS APLICADOS PARA DEBUG

### 1. En `gallos_con_pedigri.py` línea 1240:
```python
# 🔍 DEBUG: Ver qué fotos llegan
print(f"🔍 DEBUG FOTOS RECIBIDAS:")
for i, foto in enumerate(fotos):
    if foto:
        print(f"  Foto {i+1}: filename={foto.filename}, size={foto.size}, content_type={foto.content_type}")
    else:
        print(f"  Foto {i+1}: None")
```

### 2. En `multi_image_service.py` línea 37:
```python
# 🔍 DEBUG: Ver qué llega
print(f"🔍 VALIDANDO IMAGEN: filename={file.filename}, content_type={file.content_type}, size={getattr(file, 'size', 'N/A')}")

if file.content_type not in MultiImageService.ALLOWED_TYPES:
    print(f"❌ TIPO RECHAZADO: {file.content_type} no está en {MultiImageService.ALLOWED_TYPES}")
```

---

## 📋 PRÓXIMOS PASOS

### 1. Reiniciar servidor:
```bash
# Detener servidor actual
Ctrl+C

# Reiniciar
uvicorn app.main:app --reload
```

### 2. Probar desde frontend:
- Intentar subir 1 foto
- Ver logs del backend

### 3. Analizar logs:
Buscar en consola del backend:
```
🔍 DEBUG FOTOS RECIBIDAS:
  Foto 1: filename=..., size=..., content_type=...
  
🔍 VALIDANDO IMAGEN: filename=..., content_type=..., size=...
```

---

## 🎯 SOLUCIONES SEGÚN EL PROBLEMA

### Si `content_type` es incorrecto:

**Opción A: Hacer validación más flexible**
```python
# En multi_image_service.py línea 41
ALLOWED_TYPES = [
    'image/jpeg', 'image/jpg', 'image/png', 'image/webp',
    'application/octet-stream'  # ← Agregar genérico
]
```

**Opción B: Detectar tipo por extensión**
```python
# Si content_type es genérico, detectar por filename
if file.content_type == 'application/octet-stream':
    ext = file.filename.split('.')[-1].lower()
    if ext in ['jpg', 'jpeg', 'png', 'webp']:
        # Permitir
        pass
```

---

### Si `filename` está vacío:

**Generar nombre automático:**
```python
if not foto.filename:
    foto.filename = f"foto_{i+1}.jpg"
```

---

### Si `size` es 0:

**No validar size:**
```python
# Cambiar línea 1249
if foto and foto.filename:  # ← Quitar validación de size
```

---

## 🔬 COMPARACIÓN: ANTES vs AHORA

### ANTES (Cloudinary directo):
```python
# No había validación estricta de content_type
cloudinary.uploader.upload(file)  # Aceptaba cualquier cosa
```

### AHORA (Storage Manager):
```python
# Validación estricta
if file.content_type not in ALLOWED_TYPES:
    raise HTTPException(400)  # ← AQUÍ SE RECHAZA
```

---

## ✅ ACCIÓN INMEDIATA

1. **Reiniciar servidor** con los logs de debug
2. **Probar subir foto** desde frontend
3. **Copiar logs completos** que aparezcan
4. **Enviarme los logs** para ver exactamente qué está pasando

Los logs mostrarán:
- ✅ Si las fotos llegan al endpoint
- ✅ Qué `content_type` tienen
- ✅ Si tienen `filename` y `size`
- ✅ En qué punto exacto se rechazan

---

**Documento creado:** 2025-11-16  
**Estado:** 🔍 Debug activado  
**Siguiente:** Ver logs del servidor
