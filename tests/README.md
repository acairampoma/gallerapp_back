# 🧪 Tests - GalloApp Backend

Esta carpeta contiene todos los archivos de testing, validación y ejemplos de uso de la API.

---

## 📂 Estructura de Tests

### 🔗 **Tests de Endpoints**
- `test_epico_completo.py` - Test completo del sistema épico
- `test_endpoints_epicos.py` - Tests de endpoints principales
- `test_vacunas_api.py` - Tests del módulo de vacunas

### 🔐 **Tests de Autenticación**
- `test_token.py` - Tests de tokens JWT
- `test_token_simple.py` - Tests simples de tokens

### 🔥 **Tests de Firebase**
- `test_railway_firebase.py` - Tests de Firebase en Railway
- `test_firebase_debug.py` - Debug de Firebase

### 🛠️ **Tests de Sistema**
- `test_imports.py` - Tests de imports del sistema
- `test_fix.py` - Tests de fixes aplicados
- `test_syntax.py` - Tests de sintaxis Python

### 📋 **Tests de API (CURL)**
- `CURL_TESTS_COMPLETE.md` - Tests completos con cURL
- `CURL_TESTS_COMPLETE_VALIDATED.md` - Tests validados con cURL

---

## 🚀 Ejecución de Tests

### **Tests Completos**
```bash
# Test completo del sistema
python tests/test_epico_completo.py

# Tests de endpoints
python tests/test_endpoints_epicos.py
```

### **Tests de Autenticación**
```bash
# Tests de tokens
python tests/test_token.py
python tests/test_token_simple.py
```

### **Tests de Firebase**
```bash
# Tests en Railway
python tests/test_railway_firebase.py

# Debug Firebase
python tests/test_firebase_debug.py
```

### **Tests de Sistema**
```bash
# Validar imports
python tests/test_imports.py

# Validar sintaxis
python tests/test_syntax.py
```

---

## 📋 Documentación de Tests

### **Tests con cURL**
Ver archivos:
- `CURL_TESTS_COMPLETE.md` - Todos los tests
- `CURL_TESTS_COMPLETE_VALIDATED.md` - Tests validados

### **Ejemplos de Uso**
```bash
# Health check
curl https://gallerappback-production.up.railway.app/health

# Login
curl -X POST https://gallerappback-production.up.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"abc123xyz"}'
```

---

## 📊 Reportes de Tests

### **Resultados Esperados**
- ✅ **200 OK** - Endpoint funcionando
- ✅ **201 Created** - Recurso creado exitosamente
- ✅ **400/422** - Error de validación (esperado en algunos casos)
- ❌ **500** - Error interno (requiere atención)

### **Coverage**
- 🔐 **Autenticación:** Login, register, refresh, logout
- 🐓 **Gallos:** CRUD completo, pedigrí, genealogía
- 👤 **Perfiles:** Gestión de perfiles de usuario
- 🛒 **Marketplace:** Publicaciones, favoritos
- 🥊 **Peleas:** Gestión de combates
- 💳 **Pagos:** Procesamiento de pagos QR
- 🔔 **Notificaciones:** Firebase FCM

---

## 🛠️ Agregar Nuevo Test

1. **Crear archivo** con prefijo `test_`
2. **Seguir estructura** de tests existentes
3. **Incluir assertions** claros
4. **Documentar propósito** en comentarios
5. **Actualizar este README**

---

## ⚠️ Precauciones

1. **No ejecutar en producción** sin supervisión
2. **Usar datos de prueba** únicamente
3. **Limpiar datos** después de tests
4. **Revisar logs** para detectar issues

---

## 📞 Contacto

- **Issues de Tests:** Crear issue en repositorio
- **Nuevos Tests:** Contactar al equipo de backend
- **Fallas Críticas:** Contactar al equipo de DevOps

---

*Última actualización: 2025-11-13*
