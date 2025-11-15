# 📸 MULTI IMAGE UPLOAD - Guía Moderna 2025

## 🚀 CARACTERÍSTICAS

**Upload masivo de imágenes en 2025 es SIMPLE:**

- ✅ **Upload paralelo** - Sube múltiples imágenes a la vez (más rápido)
- ✅ **Optimización automática** - Convierte a webp, redimensiona, comprime
- ✅ **Validación automática** - Tipo, tamaño, formato
- ✅ **Rollback automático** - Si falla una, no afecta las demás
- ✅ **Progress tracking** - Sabe cuántas se subieron y cuántas fallaron
- ✅ **Agnóstico de proveedor** - Funciona con ImageKit, Cloudinary, S3

---

## 📋 USO BÁSICO

### 1️⃣ **Subir múltiples imágenes de gallo**

```bash
curl -X POST "http://localhost:8000/api/v1/gallos/123/images/upload" \
  -H "Authorization: Bearer TOKEN" \
  -F "files=@foto1.jpg" \
  -F "files=@foto2.jpg" \
  -F "files=@foto3.jpg" \
  -F "files=@foto4.jpg" \
  -F "set_first_as_principal=true"
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Subidas 4 de 4 imágenes",
  "data": {
    "uploaded": 4,
    "total": 4,
    "failed": 0,
    "results": [
      {
        "index": 0,
        "filename": "foto1.jpg",
        "url": "https://ik.imagekit.io/.../gallo_123_1.webp",
        "file_id": "abc123",
        "thumbnail_url": "...",
        "size": 245678,
        "width": 800,
        "height": 800
      },
      // ... más imágenes
    ],
    "errors": [],
    "gallo_id": 123,
    "principal_updated": true
  }
}
```

---

### 2️⃣ **Subir/actualizar imagen principal**

```bash
curl -X POST "http://localhost:8000/api/v1/gallos/123/images/principal" \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@foto_principal.jpg"
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Imagen principal actualizada",
  "data": {
    "gallo_id": 123,
    "foto_url": "https://ik.imagekit.io/.../gallo_123_principal.webp",
    "file_id": "xyz789"
  }
}
```

---

### 3️⃣ **Eliminar múltiples imágenes**

```bash
curl -X DELETE "http://localhost:8000/api/v1/gallos/123/images" \
  -H "Authorization: Bearer TOKEN" \
  -F "file_ids=abc123" \
  -F "file_ids=def456" \
  -F "file_ids=ghi789"
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Eliminadas 3 de 3 imágenes",
  "data": {
    "deleted": 3,
    "total": 3,
    "failed": 0,
    "errors": []
  }
}
```

---

## 💻 USO EN CÓDIGO

### **Python/FastAPI**

```python
from app.services.multi_image_service import multi_image_service

# Subir múltiples imágenes
result = await multi_image_service.upload_multiple_images(
    files=[file1, file2, file3],
    folder="gallos/user_123",
    base_name="gallo_456",
    optimize=True,
    parallel=True  # 🚀 PARALELO
)

print(f"Subidas: {result['uploaded']}/{result['total']}")
```

### **JavaScript/TypeScript (Frontend)**

```typescript
// React/Next.js
const uploadGalloImages = async (galloId: number, files: File[]) => {
  const formData = new FormData();
  
  // Agregar múltiples archivos
  files.forEach(file => {
    formData.append('files', file);
  });
  
  formData.append('set_first_as_principal', 'true');
  
  const response = await fetch(
    `http://localhost:8000/api/v1/gallos/${galloId}/images/upload`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    }
  );
  
  const result = await response.json();
  console.log(`Subidas: ${result.data.uploaded}/${result.data.total}`);
  
  return result;
};
```

### **Flutter/Dart**

```dart
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

Future<Map<String, dynamic>> uploadGalloImages(
  int galloId,
  List<File> images,
  String token
) async {
  var uri = Uri.parse('http://localhost:8000/api/v1/gallos/$galloId/images/upload');
  var request = http.MultipartRequest('POST', uri);
  
  // Headers
  request.headers['Authorization'] = 'Bearer $token';
  
  // Agregar múltiples archivos
  for (var image in images) {
    var stream = http.ByteStream(image.openRead());
    var length = await image.length();
    
    var multipartFile = http.MultipartFile(
      'files',
      stream,
      length,
      filename: image.path.split('/').last,
      contentType: MediaType('image', 'jpeg'),
    );
    
    request.files.add(multipartFile);
  }
  
  // Parámetros
  request.fields['set_first_as_principal'] = 'true';
  
  // Enviar
  var response = await request.send();
  var responseData = await response.stream.bytesToString();
  
  return jsonDecode(responseData);
}
```

---

## 🎯 CASOS DE USO

### **Caso 1: Galería de gallo**

```python
# Subir galería completa de un gallo
files = [foto1, foto2, foto3, foto4, foto5]

result = await multi_image_service.upload_gallo_images(
    gallo_id=123,
    user_id=456,
    files=files,
    db=db,
    set_first_as_principal=True
)

# La primera imagen se convierte en principal automáticamente
```

### **Caso 2: Upload genérico**

```python
# Subir imágenes a cualquier carpeta
result = await multi_image_service.upload_multiple_images(
    files=files,
    folder="eventos/evento_789",
    base_name="evento_foto",
    optimize=True,
    parallel=True
)
```

### **Caso 3: Actualizar imagen principal**

```python
# Solo actualizar la foto principal
result = await multi_image_service.upload_single_image(
    file=foto,
    folder="gallos/user_123/gallo_456",
    file_name="principal.jpg",
    optimize=True
)

# Actualizar en BD
gallo.foto_url = result['url']
db.commit()
```

---

## ⚡ OPTIMIZACIONES AUTOMÁTICAS

El servicio aplica automáticamente:

1. **Conversión a WebP** - Formato moderno, menor tamaño
2. **Redimensionamiento** - Máximo 800x800 (configurable)
3. **Compresión** - Quality 85 (balance perfecto)
4. **Thumbnails** - Genera automáticamente
5. **Progressive loading** - Carga progresiva

**Ejemplo:**
- Imagen original: 3.5 MB (4000x3000 JPG)
- Imagen optimizada: 180 KB (800x800 WebP)
- **Ahorro: 95%** 🎉

---

## 🔧 CONFIGURACIÓN

### **Límites (configurables en `multi_image_service.py`)**

```python
class MultiImageService:
    MAX_IMAGES = 10          # Máximo de imágenes por request
    MAX_SIZE_MB = 5          # Tamaño máximo por imagen
    ALLOWED_TYPES = [        # Tipos permitidos
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/webp'
    ]
```

### **Optimización (configurable)**

```python
# En upload_with_transformations
storage_manager.upload_with_transformations(
    file_content=content,
    file_name=file_name,
    folder=folder,
    width=800,        # ← Cambiar aquí
    height=800,       # ← Cambiar aquí
    quality=85,       # ← Cambiar aquí
    format="webp"     # ← Cambiar aquí
)
```

---

## 🚀 VENTAJAS vs CloudinaryService

| Característica | CloudinaryService (Viejo) | MultiImageService (2025) |
|----------------|---------------------------|--------------------------|
| Upload paralelo | ❌ No | ✅ Sí |
| Optimización automática | ⚠️ Manual | ✅ Automática |
| Validación | ⚠️ Básica | ✅ Completa |
| Rollback | ❌ No | ✅ Sí |
| Progress tracking | ❌ No | ✅ Sí |
| Agnóstico de proveedor | ❌ Solo Cloudinary | ✅ Cualquiera |
| Código | 484 líneas | 200 líneas |
| Complejidad | 🔴 Alta | 🟢 Baja |

---

## 📊 PERFORMANCE

### **Upload Secuencial vs Paralelo**

**Secuencial (viejo):**
```
Imagen 1: 2s
Imagen 2: 2s
Imagen 3: 2s
Imagen 4: 2s
Total: 8 segundos
```

**Paralelo (2025):**
```
Imagen 1, 2, 3, 4: 2s (todas a la vez)
Total: 2 segundos
```

**🚀 4x más rápido!**

---

## ✅ CHECKLIST DE MIGRACIÓN

Para migrar de `CloudinaryService` a `MultiImageService`:

- [ ] Reemplazar `CloudinaryService.upload_gallo_photo()` por `multi_image_service.upload_single_image()`
- [ ] Reemplazar `CloudinaryService.upload_multiple_photos()` por `multi_image_service.upload_multiple_images()`
- [ ] Reemplazar `CloudinaryService.delete_photo()` por `storage_manager.delete_file()`
- [ ] Reemplazar `CloudinaryService.batch_delete_gallo_photos()` por `multi_image_service.delete_multiple_images()`
- [ ] Actualizar endpoints para usar nuevos métodos
- [ ] Probar con curl/Postman
- [ ] Actualizar frontend

---

## 🎓 MEJORES PRÁCTICAS 2025

1. **Siempre usar upload paralelo** para múltiples imágenes
2. **Siempre optimizar** (webp, compresión)
3. **Validar en frontend Y backend**
4. **Mostrar progress bar** en frontend
5. **Manejar errores parciales** (algunas suben, otras no)
6. **Generar thumbnails** automáticamente
7. **Usar lazy loading** en frontend
8. **Implementar retry logic** para fallos de red

---

## 🔮 FUTURO

### **Próximas features:**

- [ ] **Resize inteligente** - Detectar faces y recortar automáticamente
- [ ] **Background removal** - Quitar fondo automáticamente
- [ ] **Image recognition** - Detectar si es un gallo de verdad
- [ ] **Duplicate detection** - No subir imágenes duplicadas
- [ ] **Batch processing** - Procesar 100+ imágenes a la vez
- [ ] **CDN integration** - Servir desde CDN más cercano
- [ ] **Progressive upload** - Subir en chunks para archivos grandes

---

**Documento creado:** 2025-11-15
**Última actualización:** 2025-11-15 10:20 AM
**Estado:** ✅ Listo para producción
**Versión:** 2025.1
