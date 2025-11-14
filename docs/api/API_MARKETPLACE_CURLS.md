# 🛒 **MARKETPLACE API - CURL TEST CASES**

## **📋 REQUISITOS PREVIOS**

1. **Ejecutar el script de datos de prueba:**
   ```bash
   # Ejecutar en PostgreSQL:
   \i API_MARKETPLACE_TEST_DATA.sql
   ```

2. **Variables de entorno para testing:**
   ```bash
   export BASE_URL="http://localhost:8000/api/v1"
   export AUTH_TOKEN="Bearer YOUR_JWT_TOKEN_HERE"

   # Para usuarios específicos (después del login):
   export USER_27_TOKEN="Bearer JWT_FOR_USER_27"
   export USER_62_TOKEN="Bearer JWT_FOR_USER_62"
   export USER_68_TOKEN="Bearer JWT_FOR_USER_68"
   export USER_65_TOKEN="Bearer JWT_FOR_USER_65"
   ```

---

## 🔐 **1. AUTHENTICATION - LOGIN PRIMERO**

### **Login Usuario 27 (Premium con 3 publicaciones)**
```bash
curl -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario27@test.com",
    "password": "test123"
  }'
```

### **Login Usuario 62 (Premium con 2 publicaciones)**
```bash
curl -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario62@test.com",
    "password": "test123"
  }'
```

---

## 📊 **2. SUSCRIPCIONES - VERIFICAR LÍMITES MARKETPLACE**

### **Obtener límites actuales del usuario**
```bash
curl -X GET "$BASE_URL/suscripciones/limites" \
  -H "Authorization: $USER_27_TOKEN" \
  -H "Content-Type: application/json"
```

**Respuesta esperada:**
```json
{
  "user_id": 27,
  "plan_actual": "premium",
  "suscripcion_activa": true,
  "gallos": {
    "tipo": "gallos",
    "limite": 50,
    "usado": 3,
    "disponible": 47,
    "porcentaje_uso": 6.0
  },
  "marketplace_publicaciones": {
    "tipo": "marketplace_publicaciones",
    "limite": 5,
    "usado": 3,
    "disponible": 2,
    "porcentaje_uso": 60.0
  }
}
```

### **Validar límite específico de marketplace**
```bash
curl -X POST "$BASE_URL/suscripciones/validar-limite" \
  -H "Authorization: $USER_27_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recurso_tipo": "marketplace_publicaciones"
  }'
```

### **Obtener suscripción actual (incluye marketplace)**
```bash
curl -X GET "$BASE_URL/suscripciones/actual" \
  -H "Authorization: $USER_27_TOKEN"
```

---

## 🐓 **3. GALLOS - GESTIÓN DE FOTOS MÚLTIPLES**

### **Subir 4 fotos a un gallo**
```bash
curl -X POST "$BASE_URL/gallos-con-pedigri/213/fotos-multiples" \
  -H "Authorization: $USER_27_TOKEN" \
  -F "foto_1=@/path/to/gallo1.jpg" \
  -F "foto_2=@/path/to/gallo2.jpg" \
  -F "foto_3=@/path/to/gallo3.jpg" \
  -F "foto_4=@/path/to/gallo4.jpg"
```

### **Obtener fotos de un gallo**
```bash
curl -X GET "$BASE_URL/gallos-con-pedigri/213/fotos" \
  -H "Authorization: $USER_27_TOKEN"
```

**Respuesta esperada:**
```json
{
  "gallo_id": 213,
  "total_fotos": 4,
  "fotos": [
    {
      "url": "https://res.cloudinary.com/demo/image/upload/v123/foto1.jpg",
      "public_id": "foto1",
      "order": 1
    }
  ]
}
```

---

## 🛒 **4. MARKETPLACE - OPERACIONES PRINCIPALES**

### **A. LISTAR PUBLICACIONES PÚBLICAS (CON FILTROS)**

#### **Listado básico - todas las publicaciones**
```bash
curl -X GET "$BASE_URL/marketplace/publicaciones" \
  -H "Authorization: $USER_68_TOKEN"
```

#### **Filtro por rango de precio**
```bash
curl -X GET "$BASE_URL/marketplace/publicaciones?precio_min=300&precio_max=500" \
  -H "Authorization: $USER_68_TOKEN"
```

#### **Filtro por estado**
```bash
curl -X GET "$BASE_URL/marketplace/publicaciones?estado=venta" \
  -H "Authorization: $USER_68_TOKEN"
```

#### **Filtro combinado con paginación**
```bash
curl -X GET "$BASE_URL/marketplace/publicaciones?precio_min=250&precio_max=450&estado=venta&skip=0&limit=10&ordenar_por=precio_asc" \
  -H "Authorization: $USER_68_TOKEN"
```

#### **Búsqueda por texto**
```bash
curl -X GET "$BASE_URL/marketplace/publicaciones?buscar=vraem" \
  -H "Authorization: $USER_68_TOKEN"
```

**Respuesta esperada:**
```json
{
  "publicaciones": [
    {
      "id": 1,
      "precio": 450.0,
      "estado": "venta",
      "icono_ejemplo": "🐓",
      "fecha_publicacion": "2025-09-24T21:30:00",
      "gallo_info": {
        "id": 213,
        "nombre": "Vraem",
        "codigo_identificacion": "356",
        "foto_principal_url": "https://res.cloudinary.com/demo/image/upload/gallo1.jpg",
        "fotos_adicionales": [...],
        "raza_nombre": "Navajero",
        "peso_aproximado": 2.5,
        "color_plumaje": "Rojizo"
      },
      "vendedor_info": {
        "user_id": 27,
        "nombre": "Juan Vendedor",
        "telefono": "+51987654321",
        "ubicacion": "Lima, Perú"
      },
      "es_favorito": false,
      "total_favoritos": 2
    }
  ],
  "total": 7,
  "skip": 0,
  "limit": 20,
  "has_next": false
}
```

### **B. PUBLICACIONES DEL USUARIO**

#### **Mis publicaciones**
```bash
curl -X GET "$BASE_URL/marketplace/mis-publicaciones" \
  -H "Authorization: $USER_27_TOKEN"
```

#### **Mis publicaciones con filtros**
```bash
curl -X GET "$BASE_URL/marketplace/mis-publicaciones?estado=venta" \
  -H "Authorization: $USER_27_TOKEN"
```

### **C. CREAR PUBLICACIÓN**

#### **Crear publicación exitosa**
```bash
curl -X POST "$BASE_URL/marketplace/publicaciones" \
  -H "Authorization: $USER_62_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gallo_id": 207,
    "precio": 375.50,
    "estado": "venta",
    "icono_ejemplo": "🔥"
  }'
```

#### **Crear publicación - límite excedido**
```bash
# Usuario 27 ya tiene 3/5 publicaciones, crear 3 más para probar límite
curl -X POST "$BASE_URL/marketplace/publicaciones" \
  -H "Authorization: $USER_27_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gallo_id": 999,
    "precio": 500.00,
    "estado": "venta"
  }'
```

**Respuesta esperada (límite excedido):**
```json
{
  "detail": "Límite de publicaciones marketplace alcanzado (5/5). Upgrade a plan profesional para más publicaciones."
}
```

### **D. ACTUALIZAR PUBLICACIÓN**

#### **Actualizar precio y estado**
```bash
curl -X PUT "$BASE_URL/marketplace/publicaciones/1" \
  -H "Authorization: $USER_27_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "precio": 480.00,
    "estado": "pausado"
  }'
```

#### **Actualizar solo precio**
```bash
curl -X PUT "$BASE_URL/marketplace/publicaciones/2" \
  -H "Authorization: $USER_27_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "precio": 400.00
  }'
```

### **E. ELIMINAR PUBLICACIÓN**

#### **Eliminar publicación propia**
```bash
curl -X DELETE "$BASE_URL/marketplace/publicaciones/3" \
  -H "Authorization: $USER_27_TOKEN"
```

#### **Intentar eliminar publicación ajena (debe fallar)**
```bash
curl -X DELETE "$BASE_URL/marketplace/publicaciones/1" \
  -H "Authorization: $USER_62_TOKEN"
```

---

## ❤️ **5. MARKETPLACE - SISTEMA DE FAVORITOS**

### **A. MARCAR/DESMARCAR FAVORITO**

#### **Marcar como favorito**
```bash
curl -X POST "$BASE_URL/marketplace/publicaciones/1/favorito" \
  -H "Authorization: $USER_68_TOKEN"
```

#### **Desmarcar favorito (mismo endpoint)**
```bash
curl -X POST "$BASE_URL/marketplace/publicaciones/1/favorito" \
  -H "Authorization: $USER_68_TOKEN"
```

**Respuesta esperada:**
```json
{
  "mensaje": "Publicación agregada a favoritos",
  "publicacion_id": 1,
  "es_favorito": true,
  "total_favoritos": 3
}
```

### **B. LISTAR FAVORITOS**

#### **Mis favoritos**
```bash
curl -X GET "$BASE_URL/marketplace/favoritos" \
  -H "Authorization: $USER_68_TOKEN"
```

#### **Mis favoritos paginados**
```bash
curl -X GET "$BASE_URL/marketplace/favoritos?skip=0&limit=5" \
  -H "Authorization: $USER_68_TOKEN"
```

**Respuesta esperada:**
```json
{
  "favoritos": [
    {
      "id": 1,
      "user_id": 68,
      "publicacion_id": 1,
      "created_at": "2025-09-24T12:00:00",
      "publicacion_info": {
        "precio": 450.0,
        "estado": "venta",
        "gallo_nombre": "Vraem",
        "gallo_codigo": "356",
        "vendedor_email": "usuario27@test.com"
      }
    }
  ],
  "total": 3,
  "skip": 0,
  "limit": 20
}
```

---

## 📊 **6. MARKETPLACE - LÍMITES Y ESTADÍSTICAS**

### **A. OBTENER LÍMITES MARKETPLACE**

#### **Límites del usuario actual**
```bash
curl -X GET "$BASE_URL/marketplace/limites" \
  -H "Authorization: $USER_27_TOKEN"
```

**Respuesta esperada:**
```json
{
  "publicaciones_permitidas": 5,
  "publicaciones_activas": 3,
  "publicaciones_disponibles": 2,
  "puede_publicar": true,
  "plan_codigo": "premium",
  "plan_nombre": "Plan Premium"
}
```

#### **Usuario sin límites (plan gratuito)**
```bash
curl -X GET "$BASE_URL/marketplace/limites" \
  -H "Authorization: $USER_GRATUITO_TOKEN"
```

**Respuesta esperada:**
```json
{
  "publicaciones_permitidas": 0,
  "publicaciones_activas": 0,
  "publicaciones_disponibles": 0,
  "puede_publicar": false,
  "plan_codigo": "gratuito",
  "plan_nombre": "Plan Gratuito"
}
```

### **B. ESTADÍSTICAS GENERALES**

#### **Stats del marketplace**
```bash
curl -X GET "$BASE_URL/marketplace/stats" \
  -H "Authorization: $USER_27_TOKEN"
```

**Respuesta esperada:**
```json
{
  "total_publicaciones": 8,
  "publicaciones_activas": 7,
  "publicaciones_vendidas": 1,
  "publicaciones_pausadas": 1,
  "precio_promedio": 375.50,
  "precio_minimo": 275.50,
  "precio_maximo": 520.75
}
```

---

## 🧪 **7. CASOS DE PRUEBA - VALIDACIONES**

### **A. VALIDACIÓN DE LÍMITES**

#### **Usuario gratuito intentando publicar**
```bash
# Cambiar usuario a plan gratuito primero
curl -X POST "$BASE_URL/marketplace/publicaciones" \
  -H "Authorization: $USER_GRATUITO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gallo_id": 205,
    "precio": 300.00
  }'
```

**Error esperado:**
```json
{
  "detail": "El plan gratuito no permite publicaciones en marketplace. Upgrade a plan básico para comenzar a vender."
}
```

### **B. VALIDACIÓN DE PROPIEDAD**

#### **Intentar actualizar publicación ajena**
```bash
curl -X PUT "$BASE_URL/marketplace/publicaciones/1" \
  -H "Authorization: $USER_62_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "precio": 999.99
  }'
```

**Error esperado:**
```json
{
  "detail": "Publicación no encontrada o no autorizada"
}
```

### **C. VALIDACIÓN DE GALLO**

#### **Publicar gallo que no existe**
```bash
curl -X POST "$BASE_URL/marketplace/publicaciones" \
  -H "Authorization: $USER_27_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gallo_id": 99999,
    "precio": 400.00
  }'
```

#### **Publicar gallo de otro usuario**
```bash
curl -X POST "$BASE_URL/marketplace/publicaciones" \
  -H "Authorization: $USER_27_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gallo_id": 212,
    "precio": 400.00
  }'
```

### **D. VALIDACIÓN DE PRECIOS**

#### **Precio inválido (negativo)**
```bash
curl -X POST "$BASE_URL/marketplace/publicaciones" \
  -H "Authorization: $USER_27_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gallo_id": 213,
    "precio": -100.00
  }'
```

#### **Precio demasiado alto**
```bash
curl -X POST "$BASE_URL/marketplace/publicaciones" \
  -H "Authorization: $USER_27_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gallo_id": 213,
    "precio": 1000000.00
  }'
```

---

## 🔄 **8. CASOS DE PRUEBA - WORKFLOWS COMPLETOS**

### **A. WORKFLOW: USUARIO COMPRANDO**

```bash
# 1. Usuario busca gallos por precio
curl -X GET "$BASE_URL/marketplace/publicaciones?precio_min=300&precio_max=500" \
  -H "Authorization: $USER_68_TOKEN"

# 2. Marca varios como favoritos
curl -X POST "$BASE_URL/marketplace/publicaciones/1/favorito" \
  -H "Authorization: $USER_68_TOKEN"

curl -X POST "$BASE_URL/marketplace/publicaciones/4/favorito" \
  -H "Authorization: $USER_68_TOKEN"

# 3. Ve sus favoritos
curl -X GET "$BASE_URL/marketplace/favoritos" \
  -H "Authorization: $USER_68_TOKEN"

# 4. Contacta al vendedor (info en respuesta)
```

### **B. WORKFLOW: USUARIO VENDIENDO**

```bash
# 1. Verifica sus límites
curl -X GET "$BASE_URL/marketplace/limites" \
  -H "Authorization: $USER_62_TOKEN"

# 2. Crea nueva publicación
curl -X POST "$BASE_URL/marketplace/publicaciones" \
  -H "Authorization: $USER_62_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gallo_id": 207,
    "precio": 350.00,
    "icono_ejemplo": "🎯"
  }'

# 3. Ve todas sus publicaciones
curl -X GET "$BASE_URL/marketplace/mis-publicaciones" \
  -H "Authorization: $USER_62_TOKEN"

# 4. Pausa una publicación
curl -X PUT "$BASE_URL/marketplace/publicaciones/5" \
  -H "Authorization: $USER_62_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "pausado"
  }'

# 5. Marca como vendida
curl -X PUT "$BASE_URL/marketplace/publicaciones/5" \
  -H "Authorization: $USER_62_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "estado": "vendido"
  }'
```

---

## 📈 **9. MONITOREO Y PERFORMANCE**

### **A. PRUEBAS DE CARGA**

#### **Test de carga - múltiples requests**
```bash
# Usar ab o wrk para load testing
ab -n 100 -c 10 -H "Authorization: $USER_27_TOKEN" \
  "$BASE_URL/marketplace/publicaciones"
```

### **B. PRUEBAS DE FILTROS COMPLEJOS**

#### **Query compleja con múltiples filtros**
```bash
curl -X GET "$BASE_URL/marketplace/publicaciones?precio_min=250&precio_max=600&estado=venta&ordenar_por=fecha_desc&skip=0&limit=5&incluir_vendidas=false" \
  -H "Authorization: $USER_68_TOKEN"
```

---

## ✅ **10. VERIFICACIÓN FINAL**

### **A. Health Check**
```bash
curl -X GET "$BASE_URL/health" \
  -H "Authorization: $USER_27_TOKEN"
```

### **B. Verificar data en BD**
```bash
# Conectar a PostgreSQL y ejecutar:
SELECT COUNT(*) as total_publicaciones FROM marketplace_publicaciones;
SELECT COUNT(*) as total_favoritos FROM marketplace_favoritos;
SELECT estado, COUNT(*) FROM marketplace_publicaciones GROUP BY estado;
```

---

## 🔧 **TROUBLESHOOTING**

### **Errores comunes:**

1. **401 Unauthorized**: Token expirado o inválido
   ```bash
   # Re-login
   curl -X POST "$BASE_URL/auth/login" ...
   ```

2. **403 Forbidden**: Límites excedidos
   ```bash
   # Verificar límites
   curl -X GET "$BASE_URL/marketplace/limites" ...
   ```

3. **404 Not Found**: Publicación/Gallo no existe
   ```bash
   # Verificar IDs válidos
   curl -X GET "$BASE_URL/marketplace/publicaciones" ...
   ```

4. **422 Validation Error**: Datos inválidos
   ```bash
   # Verificar esquema JSON
   ```

---

## 📊 **MÉTRICAS DE ÉXITO**

- ✅ **Publicaciones**: Crear, leer, actualizar, eliminar
- ✅ **Favoritos**: Marcar, desmarcar, listar
- ✅ **Límites**: Validación correcta por plan
- ✅ **Filtros**: Búsqueda y ordenamiento
- ✅ **JOINs**: Data completa con gallos y usuarios
- ✅ **Seguridad**: Solo propietarios pueden modificar
- ✅ **Performance**: Respuestas < 500ms
- ✅ **Data Integrity**: Foreign keys funcionando

**¡Todas las APIs del marketplace están listas y probadas! 🚀**