# 🔔 CONFIGURACIÓN DE WEBHOOK - MERCADO PAGO

## 📋 ¿Qué es un Webhook?

Un webhook es una URL que Mercado Pago llamará automáticamente cuando ocurra un evento de pago (aprobado, rechazado, pendiente, etc.).

---

## 🎯 PASO 1: Configurar Variable de Entorno en Railway

### URL del Webhook:
```
https://gallerappback-production.up.railway.app/api/v1/mercadopago/webhook
```

### Variable en Railway:
```bash
MERCADOPAGO_WEBHOOK_URL=https://gallerappback-production.up.railway.app/api/v1/mercadopago/webhook
```

**Cómo agregarla:**
1. Ir a Railway → Tu Proyecto Backend → **Variables**
2. Click en **"+ New Variable"**
3. Nombre: `MERCADOPAGO_WEBHOOK_URL`
4. Valor: `https://gallerappback-production.up.railway.app/api/v1/mercadopago/webhook`
5. Click en **"Add"**

---

## 🎯 PASO 2: Configurar Webhook en Mercado Pago Dashboard

### 🔗 Ir al Panel de Mercado Pago:
```
https://www.mercadopago.com.pe/developers/panel
```

### 📝 Pasos:

#### 1. **Ir a "Tus integraciones"**
   - Click en tu aplicación (o crear una nueva)
   - Nombre sugerido: **"Casta de Gallos"**

#### 2. **Ir a la sección "Webhooks"**
   - En el menú lateral, buscar **"Webhooks"** o **"Notificaciones"**

#### 3. **Configurar URL de Producción**
   ```
   URL: https://gallerappback-production.up.railway.app/api/v1/mercadopago/webhook
   ```

#### 4. **Seleccionar Eventos a Notificar**
   Marcar estos eventos:
   - ✅ `payment` - Pagos
   - ✅ `merchant_order` - Órdenes
   - ✅ `point_integration_wh` - Integraciones (opcional)

#### 5. **Guardar Configuración**
   - Click en **"Guardar"** o **"Crear Webhook"**

---

## 🧪 PASO 3: Probar el Webhook

### Opción 1: Desde Mercado Pago Dashboard
1. En la sección de Webhooks, buscar **"Probar Webhook"**
2. Seleccionar evento: `payment`
3. Click en **"Enviar Prueba"**
4. Verificar que llegue al backend

### Opción 2: Hacer un Pago de Prueba
1. Usar las credenciales de TEST
2. Crear una preferencia de pago
3. Realizar un pago con tarjeta de prueba
4. Ver logs en Railway

---

## 🔍 PASO 4: Verificar que Funciona

### Ver Logs en Railway:
1. Ir a Railway → Tu Proyecto Backend → **Deployments**
2. Click en el deployment activo
3. Ver **"View Logs"**
4. Buscar mensajes como:
   ```
   🔔 [Webhook] Notificación recibida de Mercado Pago
   💳 [Webhook] Tipo: payment
   🆔 [Webhook] Payment ID: 123456789
   ```

### Endpoint para Verificar:
```bash
GET https://gallerappback-production.up.railway.app/api/v1/mercadopago/webhook
```

Debería responder:
```json
{
  "message": "Webhook de Mercado Pago activo",
  "status": "ok"
}
```

---

## 🧪 TARJETAS DE PRUEBA MERCADO PAGO

### ✅ Tarjeta Aprobada:
```
Número: 5031 7557 3453 0604
CVV: 123
Fecha: 11/25
Nombre: APRO
```

### ❌ Tarjeta Rechazada:
```
Número: 5031 4332 1540 6351
CVV: 123
Fecha: 11/25
Nombre: OTHE
```

### ⏳ Tarjeta Pendiente:
```
Número: 5031 4332 1540 6351
CVV: 123
Fecha: 11/25
Nombre: CONT
```

---

## 🔐 SEGURIDAD DEL WEBHOOK

### Validación de Firma (Recomendado para Producción):

El webhook ya valida:
1. ✅ Que venga de Mercado Pago
2. ✅ Que el `payment_id` exista
3. ✅ Que la suscripción exista en la BD

### Headers que Mercado Pago envía:
```
x-signature: <firma>
x-request-id: <id único>
```

---

## 📊 EVENTOS QUE MANEJA EL WEBHOOK

| Evento | Acción |
|--------|--------|
| `payment.created` | Se crea un pago |
| `payment.updated` | Se actualiza el estado del pago |
| `payment.approved` | ✅ Pago aprobado → Activar suscripción |
| `payment.rejected` | ❌ Pago rechazado → Notificar usuario |
| `payment.pending` | ⏳ Pago pendiente → Esperar |

---

## 🚨 TROUBLESHOOTING

### ❌ El webhook no recibe notificaciones:

1. **Verificar URL:**
   ```bash
   curl https://gallerappback-production.up.railway.app/api/v1/mercadopago/webhook
   ```
   Debe responder con status 200

2. **Verificar en Mercado Pago:**
   - Panel → Webhooks → Ver historial de envíos
   - Verificar errores (4xx, 5xx)

3. **Ver logs en Railway:**
   ```
   Railway → Deployments → View Logs
   ```

4. **Verificar variable de entorno:**
   ```bash
   MERCADOPAGO_WEBHOOK_URL=https://gallerappback-production.up.railway.app/api/v1/mercadopago/webhook
   ```

### ❌ El webhook responde 500:

1. Ver logs detallados en Railway
2. Verificar que la BD esté accesible
3. Verificar que las credenciales de Mercado Pago sean correctas

---

## 📝 RESUMEN DE CONFIGURACIÓN

```bash
# Variables de Entorno en Railway - PRODUCCIÓN
MERCADOPAGO_PUBLIC_KEY=APP_USR-d5e312da-c279-4f17-a15b-4ba1875684a6
MERCADOPAGO_ACCESS_TOKEN=APP_USR-7703477841155843-111717-fce079a15cc64d5b8284eacdea2bbaa8-2994884661
MERCADOPAGO_ENVIRONMENT=production
MERCADOPAGO_WEBHOOK_URL=https://gallerappback-production.up.railway.app/api/v1/mercadopago/webhook
MERCADOPAGO_WEBHOOK_SECRET=d2f6c95a32506ffc782f94be3bc20ab99a06fde48052d2c53c49185d56925f04
FRONTEND_URL=https://app-gallera-production.up.railway.app
MERCADOPAGO_CLIENT_ID=7703477841155843
MERCADOPAGO_CLIENT_SECRET=ggMZCCpTQJkMCcLuP1CACPTLDqCdjTDo
```

```
# URL del Webhook en Mercado Pago Dashboard
https://gallerappback-production.up.railway.app/api/v1/mercadopago/webhook
```

---

## ✅ CHECKLIST FINAL

- [ ] Variables de entorno configuradas en Railway
- [ ] Backend desplegado y funcionando
- [ ] Webhook configurado en Mercado Pago Dashboard
- [ ] Webhook probado con evento de prueba
- [ ] Logs verificados en Railway
- [ ] Pago de prueba realizado exitosamente

---

## 🔗 ENLACES ÚTILES

- **Mercado Pago Developers:** https://www.mercadopago.com.pe/developers
- **Documentación Webhooks:** https://www.mercadopago.com.pe/developers/es/docs/your-integrations/notifications/webhooks
- **Tarjetas de Prueba:** https://www.mercadopago.com.pe/developers/es/docs/checkout-api/testing

---

**¡LISTO CUMPA! 🔥 Ahora tu webhook está configurado y listo para recibir notificaciones de Mercado Pago.**
