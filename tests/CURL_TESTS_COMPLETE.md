# 🚀 CURL Tests Completos - Sistema de Suscripciones Gallo App

## 🔧 Configuración Inicial

```bash
# Variables de entorno
export API_BASE_URL="https://tu-app.railway.app/api/v1"
export TOKEN="tu_jwt_token_aqui"
export ADMIN_TOKEN="admin_jwt_token_aqui"

# Headers comunes
HEADERS="-H 'Content-Type: application/json' -H 'Authorization: Bearer $TOKEN'"
ADMIN_HEADERS="-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'"
```

---

## 👤 1. AUTENTICACIÓN

### Login de Usuario
```bash
curl -X POST "$API_BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@test.com",
    "password": "password123"
  }'
```

### Login de Admin
```bash
curl -X POST "$API_BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan.salas.nuevo@galloapp.com",
    "password": "123456"
  }'
```

---

## 📋 2. SUSCRIPCIONES

### Obtener Suscripción Actual
```bash
curl -X GET "$API_BASE_URL/suscripciones/actual" $HEADERS
```

### Obtener Límites Actuales
```bash
curl -X GET "$API_BASE_URL/suscripciones/limites" $HEADERS
```

### Validar Límite (Crear Gallo)
```bash
curl -X POST "$API_BASE_URL/suscripciones/validar-limite" $HEADERS \
  -d '{
    "recurso_tipo": "gallos"
  }'
```

### Validar Límite (Crear Tope para Gallo)
```bash
curl -X POST "$API_BASE_URL/suscripciones/validar-limite" $HEADERS \
  -d '{
    "recurso_tipo": "topes",
    "gallo_id": 1
  }'
```

### Obtener Planes Disponibles
```bash
curl -X GET "$API_BASE_URL/suscripciones/planes" $HEADERS
```

### Obtener Plan Específico
```bash
curl -X GET "$API_BASE_URL/suscripciones/planes/premium" $HEADERS
```

### Solicitar Upgrade
```bash
curl -X POST "$API_BASE_URL/suscripciones/upgrade" $HEADERS \
  -d '{
    "plan_codigo": "premium"
  }'
```

---

## 💳 3. PAGOS CON QR YAPE

### Generar QR para Pago
```bash
curl -X POST "$API_BASE_URL/pagos/generar-qr" $HEADERS \
  -d '{
    "plan_codigo": "premium"
  }'
```

### Confirmar Pago Realizado
```bash
curl -X POST "$API_BASE_URL/pagos/confirmar" $HEADERS \
  -d '{
    "pago_id": 1,
    "referencia_yape": "12345678",
    "comprobante_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
  }'
```

### Subir Comprobante de Pago
```bash
curl -X POST "$API_BASE_URL/pagos/1/subir-comprobante" \
  -H "Authorization: Bearer $TOKEN" \
  -F "comprobante=@/ruta/a/tu/comprobante.jpg"
```

### Obtener Mis Pagos
```bash
curl -X GET "$API_BASE_URL/pagos/mis-pagos" $HEADERS
```

### Obtener Detalle de Pago
```bash
curl -X GET "$API_BASE_URL/pagos/1" $HEADERS
```

---

## 👑 4. PANEL ADMINISTRATIVO

### Dashboard Admin
```bash
curl -X GET "$API_BASE_URL/admin/dashboard" $ADMIN_HEADERS
```

### Pagos Pendientes
```bash
curl -X GET "$API_BASE_URL/admin/pagos/pendientes" $ADMIN_HEADERS
```

### Pagos Pendientes con Filtros
```bash
curl -X GET "$API_BASE_URL/admin/pagos/pendientes?estado=verificando&limit=10" $ADMIN_HEADERS
```

### Aprobar Pago
```bash
curl -X POST "$API_BASE_URL/admin/pagos/1/aprobar" $ADMIN_HEADERS \
  -d '{
    "accion": "aprobar",
    "notas": "Pago verificado correctamente en Yape. Comprobante válido."
  }'
```

### Rechazar Pago
```bash
curl -X POST "$API_BASE_URL/admin/pagos/1/rechazar" $ADMIN_HEADERS \
  -d '{
    "accion": "rechazar",
    "notas": "Comprobante no corresponde al monto o es ilegible."
  }'
```

### Obtener Notificaciones Admin
```bash
curl -X GET "$API_BASE_URL/admin/notificaciones" $ADMIN_HEADERS
```

### Notificaciones No Leídas
```bash
curl -X GET "$API_BASE_URL/admin/notificaciones?leidas=false&limit=20" $ADMIN_HEADERS
```

### Marcar Notificación como Leída
```bash
curl -X PUT "$API_BASE_URL/admin/notificaciones/1/marcar-leida" $ADMIN_HEADERS
```

### Obtener Usuarios
```bash
curl -X GET "$API_BASE_URL/admin/usuarios" $ADMIN_HEADERS
```

### Buscar Usuarios
```bash
curl -X GET "$API_BASE_URL/admin/usuarios?buscar=test&solo_premium=true&limit=20" $ADMIN_HEADERS
```

---

## 🔧 5. ENDPOINTS ADMINISTRATIVOS DE SUSCRIPCIONES

### Activar Plan Manualmente
```bash
curl -X PUT "$API_BASE_URL/suscripciones/admin/123/activar-plan?plan_codigo=premium&duracion_dias=30" $ADMIN_HEADERS
```

### Estadísticas de Suscripciones
```bash
curl -X GET "$API_BASE_URL/suscripciones/admin/estadisticas" $ADMIN_HEADERS
```

### Estadísticas de Pagos
```bash
curl -X GET "$API_BASE_URL/pagos/admin/estadisticas" $ADMIN_HEADERS
```

---

## 🐓 6. ENDPOINTS INTEGRADOS CON LÍMITES

### Crear Gallo (Con Validación de Límites)
```bash
curl -X POST "$API_BASE_URL/gallos" $HEADERS \
  -d '{
    "nombre": "Gallo de Prueba",
    "peso": 2.5,
    "color": "rojo"
  }'
```

### Crear Tope (Con Validación de Límites)
```bash
curl -X POST "$API_BASE_URL/topes" $HEADERS \
  -d '{
    "gallo_id": 1,
    "peso": 2.5,
    "fecha_tope": "2025-01-15",
    "observaciones": "Tope de prueba"
  }'
```

### Crear Pelea (Con Validación de Límites)
```bash
curl -X POST "$API_BASE_URL/peleas" $HEADERS \
  -d '{
    "gallo_id": 1,
    "oponente": "Gallo Rival",
    "fecha_pelea": "2025-01-20",
    "resultado": "pendiente"
  }'
```

---

## 📊 7. RESPUESTAS ESPERADAS

### ✅ Éxito - Crear Recurso
```json
{
  "id": 123,
  "nombre": "Gallo de Prueba",
  "user_id": 1,
  "created_at": "2025-01-09T10:30:00"
}
```

### ❌ Error - Límite Superado (HTTP 402)
```json
{
  "detail": {
    "detail": "Límite de gallos alcanzado (5/5)",
    "limite_info": {
      "recurso_tipo": "gallos",
      "limite_actual": 5,
      "cantidad_usada": 5,
      "plan_recomendado": "premium",
      "upgrade_disponible": true
    },
    "accion_requerida": "upgrade_plan"
  }
}
```

### 📱 Respuesta QR Yape
```json
{
  "pago_id": 1,
  "qr_data": "yape://merchant=GALLOAPP2025&phone=999888777&amount=25.0&...",
  "qr_url": "https://res.cloudinary.com/galloapp/image/upload/v1234567890/qr_12345.png",
  "monto": 25.0,
  "plan_nombre": "Plan Premium",
  "instrucciones": [
    "📱 Abre tu aplicación Yape",
    "🎯 Selecciona 'Yapear' o 'Pagar'",
    "📷 Escanea este código QR con tu cámara",
    "💰 Verifica que el monto sea correcto",
    "✅ Confirma el pago en tu app"
  ]
}
```

---

## 🧪 8. FLUJO DE PRUEBAS COMPLETO

### Escenario 1: Usuario Gratuito Alcanza Límites
```bash
# 1. Login
TOKEN=$(curl -s -X POST "$API_BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@user.com", "password": "password123"}' \
  | jq -r '.access_token')

# 2. Crear 5 gallos (límite gratuito)
for i in {1..5}; do
  curl -X POST "$API_BASE_URL/gallos" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"nombre\": \"Gallo $i\", \"peso\": 2.5}"
done

# 3. Intentar crear 6to gallo (debe fallar con 402)
curl -X POST "$API_BASE_URL/gallos" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Gallo 6", "peso": 2.5}'

# 4. Solicitar upgrade
curl -X POST "$API_BASE_URL/suscripciones/upgrade" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_codigo": "premium"}'
```

### Escenario 2: Proceso Completo de Pago
```bash
# 1. Generar QR
PAGO_ID=$(curl -s -X POST "$API_BASE_URL/pagos/generar-qr" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_codigo": "premium"}' \
  | jq -r '.pago_id')

# 2. Confirmar pago
curl -X POST "$API_BASE_URL/pagos/confirmar" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"pago_id\": $PAGO_ID, \"referencia_yape\": \"12345678\"}"

# 3. Admin ve pagos pendientes
curl -X GET "$API_BASE_URL/admin/pagos/pendientes" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 4. Admin aprueba pago
curl -X POST "$API_BASE_URL/admin/pagos/$PAGO_ID/aprobar" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"accion": "aprobar", "notas": "Pago verificado correctamente"}'
```

---

## ⚠️ CÓDIGOS DE ESTADO HTTP

- **200**: ✅ Éxito
- **201**: ✅ Recurso creado
- **400**: ❌ Datos inválidos
- **401**: ❌ No autenticado
- **402**: 💳 **Pago requerido (límite alcanzado)**
- **403**: ❌ Sin permisos
- **404**: ❌ No encontrado
- **500**: ❌ Error interno

---

## 🔍 DEBUGGING

### Ver Logs en Tiempo Real
```bash
# En Railway
railway logs --tail

# Local
tail -f app.log
```

### Verificar Estado de BD
```bash
# Consultar suscripción
curl -X GET "$API_BASE_URL/suscripciones/actual" $HEADERS | jq

# Ver límites
curl -X GET "$API_BASE_URL/suscripciones/limites" $HEADERS | jq
```

---

## 🎯 PRÓXIMOS PASOS

1. ✅ Ejecutar todos estos CURLs tras deployment a Railway
2. ✅ Verificar integración con Cloudinary
3. ✅ Probar notificaciones admin
4. ✅ Implementar pantallas Flutter
5. ✅ Configurar push notifications