# 📱 FLUTTER: Cómo Subir Fotos Múltiples

## 🎯 Endpoint del Backend

```
POST /api/v1/gallos-con-pedigri/{gallo_id}/fotos-multiples
```

**Acepta:**
- `foto_1` (File) - Foto principal
- `foto_2` (File) - Foto 2
- `foto_3` (File) - Foto 3
- `foto_4` (File) - Foto 4

---

## 📱 CÓDIGO FLUTTER

### 1. Método en `ApiService`

```dart
import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'https://gallerappback-production.up.railway.app';
  
  /// 📸 SUBIR FOTOS MÚLTIPLES A UN GALLO (hasta 4)
  static Future<Map<String, dynamic>> subirFotosMultiplesGallo({
    required int galloId,
    required List<File> fotos,
  }) async {
    try {
      // Validar que haya entre 1 y 4 fotos
      if (fotos.isEmpty || fotos.length > 4) {
        throw Exception('Debes subir entre 1 y 4 fotos');
      }

      // Obtener token
      final authHeaders = await _getAuthHeaders();

      // Crear request multipart
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/api/v1/gallos-con-pedigri/$galloId/fotos-multiples'),
      );

      // Agregar headers de autenticación
      request.headers.addAll(authHeaders);

      // ⭐ IMPORTANTE: Agregar fotos con nombres foto_1, foto_2, foto_3, foto_4
      for (int i = 0; i < fotos.length; i++) {
        final file = fotos[i];
        final multipartFile = await http.MultipartFile.fromPath(
          'foto_${i + 1}',  // ← CLAVE: foto_1, foto_2, foto_3, foto_4
          file.path,
        );
        request.files.add(multipartFile);
      }

      print('📸 Subiendo ${fotos.length} fotos al gallo $galloId...');

      // Enviar request
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      print('📡 Response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        print('✅ Fotos subidas exitosamente');
        print('📊 Resultado: ${data['message']}');
        return data;
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Error subiendo fotos');
      }
    } catch (e) {
      print('💥 Error subiendo fotos múltiples: $e');
      throw Exception('Error subiendo fotos: $e');
    }
  }

  // Helper para obtener headers con token
  static Future<Map<String, String>> _getAuthHeaders() async {
    final token = await _getToken(); // Tu método para obtener token
    return {
      'Authorization': 'Bearer $token',
    };
  }
}
```

---

## 🎨 USO EN LA UI

### Opción 1: Selector de Múltiples Fotos

```dart
import 'package:image_picker/image_picker.dart';
import 'dart:io';

class SubirFotosGalloScreen extends StatefulWidget {
  final int galloId;
  
  const SubirFotosGalloScreen({required this.galloId});

  @override
  State<SubirFotosGalloScreen> createState() => _SubirFotosGalloScreenState();
}

class _SubirFotosGalloScreenState extends State<SubirFotosGalloScreen> {
  final ImagePicker _picker = ImagePicker();
  List<File> _fotosSeleccionadas = [];
  bool _isUploading = false;

  /// 📸 Seleccionar múltiples fotos
  Future<void> _seleccionarFotos() async {
    try {
      final List<XFile>? images = await _picker.pickMultiImage(
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 85,
      );

      if (images != null && images.isNotEmpty) {
        // Limitar a 4 fotos
        final fotosLimitadas = images.take(4).toList();
        
        setState(() {
          _fotosSeleccionadas = fotosLimitadas
              .map((xFile) => File(xFile.path))
              .toList();
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ ${_fotosSeleccionadas.length} fotos seleccionadas'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      print('Error seleccionando fotos: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ Error seleccionando fotos'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  /// 📤 Subir fotos al backend
  Future<void> _subirFotos() async {
    if (_fotosSeleccionadas.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('⚠️ Selecciona al menos una foto'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() => _isUploading = true);

    try {
      final result = await ApiService.subirFotosMultiplesGallo(
        galloId: widget.galloId,
        fotos: _fotosSeleccionadas,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ ${result['message']}'),
            backgroundColor: Colors.green,
          ),
        );

        // Volver a la pantalla anterior
        Navigator.pop(context, true); // true = fotos actualizadas
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isUploading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Subir Fotos del Gallo'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Botón para seleccionar fotos
            ElevatedButton.icon(
              onPressed: _isUploading ? null : _seleccionarFotos,
              icon: const Icon(Icons.photo_library),
              label: const Text('Seleccionar Fotos (máx. 4)'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.all(16),
              ),
            ),

            const SizedBox(height: 20),

            // Preview de fotos seleccionadas
            if (_fotosSeleccionadas.isNotEmpty) ...[
              Text(
                '${_fotosSeleccionadas.length} foto(s) seleccionada(s):',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 10),
              
              Expanded(
                child: GridView.builder(
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 10,
                    mainAxisSpacing: 10,
                  ),
                  itemCount: _fotosSeleccionadas.length,
                  itemBuilder: (context, index) {
                    return Stack(
                      children: [
                        // Imagen
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.file(
                            _fotosSeleccionadas[index],
                            fit: BoxFit.cover,
                            width: double.infinity,
                            height: double.infinity,
                          ),
                        ),
                        
                        // Badge de orden
                        Positioned(
                          top: 8,
                          left: 8,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: index == 0 
                                  ? Colors.green 
                                  : Colors.blue,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              index == 0 ? '⭐ Principal' : 'Foto ${index + 1}',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                        
                        // Botón eliminar
                        Positioned(
                          top: 8,
                          right: 8,
                          child: IconButton(
                            icon: const Icon(Icons.close, color: Colors.white),
                            onPressed: () {
                              setState(() {
                                _fotosSeleccionadas.removeAt(index);
                              });
                            },
                            style: IconButton.styleFrom(
                              backgroundColor: Colors.red.withOpacity(0.8),
                            ),
                          ),
                        ),
                      ],
                    );
                  },
                ),
              ),
              
              const SizedBox(height: 20),
              
              // Botón subir
              ElevatedButton.icon(
                onPressed: _isUploading ? null : _subirFotos,
                icon: _isUploading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.cloud_upload),
                label: Text(
                  _isUploading 
                      ? 'Subiendo...' 
                      : 'Subir ${_fotosSeleccionadas.length} Foto(s)',
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  padding: const EdgeInsets.all(16),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
```

---

## 🎯 PUNTOS CLAVE

### 1. **Nombres de campos IMPORTANTES:**

```dart
// ✅ CORRECTO
for (int i = 0; i < fotos.length; i++) {
  final multipartFile = await http.MultipartFile.fromPath(
    'foto_${i + 1}',  // foto_1, foto_2, foto_3, foto_4
    fotos[i].path,
  );
  request.files.add(multipartFile);
}

// ❌ INCORRECTO
request.files.add(MapEntry('fotos', multipartFile));  // No funciona
request.files.add(MapEntry('foto', multipartFile));   // No funciona
request.files.add(MapEntry('imagen', multipartFile)); // No funciona
```

### 2. **Orden de las fotos:**

```dart
// La primera foto del array SIEMPRE será la principal
List<File> fotos = [
  foto_principal,  // ← Esta será foto_1 (principal)
  foto_2,          // ← Esta será foto_2
  foto_3,          // ← Esta será foto_3
  foto_4,          // ← Esta será foto_4
];
```

### 3. **Máximo 4 fotos:**

```dart
// Limitar a 4 fotos
final fotosLimitadas = fotosSeleccionadas.take(4).toList();
```

---

## 📊 RESPONSE DEL BACKEND

```json
{
  "success": true,
  "message": "Se actualizaron 3 fotos exitosamente",
  "data": {
    "gallo_id": 228,
    "gallo_nombre": "Campeón",
    "fotos_subidas": 3,
    "foto_principal_url": "https://ik.imagekit.io/xxx/foto1.jpg",
    "fotos_detalle": [
      {
        "url": "https://ik.imagekit.io/xxx/foto1.jpg",
        "orden": 1,
        "es_principal": true,
        "file_id": "abc123",
        "descripcion": "Foto 1"
      },
      {
        "url": "https://ik.imagekit.io/xxx/foto2.jpg",
        "orden": 2,
        "es_principal": false,
        "file_id": "def456",
        "descripcion": "Foto 2"
      },
      {
        "url": "https://ik.imagekit.io/xxx/foto3.jpg",
        "orden": 3,
        "es_principal": false,
        "file_id": "ghi789",
        "descripcion": "Foto 3"
      }
    ],
    "total_fotos_almacenadas": 3
  }
}
```

---

## 🔄 INTEGRACIÓN CON FORMULARIO EXISTENTE

Si ya tienes un formulario de edición de gallo:

```dart
// En tu formulario de edición
Future<void> _actualizarGalloConFotos() async {
  // 1. Actualizar datos básicos del gallo
  await ApiService.actualizarGallo(
    galloId: widget.galloId,
    datos: _formData,
  );

  // 2. Si hay fotos nuevas, subirlas
  if (_fotosNuevas.isNotEmpty) {
    await ApiService.subirFotosMultiplesGallo(
      galloId: widget.galloId,
      fotos: _fotosNuevas,
    );
  }

  // 3. Refrescar datos
  Navigator.pop(context, true);
}
```

---

## 🎨 VARIANTE: Selector Individual

Si prefieres que el usuario seleccione una por una:

```dart
List<File?> _fotos = [null, null, null, null];

Future<void> _seleccionarFoto(int index) async {
  final XFile? image = await _picker.pickImage(
    source: ImageSource.gallery,
    maxWidth: 1920,
    maxHeight: 1920,
    imageQuality: 85,
  );

  if (image != null) {
    setState(() {
      _fotos[index] = File(image.path);
    });
  }
}

// UI
Column(
  children: [
    _buildFotoSelector(0, 'Foto Principal'),
    _buildFotoSelector(1, 'Foto 2'),
    _buildFotoSelector(2, 'Foto 3'),
    _buildFotoSelector(3, 'Foto 4'),
  ],
)

Widget _buildFotoSelector(int index, String label) {
  return GestureDetector(
    onTap: () => _seleccionarFoto(index),
    child: Container(
      height: 150,
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey),
        borderRadius: BorderRadius.circular(8),
      ),
      child: _fotos[index] != null
          ? Image.file(_fotos[index]!, fit: BoxFit.cover)
          : Center(child: Text(label)),
    ),
  );
}

// Al subir
final fotosValidas = _fotos.where((f) => f != null).cast<File>().toList();
await ApiService.subirFotosMultiplesGallo(
  galloId: widget.galloId,
  fotos: fotosValidas,
);
```

---

## 📝 RESUMEN

| Aspecto | Valor |
|---------|-------|
| **Endpoint** | `POST /gallos-con-pedigri/{id}/fotos-multiples` |
| **Nombres de campos** | `foto_1`, `foto_2`, `foto_3`, `foto_4` |
| **Máximo fotos** | 4 |
| **Foto principal** | Siempre la primera (`foto_1`) |
| **Content-Type** | `multipart/form-data` |
| **Autenticación** | Bearer Token en header |

---

**Documento creado:** 2025-11-16  
**Para:** Frontend Flutter  
**Estado:** ✅ Listo para implementar
