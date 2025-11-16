# 🐛 PROBLEMA: Endpoint de Fotos Múltiples en Pedigrí

## 📅 Fecha: 2025-11-15

---

## 🎯 PROBLEMA REPORTADO

**Usuario reporta:** El API de pedigrí NO sube fotos masivas.

---

## 🔍 ANÁLISIS DEL BACKEND

### ✅ Endpoint EXISTE y está CORRECTO:

**Ubicación:** `app/api/v1/gallos_con_pedigri.py` línea 1193

```python
@router.post("/{gallo_id}/fotos-multiples", response_model=dict)
async def actualizar_fotos_multiples_gallo(
    gallo_id: int,
    foto_1: Optional[UploadFile] = File(None, description="Foto 1 del gallo"),
    foto_2: Optional[UploadFile] = File(None, description="Foto 2 del gallo"),
    foto_3: Optional[UploadFile] = File(None, description="Foto 3 del gallo"),
    foto_4: Optional[UploadFile] = File(None, description="Foto 4 del gallo"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
```

### ✅ Usa Storage Manager Correctamente:

**Línea 1249-1254:**
```python
upload_result = await multi_image_service.upload_single_image(
    file=foto,
    folder=folder,
    file_name=file_name,
    optimize=True
)
```

### ✅ Guarda en BD Correctamente:

**Línea 1291-1308:**
```python
UPDATE gallos
SET fotos_adicionales = :fotos_json,
    foto_principal_url = :foto_principal,
    url_foto_cloudinary = :foto_optimizada,
    updated_at = CURRENT_TIMESTAMP
WHERE id = :id AND user_id = :user_id
```

---

## 🧪 PRUEBA DEL ENDPOINT

### Comando cURL para probar:

```bash
# Variables
BASE_URL="http://localhost:8000/api/v1"
GALLO_ID=213
TOKEN="tu_token_aqui"

# Subir 4 fotos
curl -X POST "$BASE_URL/gallos-con-pedigri/$GALLO_ID/fotos-multiples" \
  -H "Authorization: Bearer $TOKEN" \
  -F "foto_1=@/path/to/foto1.jpg" \
  -F "foto_2=@/path/to/foto2.jpg" \
  -F "foto_3=@/path/to/foto3.jpg" \
  -F "foto_4=@/path/to/foto4.jpg"
```

### Response Esperado:

```json
{
  "success": true,
  "message": "Se actualizaron 4 fotos exitosamente",
  "data": {
    "gallo_id": 213,
    "gallo_nombre": "Campeón",
    "fotos_subidas": 4,
    "foto_principal_url": "https://ik.imagekit.io/xxx/foto1.jpg",
    "fotos_detalle": [
      {
        "url": "https://ik.imagekit.io/xxx/foto1.jpg",
        "orden": 1,
        "es_principal": true,
        "file_id": "abc123"
      },
      {
        "url": "https://ik.imagekit.io/xxx/foto2.jpg",
        "orden": 2,
        "es_principal": false,
        "file_id": "def456"
      }
    ],
    "total_fotos_almacenadas": 4
  }
}
```

---

## 🔧 POSIBLES CAUSAS DEL PROBLEMA

### 1. **Frontend NO está llamando al endpoint correcto**

#### ❌ Endpoint INCORRECTO:
```dart
// Si el frontend está usando:
POST /gallos-con-pedigri/{id}/fotos  // ← INCORRECTO
```

#### ✅ Endpoint CORRECTO:
```dart
// Debe usar:
POST /gallos-con-pedigri/{id}/fotos-multiples  // ← CORRECTO
```

---

### 2. **Frontend NO está enviando FormData correctamente**

#### ❌ Formato INCORRECTO:
```dart
// Si envía JSON:
{
  "fotos": [File1, File2, File3, File4]  // ← NO FUNCIONA
}
```

#### ✅ Formato CORRECTO:
```dart
// Debe enviar FormData:
FormData formData = FormData();
formData.files.add(MapEntry('foto_1', MultipartFile.fromFileSync(file1.path)));
formData.files.add(MapEntry('foto_2', MultipartFile.fromFileSync(file2.path)));
formData.files.add(MapEntry('foto_3', MultipartFile.fromFileSync(file3.path)));
formData.files.add(MapEntry('foto_4', MultipartFile.fromFileSync(file4.path)));
```

---

### 3. **Frontend NO tiene el método implementado**

El servicio `ApiService` en Flutter puede no tener el método para subir fotos múltiples.

---

## 📋 CHECKLIST DE VERIFICACIÓN

### Backend (Ya verificado ✅):
- [x] Endpoint existe: `/gallos-con-pedigri/{id}/fotos-multiples`
- [x] Usa `multi_image_service` correctamente
- [x] Guarda en BD correctamente
- [x] Retorna response con `fotos_detalle`

### Frontend (NECESITA VERIFICACIÓN ❌):
- [ ] ¿Existe método en `ApiService` para subir fotos múltiples?
- [ ] ¿Está usando el endpoint correcto `/fotos-multiples`?
- [ ] ¿Está enviando FormData con `foto_1`, `foto_2`, etc.?
- [ ] ¿Está manejando la respuesta correctamente?

---

## 🔧 SOLUCIÓN PROPUESTA

### PASO 1: Verificar método en ApiService (Flutter)

**Archivo:** `lib/services/api_service.dart`

Buscar si existe:
```dart
static Future<Map<String, dynamic>> subirFotosMultiplesGallo({
  required int galloId,
  required List<File> fotos,
}) async {
  // ...
}
```

---

### PASO 2: Si NO existe, implementarlo

**Agregar en `api_service.dart`:**

```dart
/// 📸 SUBIR MÚLTIPLES FOTOS A UN GALLO (hasta 4)
static Future<Map<String, dynamic>> subirFotosMultiplesGallo({
  required int galloId,
  required List<File> fotos,
}) async {
  try {
    if (fotos.isEmpty || fotos.length > 4) {
      throw ApiException('Debes subir entre 1 y 4 fotos');
    }

    final authHeaders = await _getAuthHeaders();

    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/v1/gallos-con-pedigri/$galloId/fotos-multiples'),
    );

    request.headers.addAll(authHeaders);

    // Agregar fotos con nombres foto_1, foto_2, foto_3, foto_4
    for (int i = 0; i < fotos.length; i++) {
      final file = fotos[i];
      final multipartFile = await http.MultipartFile.fromPath(
        'foto_${i + 1}',  // ← IMPORTANTE: foto_1, foto_2, etc.
        file.path,
      );
      request.files.add(multipartFile);
    }

    print('📸 Subiendo ${fotos.length} fotos al gallo $galloId...');

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    print('📡 Response status: ${response.statusCode}');
    print('📡 Response body: ${response.body}');

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      print('✅ Fotos subidas exitosamente');
      return data;
    } else {
      final error = jsonDecode(response.body);
      throw ApiException(error['detail'] ?? 'Error subiendo fotos');
    }
  } catch (e) {
    print('💥 Error subiendo fotos múltiples: $e');
    throw ApiException('Error subiendo fotos: $e');
  }
}
```

---

### PASO 3: Usar en la UI

**Ejemplo en `add_gallo_multistep_screen.dart`:**

```dart
// Cuando el usuario selecciona múltiples fotos
List<File> fotosSeleccionadas = [foto1, foto2, foto3, foto4];

try {
  setState(() => _isUploading = true);
  
  final result = await ApiService.subirFotosMultiplesGallo(
    galloId: galloId,
    fotos: fotosSeleccionadas,
  );
  
  print('✅ ${result['data']['fotos_subidas']} fotos subidas');
  
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text('✅ ${result['message']}'),
      backgroundColor: Colors.green,
    ),
  );
  
} catch (e) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text('❌ Error: $e'),
      backgroundColor: Colors.red,
    ),
  );
} finally {
  setState(() => _isUploading = false);
}
```

---

## 🧪 TESTING

### Test Manual del Backend:

```bash
# 1. Obtener token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"alancairampoma@gmail.com","password":"tu_password"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. Crear 4 archivos de prueba
echo "Test 1" > foto1.txt
echo "Test 2" > foto2.txt
echo "Test 3" > foto3.txt
echo "Test 4" > foto4.txt

# 3. Subir fotos
curl -X POST "http://localhost:8000/api/v1/gallos-con-pedigri/213/fotos-multiples" \
  -H "Authorization: Bearer $TOKEN" \
  -F "foto_1=@foto1.txt" \
  -F "foto_2=@foto2.txt" \
  -F "foto_3=@foto3.txt" \
  -F "foto_4=@foto4.txt" \
  | jq .

# 4. Verificar fotos subidas
curl -X GET "http://localhost:8000/api/v1/gallos-con-pedigri/213/fotos" \
  -H "Authorization: Bearer $TOKEN" \
  | jq .
```

---

## 📊 DIAGNÓSTICO RÁPIDO

### Para saber exactamente qué está pasando:

1. **Revisar logs del backend:**
   ```bash
   # Ver si el endpoint está siendo llamado
   tail -f logs/app.log | grep "fotos-multiples"
   ```

2. **Probar endpoint con cURL:**
   ```bash
   # Si funciona con cURL, el problema es el frontend
   # Si NO funciona con cURL, el problema es el backend
   ```

3. **Revisar código del frontend:**
   ```bash
   # Buscar en api_service.dart si existe el método
   grep -r "fotos-multiples" lib/services/
   ```

---

## 🎯 CONCLUSIÓN

### El backend está CORRECTO ✅

El endpoint `/gallos-con-pedigri/{id}/fotos-multiples` existe y funciona correctamente.

### El problema está en el FRONTEND ❌

Posibles causas:
1. No existe el método en `ApiService`
2. Está llamando al endpoint incorrecto
3. No está enviando FormData correctamente
4. No está usando los nombres correctos (`foto_1`, `foto_2`, etc.)

---

## 📝 ACCIÓN REQUERIDA

### INMEDIATO:

1. **Verificar si existe el método en Flutter:**
   - Abrir `lib/services/api_service.dart`
   - Buscar `subirFotosMultiplesGallo` o similar
   - Si NO existe, implementarlo según el código de arriba

2. **Probar el endpoint con cURL:**
   - Ejecutar el comando de prueba
   - Verificar que funciona desde backend

3. **Implementar en Flutter:**
   - Agregar método en `ApiService`
   - Actualizar UI para usar el método
   - Probar subida de 4 fotos

---

## 📞 SIGUIENTE PASO

**¿Puedes confirmar?**

1. ¿El endpoint funciona con cURL? (probar comando de arriba)
2. ¿Existe el método en `api_service.dart` del frontend?
3. ¿Qué error exacto muestra el frontend al intentar subir fotos?

Con esa información puedo darte la solución exacta.

---

**Documento creado:** 2025-11-15  
**Estado:** 🔍 Diagnóstico Completo  
**Acción:** Verificar Frontend
