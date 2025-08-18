# 🧪 GUÍA DE PRUEBA COMPLETA - NOTIFICACIONES FIREBASE GALLOAPP

## ✅ ESTADO ACTUAL:
- ✅ Firebase configurado en Flutter
- ✅ Backend con Firebase Admin SDK
- ✅ Endpoints de notificaciones creados
- ✅ Variables de entorno listas

## 📋 PASOS PARA PROBAR:

### 1️⃣ CONFIGURAR RAILWAY:
1. Ir a tu proyecto en Railway
2. Variables > New Variable
3. Agregar TODAS las variables del archivo `RAILWAY_ENV_VARIABLES.txt`
4. Deploy automático

### 2️⃣ PROBAR EN FLUTTER:
```dart
// En tu app, después del login:
await FirebaseNotificationService.initialize();
```

### 3️⃣ PROBAR NOTIFICACIÓN DE PRUEBA:
```bash
# Con tu token JWT:
curl -X POST https://tu-backend.railway.app/api/v1/notifications/test-notification \
  -H "Authorization: Bearer TU_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### 4️⃣ FLUJO DE SUSCRIPCIÓN:
1. Usuario solicita suscripción → Se notifica a admins
2. Admin aprueba → Se notifica al usuario

## 🔥 ENDPOINTS DISPONIBLES:

### Registrar Token FCM:
```bash
POST /api/v1/notifications/register-fcm-token
{
  "fcm_token": "token_de_firebase",
  "platform": "android",
  "device_info": "Samsung Galaxy"
}
```

### Notificación de Prueba:
```bash
POST /api/v1/notifications/test-notification
# No requiere body
```

### Notificar Nueva Suscripción (a admins):
```bash
POST /api/v1/notifications/notify-admin-subscription
{
  "user_name": "Juan Pérez",
  "user_email": "juan@email.com",
  "plan_name": "Plan Premium",
  "amount": 50.00
}
```

### Notificar Aprobación (a usuario):
```bash
POST /api/v1/notifications/notify-user-approved?user_id=123&plan_name=Premium
```

## ✅ TODO LISTO PARA PROBAR!