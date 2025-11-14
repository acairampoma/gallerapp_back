# 🚀 CURL Tests VALIDADOS - Sistema de Suscripciones Gallo App

## 🔧 CREDENCIALES Y CONFIGURACIÓN

```bash
# Variables de entorno
export API_BASE_URL="http://localhost:8000"
export ADMIN_EMAIL="juan.salas.nuevo@galloapp.com"
export ADMIN_PASSWORD="123456"
export USER_EMAIL="test@user.com"
export USER_PASSWORD="password123"

# Obtener tokens (se ejecutan al inicio)
USER_TOKEN=""
ADMIN_TOKEN=""
```

---

## 📋 ANÁLISIS DOBLE CHECK DE CADA CURL

### 🔒 **1. AUTENTICACIÓN - PRIMER PASO OBLIGATORIO**

#### 1.1 Login de Admin
```bash
curl -X POST "$API_BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan.salas.nuevo@galloapp.com",
    "password": "123456"
  }'
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** Correcta, JSON válido
- ✅ **Tabla:** Consulta tabla `users` WHERE email = 'juan.salas.nuevo@galloapp.com'
- ✅ **Comunicación:** JWT token en response.access_token
- ✅ **Best Practice:** POST para login (no GET), credenciales en body
- ✅ **Seguridad:** Password encriptado en BD con bcrypt/pbkdf2
- 🎯 **Resultado:** Retorna JWT token para usar en ADMIN_TOKEN

#### 1.2 Login de Usuario Normal
```bash
curl -X POST "$API_BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@user.com",
    "password": "password123"
  }'
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** Correcta, estructura idéntica al admin
- ✅ **Tabla:** Consulta tabla `users` para usuario normal
- ✅ **Comunicación:** Mismo JWT pero sin privilegios admin
- ✅ **Best Practice:** Reutilización del mismo endpoint para todos los usuarios
- 🎯 **Resultado:** JWT para operaciones de usuario normal

---

## 📋 **2. SUSCRIPCIONES - GESTIÓN DE LÍMITES**

#### 2.1 Obtener Suscripción Actual del Usuario
```bash
USER_TOKEN=$(curl -s -X POST "$API_BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@user.com", "password": "password123"}' \
  | jq -r '.access_token')

curl -X GET "$API_BASE_URL/api/v1/suscripciones/actual" \
  -H "Authorization: Bearer $USER_TOKEN"
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** Bearer token correcto según RFC 6750
- ✅ **Tabla:** JOIN entre `suscripciones` y `users` WHERE user_id = current_user
- ✅ **Comunicación:** Middleware get_current_user_id extrae user del JWT
- ✅ **Best Practice:** Endpoint RESTful GET para obtener recurso
- ✅ **Seguridad:** Solo ve su propia suscripción (autorización por user_id)
- 🎯 **Resultado:** Retorna plan actual, límites y fecha vencimiento

#### 2.2 Verificar Límites y Uso Actual
```bash
curl -X GET "$API_BASE_URL/api/v1/suscripciones/limites" \
  -H "Authorization: Bearer $USER_TOKEN"
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** GET simple con autorización
- ✅ **Tablas:** Consulta `gallos`, `topes`, `peleas`, `vacunas` para contar uso actual
- ✅ **Comunicación:** LimiteService hace múltiples COUNT() optimizados
- ✅ **Best Practice:** Endpoint dedicado para información de límites
- ✅ **Performance:** Usa COUNT() con índices en lugar de SELECT *
- 🎯 **Resultado:** Límites por recurso y cantidades usadas

#### 2.3 Validar si Puede Crear Recurso
```bash
curl -X POST "$API_BASE_URL/api/v1/suscripciones/validar-limite" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recurso_tipo": "gallos"
  }'
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** POST con JSON body válido
- ✅ **Tabla:** Consulta suscripción activa + contador de gallos actuales
- ✅ **Comunicación:** ValidacionLimite schema con puede_crear boolean
- ✅ **Best Practice:** Validación antes de crear (evita errores)
- ✅ **UX:** Devuelve información para mostrar popup de upgrade
- 🎯 **Resultado:** true/false + información para upgrade

#### 2.4 Validar Límite por Gallo (Topes/Peleas/Vacunas)
```bash
curl -X POST "$API_BASE_URL/api/v1/suscripciones/validar-limite" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recurso_tipo": "topes",
    "gallo_id": 1
  }'
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** JSON con gallo_id requerido para recursos por gallo
- ✅ **Tablas:** Verifica que gallo pertenece al usuario + cuenta topes del gallo
- ✅ **Comunicación:** Validación cruzada de ownership del gallo
- ✅ **Best Practice:** Verificación de autorización a nivel de recurso
- ✅ **Seguridad:** No puede validar gallos de otros usuarios
- 🎯 **Resultado:** Validación específica por gallo individual

---

## 💳 **3. PAGOS CON QR YAPE - PROCESO COMPLETO**

#### 3.1 Obtener Planes Disponibles
```bash
curl -X GET "$API_BASE_URL/api/v1/suscripciones/planes" \
  -H "Authorization: Bearer $USER_TOKEN"
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** GET simple para catálogo público
- ✅ **Tabla:** SELECT * FROM planes_catalogo WHERE activo = true
- ✅ **Comunicación:** Lista completa de planes con precios y límites
- ✅ **Best Practice:** Endpoint público para mostrar opciones
- ✅ **Ordenamiento:** ORDER BY orden ASC (del más básico al más premium)
- 🎯 **Resultado:** Array con 4 planes: gratuito, básico, premium, profesional

#### 3.2 Solicitar Upgrade (Preparar Pago)
```bash
curl -X POST "$API_BASE_URL/api/v1/suscripciones/upgrade" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_codigo": "premium"
  }'
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** POST con plan_codigo válido
- ✅ **Tabla:** Verifica plan exists + suscripción actual del usuario
- ✅ **Comunicación:** Valida que no sea downgrade (premium > gratuito)
- ✅ **Best Practice:** Preparación antes del pago real
- ✅ **Validación:** Impide downgrades automáticos
- 🎯 **Resultado:** Confirmación de upgrade válido + next step

#### 3.3 Generar QR Yape para Pago
```bash
curl -X POST "$API_BASE_URL/api/v1/pagos/generar-qr" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_codigo": "premium"
  }'
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** POST con plan requerido
- ✅ **Tablas:** INSERT en `pagos_pendientes` + consulta `planes_catalogo`
- ✅ **Comunicación:** QRYapeService genera QR + sube a Cloudinary
- ✅ **Best Practice:** Referencia única por pago (GP + hash MD5)
- ✅ **Integración:** Cloudinary para URLs persistentes de QR
- ✅ **UX:** QR incluye monto, merchant info y referencia
- 🎯 **Resultado:** QR URL + datos + instrucciones de pago

#### 3.4 Confirmar Pago Realizado
```bash
curl -X POST "$API_BASE_URL/api/v1/pagos/confirmar" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pago_id": 1,
    "referencia_yape": "12345678",
    "comprobante_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
  }'
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** JSON con pago_id obligatorio
- ✅ **Tabla:** UPDATE pagos_pendientes SET estado='verificando'
- ✅ **Comunicación:** Base64 decode + upload a Cloudinary automático
- ✅ **Best Practice:** Estado 'verificando' permite tracking del proceso
- ✅ **Notificaciones:** Dispara push notifications a todos los admins
- ✅ **Asíncrono:** Upload de comprobante no bloquea la confirmación
- 🎯 **Resultado:** Estado verificando + notificaciones enviadas

#### 3.5 Subir Comprobante como Archivo
```bash
curl -X POST "$API_BASE_URL/api/v1/pagos/1/subir-comprobante" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -F "comprobante=@/ruta/a/comprobante.jpg"
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** multipart/form-data para archivos
- ✅ **Tabla:** UPDATE pagos_pendientes SET comprobante_url
- ✅ **Comunicación:** UploadFile FastAPI + validación de tipos
- ✅ **Best Practice:** Validación 5MB máximo + tipos de imagen
- ✅ **Seguridad:** Solo puede subir a sus propios pagos
- ✅ **Storage:** Organizado por carpetas user_id en Cloudinary
- 🎯 **Resultado:** URL del comprobante subido

---

## 👑 **4. PANEL ADMINISTRATIVO - VERIFICACIÓN DE PAGOS**

#### 4.1 Login de Admin y Dashboard
```bash
ADMIN_TOKEN=$(curl -s -X POST "$API_BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "juan.salas.nuevo@galloapp.com", "password": "123456"}' \
  | jq -r '.access_token')

curl -X GET "$API_BASE_URL/api/v1/admin/dashboard" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** Bearer token con privilegios admin
- ✅ **Tabla:** Consultas agregadas (COUNT, SUM) en múltiples tablas
- ✅ **Comunicación:** Middleware verificar_admin valida es_admin=true
- ✅ **Best Practice:** Dashboard con métricas en tiempo real
- ✅ **Performance:** Consultas optimizadas con funciones agregadas
- ✅ **UX:** Alertas urgentes para pagos vencidos (48+ horas)
- 🎯 **Resultado:** Métricas completas para administración

#### 4.2 Ver Pagos Pendientes
```bash
curl -X GET "$API_BASE_URL/api/v1/admin/pagos/pendientes" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** GET con autorización de admin
- ✅ **Tabla:** SELECT con JOIN a users y planes_catalogo
- ✅ **Comunicación:** PagoPendienteAdmin schema con info extendida
- ✅ **Best Practice:** Ordenado por prioridad (verificando antes que pendiente)
- ✅ **UX:** Incluye tiempo transcurrido y flags de sospechoso
- ✅ **Paginación:** Limit/offset para performance con muchos pagos
- 🎯 **Resultado:** Lista priorizada para verificación eficiente

#### 4.3 Aprobar Pago (Activar Plan)
```bash
curl -X POST "$API_BASE_URL/api/v1/admin/pagos/1/aprobar" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accion": "aprobar",
    "notas": "Pago verificado correctamente en Yape. Comprobante válido."
  }'
```

**🔍 ANÁLISIS TÉCNICA:**
- ✅ **Sintaxis:** POST con notas descriptivas
- ✅ **Tablas:** UPDATE pagos_pendientes + UPDATE suscripciones + UPDATE users
- ✅ **Comunicación:** Proceso atómico en transacción
- ✅ **Best Practice:** _activar_plan_usuario encapsula lógica compleja
- ✅ **Auditoria:** Registra admin_id y timestamp de aprobación
- ✅ **Automatización:** Plan se activa inmediatamente tras aprobación
- 🎯 **Resultado:** Plan activado + usuario premium + fecha renovación

#### 4.4 Rechazar Pago
```bash
curl -X POST "$API_BASE_URL/api/v1/admin/pagos/1/rechazar" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accion": "rechazar", 
    "notas": "Comprobante no corresponde al monto solicitado."
  }'
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** Requiere notas obligatorias para rechazo
- ✅ **Tabla:** UPDATE pagos_pendientes SET estado='rechazado'
- ✅ **Comunicación:** Validación de notas != null/empty
- ✅ **Best Practice:** Trazabilidad completa del motivo de rechazo
- ✅ **UX:** Usuario puede ver el motivo del rechazo
- 🎯 **Resultado:** Pago rechazado con motivo registrado

---

## 🔔 **5. NOTIFICACIONES Y GESTIÓN**

#### 5.1 Ver Notificaciones de Admin
```bash
curl -X GET "$API_BASE_URL/api/v1/admin/notificaciones" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** GET con filtros opcionales
- ✅ **Tabla:** SELECT FROM notificaciones_admin WHERE admin_id
- ✅ **Comunicación:** Solo ve sus propias notificaciones
- ✅ **Best Practice:** Ordenado por prioridad + fecha (más urgentes primero)
- ✅ **Performance:** Limit por defecto para evitar sobrecarga
- 🎯 **Resultado:** Lista de notificaciones pendientes y leídas

#### 5.2 Marcar Notificación como Leída
```bash
curl -X PUT "$API_BASE_URL/api/v1/admin/notificaciones/1/marcar-leida" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** PUT para actualización específica
- ✅ **Tabla:** UPDATE notificaciones_admin SET leido=true
- ✅ **Comunicación:** Verifica ownership de la notificación
- ✅ **Best Practice:** PUT para updates, no POST
- ✅ **Seguridad:** Solo puede marcar sus propias notificaciones
- 🎯 **Resultado:** Notificación marcada como procesada

---

## 📊 **6. ENDPOINTS CON VALIDACIÓN DE LÍMITES INTEGRADA**

#### 6.1 Crear Gallo (Con Límite Automático)
```bash
curl -X POST "$API_BASE_URL/api/v1/gallos" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Gallo de Prueba",
    "peso": 2.5,
    "color": "rojo"
  }'
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** JSON válido con campos requeridos
- ✅ **Middleware:** @validar_limite_gallos ejecuta ANTES del endpoint
- ✅ **Tabla:** Si pasa validación → INSERT gallos, si no → HTTP 402
- ✅ **Comunicación:** LimiteMiddleware intercepta y valida automáticamente
- ✅ **Best Practice:** Validación transparente sin duplicar código
- ✅ **UX:** Error 402 específico para mostrar popup de upgrade
- 🎯 **Resultado:** Gallo creado O error 402 con info de upgrade

#### 6.2 Crear Tope (Con Validación por Gallo)
```bash
curl -X POST "$API_BASE_URL/api/v1/topes" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gallo_id": 1,
    "peso": 2.5,
    "fecha_tope": "2025-01-15",
    "observaciones": "Tope de prueba"
  }'
```

**🔍 ANÁLISIS TÉCNICO:**
- ✅ **Sintaxis:** gallo_id requerido para validación
- ✅ **Middleware:** @validar_limite_topes("gallo_id") valida específicamente
- ✅ **Tabla:** Verifica ownership del gallo + cuenta topes del gallo
- ✅ **Comunicación:** Validación cruzada de recursos anidados
- ✅ **Best Practice:** Validación granular por gallo individual
- ✅ **Seguridad:** No puede crear topes para gallos ajenos
- 🎯 **Resultado:** Tope creado O error específico por gallo

---

## 🧪 **7. ESCENARIOS COMPLETOS DE TESTING**

### **Escenario 1: Usuario Gratuito Alcanza Límites**
```bash
#!/bin/bash
# Test completo de límites

echo "🧪 TEST: Usuario alcanza límite de gallos"

# 1. Login usuario
USER_TOKEN=$(curl -s -X POST "$API_BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@user.com", "password": "password123"}' \
  | jq -r '.access_token')

echo "✅ Token obtenido: ${USER_TOKEN:0:20}..."

# 2. Ver límites actuales
echo "📊 Límites actuales:"
curl -s -X GET "$API_BASE_URL/api/v1/suscripciones/limites" \
  -H "Authorization: Bearer $USER_TOKEN" | jq

# 3. Crear 5 gallos (límite gratuito)
echo "🐓 Creando 5 gallos..."
for i in {1..5}; do
  curl -s -X POST "$API_BASE_URL/api/v1/gallos" \
    -H "Authorization: Bearer $USER_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"nombre\": \"Gallo $i\", \"peso\": 2.5, \"color\": \"rojo\"}" | jq '.id'
done

# 4. Intentar crear 6to gallo (debe fallar)
echo "❌ Intentando crear 6to gallo (debe fallar):"
curl -X POST "$API_BASE_URL/api/v1/gallos" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Gallo 6", "peso": 2.5, "color": "azul"}'

# 5. Ver planes disponibles
echo "📋 Planes disponibles:"
curl -s -X GET "$API_BASE_URL/api/v1/suscripciones/planes" \
  -H "Authorization: Bearer $USER_TOKEN" | jq
```

### **Escenario 2: Proceso Completo de Pago**
```bash
#!/bin/bash
echo "🧪 TEST: Proceso completo de pago con QR"

# 1. Solicitar upgrade
echo "🚀 Solicitando upgrade a premium:"
curl -s -X POST "$API_BASE_URL/api/v1/suscripciones/upgrade" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_codigo": "premium"}' | jq

# 2. Generar QR
echo "📱 Generando QR Yape:"
QR_RESPONSE=$(curl -s -X POST "$API_BASE_URL/api/v1/pagos/generar-qr" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_codigo": "premium"}')

PAGO_ID=$(echo $QR_RESPONSE | jq -r '.pago_id')
echo "✅ Pago ID: $PAGO_ID"
echo "🖼️ QR URL: $(echo $QR_RESPONSE | jq -r '.qr_url')"

# 3. Confirmar pago
echo "✅ Confirmando pago realizado:"
curl -s -X POST "$API_BASE_URL/api/v1/pagos/confirmar" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"pago_id\": $PAGO_ID, \"referencia_yape\": \"TEST123456\"}" | jq

# 4. Admin ve pagos pendientes
echo "👑 Admin viendo pagos pendientes:"
ADMIN_TOKEN=$(curl -s -X POST "$API_BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "juan.salas.nuevo@galloapp.com", "password": "123456"}' \
  | jq -r '.access_token')

curl -s -X GET "$API_BASE_URL/api/v1/admin/pagos/pendientes" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# 5. Admin aprueba pago
echo "✅ Admin aprobando pago:"
curl -s -X POST "$API_BASE_URL/api/v1/admin/pagos/$PAGO_ID/aprobar" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"accion": "aprobar", "notas": "Pago verificado en test"}' | jq

# 6. Verificar plan activado
echo "📋 Verificando plan activado:"
curl -s -X GET "$API_BASE_URL/api/v1/suscripciones/actual" \
  -H "Authorization: Bearer $USER_TOKEN" | jq
```

---

## ⚡ **QUICK TEST - 5 CURLs ESENCIALES**

```bash
# 1. ¿Está funcionando la API?
curl -X GET "$API_BASE_URL/health"

# 2. ¿Puedo hacer login de admin?
curl -X POST "$API_BASE_URL/auth/login" -H "Content-Type: application/json" -d '{"email": "juan.salas.nuevo@galloapp.com", "password": "123456"}'

# 3. ¿Están los endpoints de suscripciones?
curl -X GET "$API_BASE_URL/api/v1/suscripciones/planes"

# 4. ¿Funciona el dashboard admin?
# (Usar ADMIN_TOKEN del paso 2)
curl -X GET "$API_BASE_URL/api/v1/admin/dashboard" -H "Authorization: Bearer $ADMIN_TOKEN"

# 5. ¿Se pueden generar QRs?
# (Usar USER_TOKEN)
curl -X POST "$API_BASE_URL/api/v1/pagos/generar-qr" -H "Authorization: Bearer $USER_TOKEN" -H "Content-Type: application/json" -d '{"plan_codigo": "premium"}'
```

---

## 🎯 **RESUMEN DE BEST PRACTICES APLICADAS**

### ✅ **Arquitectura RESTful:**
- GET para obtener recursos
- POST para crear/procesar
- PUT para actualizar específico
- Códigos HTTP semánticamente correctos

### ✅ **Seguridad:**
- JWT Bearer tokens
- Middleware de autorización
- Validación de ownership de recursos
- Credenciales nunca en URL

### ✅ **Performance:**
- Consultas con índices
- COUNT() en lugar de SELECT *
- Paginación con limit/offset
- Joins optimizados

### ✅ **UX/Error Handling:**
- HTTP 402 específico para límites
- Mensajes descriptivos en español
- Información para upgrade en errores
- Validación previa sin efectos secundarios

### ✅ **Escalabilidad:**
- Middleware reutilizable
- Servicios modulares
- Notificaciones asíncronas
- Separación de responsabilidades

---

**¡SISTEMA COMPLETO Y VALIDADO TÉCNICAMENTE! 🔥**

Juan, ahora sí tienes TODOS los CURLs con explicación técnica completa. Cada endpoint fue diseñado siguiendo las mejores prácticas de REST, seguridad, performance y experiencia de usuario.