# 💳 Mercado Pago - Guía de Configuración Completa

## 📋 Tabla de Contenidos
1. [Archivos Creados](#archivos-creados)
2. [Variables de Entorno](#variables-de-entorno)
3. [Migración de Base de Datos](#migración-de-base-de-datos)
4. [Endpoints Disponibles](#endpoints-disponibles)
5. [Flujo de Pago Completo](#flujo-de-pago-completo)
6. [Testing](#testing)
7. [Deployment en Railway](#deployment-en-railway)

---

## 1. 📁 Archivos Creados

### Backend:
```
app/
├── services/
│   └── mercadopago_service.py          ✅ NUEVO - Servicio principal
├── api/v1/
│   └── mercadopago.py                  ✅ NUEVO - Endpoints API
├── models/
│   └── suscripcion.py                  ✏️ MODIFICADO - Campos MP agregados
└── main.py                             ✏️ MODIFICADO - Router registrado

migrations/
└── add_mercadopago_fields_to_suscripciones.sql  ✅ NUEVO

requirements.txt                        ✏️ MODIFICADO - SDK agregado
```

---

## 2. 🔐 Variables de Entorno

### En Railway (Production):

Ve a tu proyecto en Railway → Variables → Add Variable:

```bash
# 💳 Mercado Pago - PRODUCCIÓN
MERCADOPAGO_ACCESS_TOKEN=APP_USR-XXXXXXXXXX-XXXXXX-XXXXXXXX-XXXXXXXX
MERCADOPAGO_PUBLIC_KEY=APP_USR-XXXXXXXXXX-XXXXXX-XXXXXXXX
MERCADOPAGO_WEBHOOK_URL=https://gallerappback-production.up.railway.app/api/v1/mercadopago/webhook
MERCADOPAGO_ENVIRONMENT=production

# Frontend URL (para redirecciones)
FRONTEND_URL=https://app-gallera-production.up.railway.app
```

### ¿Dónde obtener las credenciales?

1. **Ir a Mercado Pago Developers:**
   ```
   https://www.mercadopago.com.pe/developers/panel
   ```

2. **Crear una aplicación:**
   - Click en "Tus integraciones"
   - Click en "Crear aplicación"
   - Nombre: "Casta de Gallos"
   - Producto: "Pagos online"

3. **Obtener credenciales:**
   - Ve a "Credenciales"
   - Copia el **Access Token** de Producción
   - Copia la **Public Key** de Producción

### Para Testing (Opcional):

```bash
MERCADOPAGO_TEST_ACCESS_TOKEN=TEST-XXXXXXXXXX-XXXXXX-XXXXXXXX
MERCADOPAGO_TEST_PUBLIC_KEY=TEST-XXXXXXXXXX-XXXXXX-XXXXXXXX
MERCADOPAGO_ENVIRONMENT=sandbox
```

---

## 3. 🗄️ Migración de Base de Datos

### Ejecutar en Railway:

1. **Conectarse a la BD de Railway:**
   ```bash
   # Desde Railway CLI
   railway connect postgres
   ```

2. **Ejecutar migración:**
   ```sql
   -- Copiar y pegar el contenido de:
   migrations/add_mercadopago_fields_to_suscripciones.sql
   ```

3. **Verificar:**
   ```sql
   SELECT column_name, data_type 
   FROM information_schema.columns
   WHERE table_name = 'suscripciones'
   AND column_name LIKE '%payment%';
   ```

### Campos agregados:
- `payment_id` - ID del pago en Mercado Pago
- `preference_id` - ID de la preferencia
- `external_reference` - Referencia única
- `payment_method` - Método de pago (yape, credit_card, etc)
- `payment_status` - Estado (approved, pending, rejected)
- `payment_status_detail` - Detalle del estado
- `transaction_amount` - Monto real pagado
- `fecha_pago` - Fecha del pago
- `mercadopago_data` - JSON con data completa

---

## 4. 🌐 Endpoints Disponibles

### Para el Frontend:

#### 1. Crear Preferencia de Pago
```http
POST /api/v1/mercadopago/crear-preferencia
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "plan_codigo": "premium"
}

Response:
{
  "success": true,
  "preference_id": "123456789-abc-def",
  "init_point": "https://www.mercadopago.com.pe/checkout/v1/redirect?pref_id=...",
  "suscripcion_id": 42,
  "plan": {
    "codigo": "premium",
    "nombre": "Plan Premium",
    "precio": 50.00,
    "duracion_dias": 30
  }
}
```

#### 2. Consultar Estado de Pago
```http
GET /api/v1/mercadopago/estado-pago/{payment_id}
Authorization: Bearer {JWT_TOKEN}

Response:
{
  "success": true,
  "payment_id": "123456789",
  "status": "approved",
  "status_detail": "accredited",
  "monto": 50.00,
  "metodo_pago": "yape",
  "fecha_aprobacion": "2024-11-17T15:30:00Z",
  "suscripcion": {
    "id": 42,
    "plan": "Plan Premium",
    "status": "active",
    "fecha_inicio": "2024-11-17",
    "fecha_fin": "2024-12-17"
  }
}
```

#### 3. Obtener Mi Suscripción
```http
GET /api/v1/mercadopago/mi-suscripcion
Authorization: Bearer {JWT_TOKEN}

Response:
{
  "success": true,
  "tiene_suscripcion": true,
  "suscripcion": {
    "id": 42,
    "plan_type": "premium",
    "plan_name": "Plan Premium",
    "precio": 50.00,
    "status": "active",
    "fecha_inicio": "2024-11-17",
    "fecha_fin": "2024-12-17",
    "dias_restantes": 30,
    "payment_method": "yape",
    "limites": {
      "gallos_maximo": 50,
      "topes_por_gallo": 20,
      "peleas_por_gallo": 20,
      "vacunas_por_gallo": 20
    }
  }
}
```

### Webhook (Automático):

```http
POST /api/v1/mercadopago/webhook
Content-Type: application/json

{
  "type": "payment",
  "data": {
    "id": "123456789"
  }
}
```

Este endpoint es llamado automáticamente por Mercado Pago cuando:
- Un pago es aprobado ✅
- Un pago es rechazado ❌
- Un pago queda pendiente ⏳

---

## 5. 🔄 Flujo de Pago Completo

### Paso a Paso:

```
1️⃣ USUARIO SELECCIONA PLAN
   Frontend: Usuario elige "Plan Premium"
   
2️⃣ CREAR PREFERENCIA
   POST /api/v1/mercadopago/crear-preferencia
   Backend: Crea preferencia en Mercado Pago
   Backend: Crea suscripción con status="pending"
   Response: Devuelve init_point (URL de pago)
   
3️⃣ REDIRIGIR A CHECKOUT
   Frontend: Abre init_point en navegador
   Usuario: Paga con Yape/Tarjeta/etc en Mercado Pago
   
4️⃣ MERCADO PAGO PROCESA PAGO
   MP: Valida pago
   MP: Envía webhook a tu backend
   
5️⃣ WEBHOOK ACTIVA SUSCRIPCIÓN
   POST /api/v1/mercadopago/webhook
   Backend: Recibe notificación
   Backend: Actualiza suscripción a status="active"
   Backend: Guarda payment_id, payment_method, etc
   Backend: Desactiva otras suscripciones del usuario
   
6️⃣ USUARIO ES REDIRIGIDO
   MP: Redirige a /pago-exitoso
   Frontend: Muestra mensaje de éxito
   Frontend: Actualiza UI con plan activo
```

### Diagrama:

```
👤 USUARIO                    🏦 MERCADO PAGO              💻 TU BACKEND
┌─────────────────┐          ┌─────────────────────┐      ┌─────────────────┐
│ 1. Elige plan   │   ──►    │                     │      │ 2. Crea         │
│    Premium      │          │                     │      │    preferencia  │
│                 │          │                     │      │    + suscripción│
│                 │          │                     │      │    pending      │
│                 │   ◄──    │                     │   ◄──│                 │
│ 3. Abre checkout│          │                     │      │                 │
│    de MP        │   ──►    │ 4. Procesa pago     │      │                 │
│                 │          │    con Yape         │      │                 │
│                 │          │                     │   ──►│ 5. Webhook      │
│                 │          │                     │      │    activa       │
│                 │          │                     │      │    suscripción  │
│ 6. Redirigido   │   ◄──    │ Redirige a success  │      │                 │
│    a /pago-     │          │                     │      │                 │
│    exitoso      │          │                     │      │                 │
└─────────────────┘          └─────────────────────┘      └─────────────────┘
```

---

## 6. 🧪 Testing

### 1. Probar Creación de Preferencia:

```bash
curl -X POST https://gallerappback-production.up.railway.app/api/v1/mercadopago/crear-preferencia \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_codigo": "premium"}'
```

### 2. Probar Webhook (Simulado):

```bash
curl -X POST https://gallerappback-production.up.railway.app/api/v1/mercadopago/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "type": "payment",
    "data": {
      "id": "123456789"
    }
  }'
```

### 3. Verificar Suscripción:

```bash
curl -X GET https://gallerappback-production.up.railway.app/api/v1/mercadopago/mi-suscripcion \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 7. 🚀 Deployment en Railway

### Checklist de Deployment:

- [ ] 1. Variables de entorno configuradas en Railway
- [ ] 2. Migración de BD ejecutada
- [ ] 3. SDK de Mercado Pago instalado (`requirements.txt`)
- [ ] 4. Código pusheado a GitHub
- [ ] 5. Railway redeploya automáticamente
- [ ] 6. Verificar logs: `railway logs`
- [ ] 7. Probar endpoint de salud: `GET /`
- [ ] 8. Probar creación de preferencia
- [ ] 9. Configurar webhook URL en Mercado Pago

### Configurar Webhook en Mercado Pago:

1. **Ir a tu aplicación en MP:**
   ```
   https://www.mercadopago.com.pe/developers/panel/app/{APP_ID}/webhooks
   ```

2. **Agregar webhook:**
   - URL: `https://gallerappback-production.up.railway.app/api/v1/mercadopago/webhook`
   - Eventos: Seleccionar "Pagos"
   - Guardar

3. **Verificar:**
   - Hacer un pago de prueba
   - Ver logs en Railway: `railway logs --follow`
   - Debe aparecer: `📬 Webhook recibido de Mercado Pago`

---

## 8. 📊 Monitoreo

### Logs Importantes:

```bash
# Ver logs en tiempo real
railway logs --follow

# Buscar logs de Mercado Pago
railway logs | grep "mercadopago"

# Buscar webhooks
railway logs | grep "Webhook recibido"
```

### Queries de BD para Monitoreo:

```sql
-- Ver suscripciones activas con Mercado Pago
SELECT 
    u.email,
    s.plan_name,
    s.payment_method,
    s.transaction_amount,
    s.fecha_pago,
    s.status
FROM suscripciones s
JOIN users u ON s.user_id = u.id
WHERE s.payment_id IS NOT NULL
ORDER BY s.fecha_pago DESC;

-- Ver pagos pendientes
SELECT 
    u.email,
    s.plan_name,
    s.preference_id,
    s.created_at
FROM suscripciones s
JOIN users u ON s.user_id = u.id
WHERE s.status = 'pending'
AND s.preference_id IS NOT NULL
ORDER BY s.created_at DESC;

-- Estadísticas de pagos
SELECT 
    payment_method,
    COUNT(*) as total,
    SUM(transaction_amount) as monto_total
FROM suscripciones
WHERE payment_status = 'approved'
GROUP BY payment_method;
```

---

## 9. 🔧 Troubleshooting

### Problema: "Mercado Pago no configurado"

**Solución:**
- Verificar que `MERCADOPAGO_ACCESS_TOKEN` esté en Railway
- Verificar que no tenga espacios extra
- Reiniciar el servicio en Railway

### Problema: "Webhook no llega"

**Solución:**
- Verificar URL del webhook en Mercado Pago
- Verificar que Railway esté corriendo
- Ver logs: `railway logs | grep webhook`
- Probar con curl manualmente

### Problema: "Suscripción no se activa"

**Solución:**
- Verificar que el webhook se recibió
- Verificar que `external_reference` coincida
- Ver logs de procesamiento del webhook
- Verificar estado del pago en Mercado Pago

---

## 10. 📞 Soporte

### Recursos:
- **Documentación MP:** https://www.mercadopago.com.pe/developers/es/docs
- **SDK Python:** https://github.com/mercadopago/sdk-python
- **Webhooks:** https://www.mercadopago.com.pe/developers/es/docs/your-integrations/notifications/webhooks

### Contacto Mercado Pago:
- **Email:** developers@mercadopago.com
- **Chat:** Desde el panel de desarrolladores

---

**¡Listo cumpa! 🔥 Mercado Pago integrado y documentado.**
