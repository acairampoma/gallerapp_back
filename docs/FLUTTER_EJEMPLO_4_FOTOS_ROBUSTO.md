# 📱 FLUTTER: Ejemplo Robusto de 4 Cajas de Fotos

## 🎯 ESCENARIO: Editar Gallo con 4 Cajas de Fotos

**Requisitos:**
- 3 cajas para "Agregar foto" (fotos adicionales)
- Respetar la selección de cada caja
- Subir masivamente las 4 fotos al backend
- Mostrar progreso de carga
- Manejar errores robustamente

---

## 📸 PASO 1: Widget de Caja de Foto

```dart
// lib/widgets/foto_picker_box.dart

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

class FotoPickerBox extends StatelessWidget {
  final File? imagen;
  final String label;
  final VoidCallback onTap;
  final VoidCallback? onDelete;
  final bool isLoading;

  const FotoPickerBox({
    Key? key,
    required this.imagen,
    required this.label,
    required this.onTap,
    this.onDelete,
    this.isLoading = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: isLoading ? null : onTap,
      child: Container(
        width: 100,
        height: 100,
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: imagen != null ? Colors.green : Colors.grey[400]!,
            width: 2,
          ),
        ),
        child: Stack(
          children: [
            // Imagen o placeholder
            if (imagen != null)
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Image.file(
                  imagen!,
                  width: 100,
                  height: 100,
                  fit: BoxFit.cover,
                ),
              )
            else
              Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.add_photo_alternate,
                      size: 32,
                      color: Colors.grey[600],
                    ),
                    SizedBox(height: 4),
                    Text(
                      label,
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.grey[600],
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),

            // Loading overlay
            if (isLoading)
              Container(
                decoration: BoxDecoration(
                  color: Colors.black54,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Center(
                  child: CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                  ),
                ),
              ),

            // Botón de eliminar
            if (imagen != null && !isLoading && onDelete != null)
              Positioned(
                top: 4,
                right: 4,
                child: GestureDetector(
                  onTap: onDelete,
                  child: Container(
                    padding: EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.close,
                      size: 16,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
```

---

## 📋 PASO 2: Screen de Edición con 4 Cajas

```dart
// lib/screens/edit_gallo_fotos_screen.dart

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import '../widgets/foto_picker_box.dart';

class EditGalloFotosScreen extends StatefulWidget {
  final int galloId;
  final String galloNombre;
  final String? fotoActualUrl;

  const EditGalloFotosScreen({
    Key? key,
    required this.galloId,
    required this.galloNombre,
    this.fotoActualUrl,
  }) : super(key: key);

  @override
  _EditGalloFotosScreenState createState() => _EditGalloFotosScreenState();
}

class _EditGalloFotosScreenState extends State<EditGalloFotosScreen> {
  final ImagePicker _picker = ImagePicker();
  
  // 🎯 ESTADO: 3 fotos adicionales (respetando cada caja)
  File? _fotoAdicional1;
  File? _fotoAdicional2;
  File? _fotoAdicional3;
  
  bool _isUploading = false;
  double _uploadProgress = 0.0;

  // 📸 Seleccionar foto para una caja específica
  Future<void> _seleccionarFoto(int cajaNumero) async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 85,
      );

      if (image != null) {
        setState(() {
          switch (cajaNumero) {
            case 1:
              _fotoAdicional1 = File(image.path);
              break;
            case 2:
              _fotoAdicional2 = File(image.path);
              break;
            case 3:
              _fotoAdicional3 = File(image.path);
              break;
          }
        });

        print('✅ Foto seleccionada para caja $cajaNumero: ${image.path}');
      }
    } catch (e) {
      print('❌ Error seleccionando foto: $e');
      _mostrarError('Error al seleccionar foto: $e');
    }
  }

  // 🗑️ Eliminar foto de una caja
  void _eliminarFoto(int cajaNumero) {
    setState(() {
      switch (cajaNumero) {
        case 1:
          _fotoAdicional1 = null;
          break;
        case 2:
          _fotoAdicional2 = null;
          break;
        case 3:
          _fotoAdicional3 = null;
          break;
      }
    });
  }

  // 🚀 SUBIR FOTOS AL BACKEND (MASIVO)
  Future<void> _subirFotos() async {
    // Validar que al menos una foto esté seleccionada
    if (_fotoAdicional1 == null && 
        _fotoAdicional2 == null && 
        _fotoAdicional3 == null) {
      _mostrarError('Debes seleccionar al menos una foto');
      return;
    }

    setState(() {
      _isUploading = true;
      _uploadProgress = 0.0;
    });

    try {
      print('📤 Iniciando subida de fotos...');
      print('📸 Caja 1: ${_fotoAdicional1 != null ? "✅" : "❌"}');
      print('📸 Caja 2: ${_fotoAdicional2 != null ? "✅" : "❌"}');
      print('📸 Caja 3: ${_fotoAdicional3 != null ? "✅" : "❌"}');

      // 🎯 LLAMADA AL API: Respetando cada caja
      final result = await ApiService.subirFotosMultiplesGallo(
        galloId: widget.galloId,
        foto1: _fotoAdicional1,  // Caja 1 → foto_1
        foto2: _fotoAdicional2,  // Caja 2 → foto_2
        foto3: _fotoAdicional3,  // Caja 3 → foto_3
        onProgress: (progress) {
          setState(() {
            _uploadProgress = progress;
          });
        },
      );

      print('✅ Respuesta del servidor: $result');

      // Mostrar resultado
      final data = result['data'];
      final fotosSubidas = data['fotos_subidas'] ?? 0;
      final mensaje = result['message'] ?? 'Fotos actualizadas';

      _mostrarExito('$mensaje\n$fotosSubidas fotos subidas correctamente');

      // Volver a la pantalla anterior
      await Future.delayed(Duration(seconds: 2));
      Navigator.pop(context, true); // true = fotos actualizadas

    } catch (e) {
      print('❌ Error subiendo fotos: $e');
      _mostrarError('Error al subir fotos: $e');
    } finally {
      setState(() {
        _isUploading = false;
        _uploadProgress = 0.0;
      });
    }
  }

  void _mostrarExito(String mensaje) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(mensaje),
        backgroundColor: Colors.green,
        duration: Duration(seconds: 3),
      ),
    );
  }

  void _mostrarError(String mensaje) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(mensaje),
        backgroundColor: Colors.red,
        duration: Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('📸 Editar Fotos'),
        subtitle: Text(widget.galloNombre),
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 📷 FOTO ACTUAL (Solo visualización)
            if (widget.fotoActualUrl != null) ...[
              Text(
                'Foto Principal Actual',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 8),
              Container(
                width: double.infinity,
                height: 200,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.blue, width: 2),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(10),
                  child: Image.network(
                    widget.fotoActualUrl!,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return Center(
                        child: Icon(Icons.error, size: 48, color: Colors.red),
                      );
                    },
                  ),
                ),
              ),
              SizedBox(height: 24),
            ],

            // 📸 TÍTULO: FOTOS ADICIONALES
            Text(
              'Agregar Fotos Adicionales',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Selecciona hasta 3 fotos adicionales',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
            ),
            SizedBox(height: 16),

            // 🎯 3 CAJAS DE FOTOS (RESPETANDO CADA UNA)
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                // CAJA 1
                FotoPickerBox(
                  imagen: _fotoAdicional1,
                  label: 'Foto 1',
                  isLoading: _isUploading,
                  onTap: () => _seleccionarFoto(1),
                  onDelete: () => _eliminarFoto(1),
                ),

                // CAJA 2
                FotoPickerBox(
                  imagen: _fotoAdicional2,
                  label: 'Foto 2',
                  isLoading: _isUploading,
                  onTap: () => _seleccionarFoto(2),
                  onDelete: () => _eliminarFoto(2),
                ),

                // CAJA 3
                FotoPickerBox(
                  imagen: _fotoAdicional3,
                  label: 'Foto 3',
                  isLoading: _isUploading,
                  onTap: () => _seleccionarFoto(3),
                  onDelete: () => _eliminarFoto(3),
                ),
              ],
            ),

            SizedBox(height: 24),

            // 📊 PROGRESO DE CARGA
            if (_isUploading) ...[
              LinearProgressIndicator(
                value: _uploadProgress,
                backgroundColor: Colors.grey[300],
                valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
              ),
              SizedBox(height: 8),
              Text(
                'Subiendo fotos... ${(_uploadProgress * 100).toInt()}%',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                ),
              ),
              SizedBox(height: 24),
            ],

            // 🚀 BOTÓN DE SUBIR
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton.icon(
                onPressed: _isUploading ? null : _subirFotos,
                icon: Icon(_isUploading ? Icons.hourglass_empty : Icons.cloud_upload),
                label: Text(
                  _isUploading ? 'Subiendo...' : 'Subir Fotos',
                  style: TextStyle(fontSize: 16),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),

            SizedBox(height: 16),

            // ℹ️ INFORMACIÓN
            Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blue[200]!),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.blue),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Las fotos se subirán respetando la caja seleccionada. '
                      'Puedes subir 1, 2 o 3 fotos.',
                      style: TextStyle(fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 🔌 PASO 3: Servicio API (ApiService)

```dart
// lib/services/api_service.dart

import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'http://tu-servidor.com';

  /// 📸 SUBIR MÚLTIPLES FOTOS A UN GALLO (RESPETANDO CADA CAJA)
  static Future<Map<String, dynamic>> subirFotosMultiplesGallo({
    required int galloId,
    File? foto1,  // Caja 1
    File? foto2,  // Caja 2
    File? foto3,  // Caja 3
    Function(double)? onProgress,
  }) async {
    try {
      // Validar que al menos una foto esté presente
      if (foto1 == null && foto2 == null && foto3 == null) {
        throw Exception('Debes seleccionar al menos una foto');
      }

      print('📤 Preparando subida de fotos para gallo $galloId...');

      // Obtener token de autenticación
      final token = await _getAuthToken();
      if (token == null) {
        throw Exception('No hay sesión activa');
      }

      // Crear request multipart
      final uri = Uri.parse('$baseUrl/api/v1/gallos-con-pedigri/$galloId/fotos-multiples');
      final request = http.MultipartRequest('POST', uri);

      // Agregar headers
      request.headers['Authorization'] = 'Bearer $token';

      // 🎯 AGREGAR FOTOS RESPETANDO CADA CAJA
      if (foto1 != null) {
        print('📸 Agregando foto_1: ${foto1.path}');
        final multipartFile = await http.MultipartFile.fromPath(
          'foto_1',  // ← IMPORTANTE: nombre exacto que espera el backend
          foto1.path,
        );
        request.files.add(multipartFile);
      }

      if (foto2 != null) {
        print('📸 Agregando foto_2: ${foto2.path}');
        final multipartFile = await http.MultipartFile.fromPath(
          'foto_2',  // ← IMPORTANTE: nombre exacto
          foto2.path,
        );
        request.files.add(multipartFile);
      }

      if (foto3 != null) {
        print('📸 Agregando foto_3: ${foto3.path}');
        final multipartFile = await http.MultipartFile.fromPath(
          'foto_3',  // ← IMPORTANTE: nombre exacto
          foto3.path,
        );
        request.files.add(multipartFile);
      }

      print('📤 Enviando ${request.files.length} fotos al servidor...');

      // Enviar request con progreso
      final streamedResponse = await request.send();

      // Simular progreso (opcional)
      if (onProgress != null) {
        for (double i = 0.0; i <= 1.0; i += 0.1) {
          await Future.delayed(Duration(milliseconds: 100));
          onProgress(i);
        }
      }

      // Obtener response
      final response = await http.Response.fromStream(streamedResponse);

      print('📡 Status code: ${response.statusCode}');
      print('📡 Response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        print('✅ Fotos subidas exitosamente');
        return data;
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Error desconocido');
      }

    } catch (e) {
      print('💥 Error en subirFotosMultiplesGallo: $e');
      rethrow;
    }
  }

  /// 🔑 Obtener token de autenticación
  static Future<String?> _getAuthToken() async {
    // Implementar según tu sistema de autenticación
    // Ejemplo con SharedPreferences:
    // final prefs = await SharedPreferences.getInstance();
    // return prefs.getString('auth_token');
    
    return 'tu_token_aqui'; // Placeholder
  }
}
```

---

## 🎯 PASO 4: Uso desde otra pantalla

```dart
// Ejemplo: Desde la pantalla de detalles del gallo

ElevatedButton(
  onPressed: () async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => EditGalloFotosScreen(
          galloId: gallo.id,
          galloNombre: gallo.nombre,
          fotoActualUrl: gallo.fotoPrincipalUrl,
        ),
      ),
    );

    // Si result == true, las fotos se actualizaron
    if (result == true) {
      print('✅ Fotos actualizadas, recargar datos...');
      // Recargar datos del gallo
      _cargarDatosGallo();
    }
  },
  child: Text('📸 Editar Fotos'),
)
```

---

## 📊 FLUJO COMPLETO

### 1. Usuario abre pantalla de edición
```
EditGalloFotosScreen
├── Muestra foto principal actual (solo visualización)
└── Muestra 3 cajas vacías para fotos adicionales
```

### 2. Usuario selecciona fotos
```
Caja 1: [Seleccionar] → foto1.jpg ✅
Caja 2: [Seleccionar] → foto2.jpg ✅
Caja 3: [Vacía] ❌
```

### 3. Usuario presiona "Subir Fotos"
```dart
ApiService.subirFotosMultiplesGallo(
  galloId: 123,
  foto1: File('/path/foto1.jpg'),  // Caja 1
  foto2: File('/path/foto2.jpg'),  // Caja 2
  foto3: null,                      // Caja 3 vacía
)
```

### 4. Backend recibe request
```python
# Backend recibe:
foto_1 = File(foto1.jpg)  # ✅
foto_2 = File(foto2.jpg)  # ✅
foto_3 = None             # ❌ (no se envió)
foto_4 = None             # ❌ (no se envió)

# Backend procesa:
for i, foto in enumerate([foto_1, foto_2, foto_3, foto_4]):
    if foto:
        # Subir foto con orden correcto
        foto_obj = {"orden": i + 1, ...}
```

### 5. Backend responde
```json
{
  "success": true,
  "message": "Se actualizaron 2 fotos exitosamente",
  "data": {
    "fotos_subidas": 2,
    "fotos_detalle": [
      {"url": "...", "orden": 1, "es_principal": false},
      {"url": "...", "orden": 2, "es_principal": false}
    ]
  }
}
```

---

## ✅ VENTAJAS DE ESTE ENFOQUE

1. **Respeta cada caja:** Foto 1 → foto_1, Foto 2 → foto_2, etc.
2. **Robusto:** Maneja errores, progreso, validaciones
3. **Flexible:** Puedes subir 1, 2 o 3 fotos
4. **Visual:** Usuario ve exactamente qué foto va en cada caja
5. **Feedback:** Progreso de carga, mensajes de éxito/error

---

## 🚨 PUNTOS IMPORTANTES

### En Flutter:
```dart
// ✅ CORRECTO: Nombres exactos que espera el backend
'foto_1'  // Caja 1
'foto_2'  // Caja 2
'foto_3'  // Caja 3

// ❌ INCORRECTO:
'foto1'   // Sin guión bajo
'fotos[]' // Array
'imagen_1' // Nombre diferente
```

### En Backend:
```python
# ✅ CORRECTO: Parámetros con nombres exactos
foto_1: Optional[UploadFile] = File(None)
foto_2: Optional[UploadFile] = File(None)
foto_3: Optional[UploadFile] = File(None)

# El backend respeta el orden:
# foto_1 → orden 1
# foto_2 → orden 2
# foto_3 → orden 3
```

---

## 🎯 RESULTADO FINAL

**Usuario ve:**
```
┌─────────────────────────────────┐
│  📷 Foto Principal Actual       │
│  [Imagen de Cloudinary]         │
└─────────────────────────────────┘

Agregar Fotos Adicionales:

┌────────┐  ┌────────┐  ┌────────┐
│ Foto 1 │  │ Foto 2 │  │ Foto 3 │
│   ✅   │  │   ✅   │  │   ❌   │
└────────┘  └────────┘  └────────┘

        [Subir Fotos]
```

**Backend recibe y procesa:**
- Detecta si foto principal es Cloudinary → ✅ Permite actualización
- Sube foto_1 y foto_2 a ImageKit
- Guarda en BD con orden correcto
- Retorna URLs de ImageKit

**¡LISTO CUMPA! 🎉**

---

**Documento creado:** 2025-11-16
**Probado:** ✅ Backend corregido
**Estado:** Listo para implementar en Flutter
