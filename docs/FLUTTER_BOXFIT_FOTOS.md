# 📸 Flutter: Ajustar Fotos en Cajas - BoxFit

## 🎯 Problema Resuelto

Las fotos se salían de las cajas y se veían deformadas en el formulario de gallos.

## 🔧 Solución: Propiedad `BoxFit`

### ¿Qué es BoxFit?

`BoxFit` es una propiedad de Flutter que controla **cómo se ajusta una imagen dentro de su contenedor**.

### Tipos de BoxFit:

#### 1. `BoxFit.contain` ✅ (RECOMENDADO)
```dart
Image.file(
  foto,
  fit: BoxFit.contain, // ← La foto se ajusta DENTRO de la caja
)
```

**Resultado:**
- ✅ La foto COMPLETA se ve dentro de la caja
- ✅ NO se corta ninguna parte
- ✅ Puede quedar espacio vacío arriba/abajo o a los lados
- ✅ Mantiene proporciones originales

**Ejemplo visual:**
```
┌─────────────────┐
│                 │
│   ┌─────────┐   │  ← Foto completa dentro
│   │  FOTO   │   │
│   └─────────┘   │
│                 │
└─────────────────┘
```

---

#### 2. `BoxFit.cover` ❌ (Problema anterior)
```dart
Image.file(
  foto,
  fit: BoxFit.cover, // ← La foto LLENA toda la caja
)
```

**Resultado:**
- ❌ La foto se CORTA para llenar toda la caja
- ❌ Puede perder partes importantes de la imagen
- ✅ No hay espacios vacíos
- ✅ Mantiene proporciones pero corta

**Ejemplo visual:**
```
┌─────────────────┐
│█████████████████│  ← Foto cortada
│█████FOTO████████│     (se pierde arriba/abajo)
│█████████████████│
└─────────────────┘
```

---

#### 3. `BoxFit.fill` ⚠️ (Deforma la imagen)
```dart
Image.file(
  foto,
  fit: BoxFit.fill, // ← Estira la foto
)
```

**Resultado:**
- ❌ La foto se DEFORMA para llenar la caja
- ❌ NO mantiene proporciones
- ✅ No hay espacios vacíos
- ❌ Imagen distorsionada

**Ejemplo visual:**
```
┌─────────────────┐
│█████████████████│  ← Foto estirada
│███FOTO GORDA████│     (deformada)
│█████████████████│
└─────────────────┘
```

---

#### 4. Otros BoxFit:

- `BoxFit.fitWidth` - Ajusta al ancho
- `BoxFit.fitHeight` - Ajusta a la altura
- `BoxFit.none` - Tamaño original (puede salirse)
- `BoxFit.scaleDown` - Reduce si es muy grande

---

## 🔥 Cambios Aplicados

### ANTES (Problema):

```dart
// Foto principal
ClipRRect(
  borderRadius: BorderRadius.circular(14),
  child: _buildImageForDisplay(_selectedImages[0], BoxFit.cover), // ❌ Se cortaba
),

// Fotos adicionales
ClipRRect(
  borderRadius: BorderRadius.circular(8),
  child: _buildImageForDisplay(_selectedImages[photoIndex], BoxFit.cover), // ❌ Se cortaban
),
```

**Problemas:**
- Las fotos se cortaban
- Se perdían partes importantes
- No se veía la foto completa

---

### DESPUÉS (Solución):

```dart
// Foto principal
Container(
  height: 200,
  width: double.infinity,
  decoration: BoxDecoration(
    borderRadius: BorderRadius.circular(14),
    border: Border.all(color: Colors.grey[300]!),
    color: Colors.grey[100], // ✅ Fondo gris para ver el ajuste
  ),
  child: Stack(
    children: [
      ClipRRect(
        borderRadius: BorderRadius.circular(14),
        child: Container(
          width: double.infinity,
          height: double.infinity,
          child: _buildImageForDisplay(_selectedImages[0], BoxFit.contain), // ✅ Se ajusta dentro
        ),
      ),
      // ... badges y botones
    ],
  ),
)

// Fotos adicionales
ClipRRect(
  borderRadius: BorderRadius.circular(8),
  child: Container(
    width: double.infinity,
    height: double.infinity,
    color: Colors.grey[100], // ✅ Fondo gris
    child: _buildImageForDisplay(_selectedImages[photoIndex], BoxFit.contain), // ✅ Se ajusta dentro
  ),
),
```

**Mejoras:**
- ✅ Foto completa visible
- ✅ No se corta nada
- ✅ Fondo gris para ver el espacio
- ✅ Se ve hermosa dentro de la caja

---

## 📐 Dimensiones de las Cajas

### Foto Principal:
```dart
Container(
  height: 200,        // ← Alto fijo: 200 píxeles
  width: double.infinity, // ← Ancho: todo el disponible
)
```

### Fotos Adicionales:
```dart
GridView.builder(
  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
    crossAxisCount: 3,      // ← 3 columnas
    crossAxisSpacing: 8,    // ← Espacio horizontal: 8px
    mainAxisSpacing: 8,     // ← Espacio vertical: 8px
    childAspectRatio: 1.0,  // ← Cuadrado (1:1)
  ),
)
```

**Resultado:**
- Foto principal: Rectángulo horizontal (ancho x 200px)
- Fotos adicionales: Cuadrados pequeños (3 en fila)

---

## 🎨 Fondo Gris

### ¿Por qué agregamos fondo gris?

```dart
color: Colors.grey[100], // ← Fondo gris claro
```

**Razones:**
1. ✅ Se ve el espacio vacío cuando la foto no llena toda la caja
2. ✅ Contraste visual agradable
3. ✅ Indica que hay una foto cargada
4. ✅ Mejor experiencia de usuario

**Ejemplo:**

```
┌─────────────────┐
│░░░░░░░░░░░░░░░░░│  ← Fondo gris (espacios vacíos)
│░░┌───────────┐░░│
│░░│   FOTO    │░░│  ← Foto centrada
│░░└───────────┘░░│
│░░░░░░░░░░░░░░░░░│
└─────────────────┘
```

---

## 🔍 Función Helper Mejorada

```dart
// 🖼️ HELPER: Construir widget de imagen según tipo (File o XFile)
// BoxFit.contain = La imagen se ajusta dentro del contenedor sin cortarse
// BoxFit.cover = La imagen llena todo el contenedor (puede cortarse)
Widget _buildImageForDisplay(dynamic image, BoxFit fit) {
  if (image is XFile) {
    return Image.network(
      image.path,
      fit: fit,
      width: double.infinity,
      height: double.infinity,
      errorBuilder: (context, error, stackTrace) {
        return Center(
          child: Icon(Icons.broken_image, color: Colors.grey, size: 40),
        );
      },
    );
  } else {
    return Image.file(
      image as File,
      fit: fit,
      width: double.infinity,
      height: double.infinity,
      errorBuilder: (context, error, stackTrace) {
        return Center(
          child: Icon(Icons.broken_image, color: Colors.grey, size: 40),
        );
      },
    );
  }
}
```

**Mejoras:**
- ✅ Comentarios explicativos
- ✅ `errorBuilder` para manejar errores
- ✅ Icono de imagen rota si falla la carga
- ✅ Funciona con File (móvil) y XFile (web)

---

## 📱 Resultado Visual

### Foto Principal:
```
┌─────────────────────────────────┐
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│░░░░┌───────────────────────┐░░░░│
│░░░░│                       │░░░░│
│░░░░│      FOTO GALLO       │░░░░│  ← Foto completa
│░░░░│      (Principal)      │░░░░│     sin cortar
│░░░░│                       │░░░░│
│░░░░└───────────────────────┘░░░░│
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
└─────────────────────────────────┘
   [Principal] [X]  ← Badges
```

### Fotos Adicionales:
```
┌─────────┐  ┌─────────┐  ┌─────────┐
│░░░░░░░░░│  │░░░░░░░░░│  │░░░░░░░░░│
│░┌─────┐░│  │░┌─────┐░│  │░░░░░░░░░│
│░│FOTO │░│  │░│FOTO │░│  │░░ [+] ░░│  ← Agregar más
│░│  2  │░│  │░│  3  │░│  │░Agregar░│
│░└─────┘░│  │░└─────┘░│  │░░░░░░░░░│
│░░░░░░░░░│  │░░░░░░░░░│  │░░░░░░░░░│
└─────────┘  └─────────┘  └─────────┘
```

---

## 🎯 Resumen de Propiedades

| Propiedad | Valor | Propósito |
|-----------|-------|-----------|
| `fit` | `BoxFit.contain` | Ajustar foto dentro sin cortar |
| `color` | `Colors.grey[100]` | Fondo gris para espacios vacíos |
| `width` | `double.infinity` | Usar todo el ancho disponible |
| `height` | `double.infinity` | Usar toda la altura disponible |
| `borderRadius` | `BorderRadius.circular(14)` | Esquinas redondeadas |
| `errorBuilder` | `Icon(Icons.broken_image)` | Mostrar icono si falla |

---

## ✅ Checklist de Verificación

Después de aplicar los cambios, verifica:

- [ ] Foto principal se ve completa (no cortada)
- [ ] Fotos adicionales se ven completas
- [ ] Hay fondo gris en espacios vacíos
- [ ] Las fotos mantienen sus proporciones
- [ ] No hay deformación
- [ ] Esquinas redondeadas funcionan
- [ ] Botones de eliminar visibles
- [ ] Badge "Principal" visible

---

## 🚀 Cómo Probar

1. **Abrir app Flutter**
2. **Ir a formulario de crear/editar gallo**
3. **Subir foto principal** (cualquier tamaño)
4. **Verificar:**
   - ✅ Se ve completa dentro de la caja
   - ✅ No se corta
   - ✅ Fondo gris en espacios vacíos
5. **Subir fotos adicionales**
6. **Verificar:**
   - ✅ Se ven completas en las cajas pequeñas
   - ✅ Mantienen proporciones

---

## 📝 Notas Técnicas

### ¿Cuándo usar cada BoxFit?

| Caso de Uso | BoxFit Recomendado |
|-------------|-------------------|
| Fotos de gallos (importante ver completo) | `BoxFit.contain` |
| Avatares de perfil (circular) | `BoxFit.cover` |
| Banners (llenar espacio) | `BoxFit.cover` |
| Logos (mantener proporciones) | `BoxFit.contain` |
| Fondos de pantalla | `BoxFit.cover` |
| Galerías de fotos | `BoxFit.contain` |

### Combinación con ClipRRect

```dart
ClipRRect(
  borderRadius: BorderRadius.circular(14), // ← Esquinas redondeadas
  child: Container(
    child: Image.file(foto, fit: BoxFit.contain),
  ),
)
```

**Importante:**
- `ClipRRect` corta las esquinas
- `Container` con `color` da el fondo
- `Image.file` con `BoxFit.contain` ajusta la foto

---

**Documento creado:** 2025-11-16  
**Archivo modificado:** `add_gallo_multistep_screen.dart`  
**Propiedad clave:** `BoxFit.contain`  
**Estado:** ✅ Implementado y Documentado
