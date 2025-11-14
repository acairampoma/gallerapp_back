# 📋 ANÁLISIS Y PLAN DE MIGRACIÓN: Sistema de Registro y Verificación por Email

## 📅 Fecha de Análisis
**2025-11-14**

---

## 🎯 OBJETIVO
Migrar el sistema de registro de usuarios de SendGrid a servidor SMTP local para verificación por código de 6 dígitos.

---

## 📊 SISTEMA ACTUAL (GalloApp Backend)

### 🔐 **Endpoint de Registro Actual**
```python
POST /auth/register
```
- **Funcionamiento:** Registro directo sin verificación por email
- **Estado:** `is_verified = True` (auto-verificado)
- **Email:** Solo para recuperación de contraseña (SendGrid)

### 📧 **Servicio Email Actual (SendGrid)**
- **Archivo:** `app/services/email_service.py`
- **Función:** `send_password_reset_code()`
- **Características:**
  - Usa SendGrid API
  - HTML personalizado con tema "Casta de Gallos"
  - Solo para recuperación de contraseña
  - **NO se usa para verificación de registro**

### 🔑 **Configuración SendGrid Actual**
```python
# app/core/config.py
SENDGRID_API_KEY: str = "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"
SENDGRID_FROM_EMAIL: str = "alancairampoma@gmail.com"
SENDGRID_FROM_NAME: str = "Casta de Gallos"
```

---

## 🚀 SISTEMA SMTP DISPONIBLE (Proyecto Seguridad)

### 📧 **Servicio Email SMTP**
- **Archivo:** `C:\Users\acairamp\Documents\proyecto\Curso-Nttdata\app_ms_security\app\services\email_service.py`
- **Funciones disponibles:**
  - `send_verification_email()` - ✅ Perfecto para nuestro caso
  - `send_password_reset_code()` - Ya lo usamos
  - `send_security_alert()` - Alertas de seguridad

### ⚙️ **Configuración SMTP**
```python
# SMTP del proyecto seguridad
SMTP_HOST: str = "mail.qadrante2.com"
SMTP_PORT: int = 587
SMTP_USER: str = "sistemas@qadrante2.com"
SMTP_PASSWORD: str = "qadrante25$"
SMTP_FROM_EMAIL: str = "sistemas@qadrante2.com"
SMTP_FROM_NAME: str = "Microservicio Seguridad GenOps"
```

### 🎨 **Plantilla Email Verificación**
- **Diseño profesional** con gradientes
- **Código de 6 dígitos** destacado
- **Vigencia de 15 minutos**
- **Branding "GenOps Security"** (podemos personalizar)

---

## 🔄 PLAN DE MIGRACIÓN

### **PASO 1: Integrar Servicio SMTP**
1. **Copiar** `email_service.py` del proyecto seguridad
2. **Adaptar** configuración SMTP en `config.py`
3. **Reemplazar** servicio SendGrid actual

### **PASO 2: Modificar Flujo de Registro**
```python
# ANTES (Actual)
POST /auth/register → Usuario creado → is_verified = True → Login directo

# DESPUÉS (Nuevo)
POST /auth/register → Usuario creado → is_verified = False → Email con código → 
POST /auth/verify-email → Verificar código → is_verified = True → Login permitido
```

### **PASO 3: Nuevos Endpoints Requeridos**
```python
POST /auth/verify-email          # Verificar código de email
POST /auth/resend-verification   # Reenviar código
GET  /auth/verification-status   # Estado de verificación
```

### **PASO 4: Actualizar Middleware de Autenticación**
- Bloquear login si `is_verified = False`
- Mensaje claro: "Por favor verifica tu email"

---

## 📝 ESQUEMAS REQUERIDOS

### **Nuevo Schema para Verificación**
```python
class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str  # 6 dígitos

class VerifyEmailResponse(BaseModel):
    success: bool
    message: str
    verified: bool
    next_step: str  # "login" o "register"
```

### **Modificación Schema Register**
```python
# ANTES
class RegisterResponse:
    user: UserResponse
    profile: ProfileResponse
    message: str
    login_credentials: dict  # Eliminar esto

# DESPUÉS  
class RegisterResponse:
    user: UserResponse
    profile: ProfileResponse
    message: str
    verification_required: bool = True
    next_step: str = "verify_email"
```

---

## 🔄 CAMBIOS EN MODELOS

### **Modelo User - Nuevo Campo**
```python
class User(Base):
    # ... campos existentes
    email_verification_code: Column(String(6), nullable=True)
    email_verification_expires: Column(DateTime, nullable=True)
    # is_verified ya existe (boolean)
```

---

## 📱 INSTRUCCIONES PARA FLUTTER FRONTEND

### **Nuevo Flujo de Registro**
```dart
// 1. Registro inicial
final response = await api.register(userData);
// Response: verification_required: true

// 2. Mostrar pantalla "Verifica tu email"
// Mensaje: "Hemos enviado un código a tu@email.com"

// 3. Verificación del código
final verifyResponse = await api.verifyEmail(
  email: userData.email,
  code: userEnteredCode
);

if (verifyResponse.verified) {
  // Redirigir a login
  Navigator.pushReplacementNamed('/login');
} else {
  // Mostrar error de código inválido
  showError('Código inválido o expirado');
}
```

### **Nuevos Métodos API**
```dart
// Verificar email
Future<VerifyEmailResponse> verifyEmail({
  required String email,
  required String code
}) async {
  final response = await http.post(
    Uri.parse('$baseUrl/auth/verify-email'),
    body: jsonEncode({'email': email, 'code': code}),
    headers: {'Content-Type': 'application/json'},
  );
  return VerifyEmailResponse.fromJson(jsonDecode(response.body));
}

// Reenviar código
Future<void> resendVerification(String email) async {
  await http.post(
    Uri.parse('$baseUrl/auth/resend-verification'),
    body: jsonEncode({'email': email}),
    headers: {'Content-Type': 'application/json'},
  );
}
```

---

## ⚠️ CONSIDERACIONES IMPORTANTES

### **1. Compatibilidad con Usuarios Existentes**
- Usuarios ya registrados con `is_verified = True` → No afectados
- Nuevos registros → Requerirán verificación

### **2. Configuración SMTP en Producción**
- **Desarrollo:** Usar servidor SMTP local
- **Producción (Railway):** Configurar variables de entorno SMTP

### **3. Manejo de Errores**
- Email no llega → Opción de reenviar código
- Código expirado → Generar nuevo código automáticamente
- Email inválido → Validación antes de enviar

### **4. Seguridad**
- Límite de intentos de verificación (5 intentos)
- Rate limiting en resend-verification (1 cada 2 minutos)
- Log de todos los intentos fallidos

---

## 🚀 IMPLEMENTACIÓN PRIORITARIA

### **HIGH PRIORITY (Esta semana)**
1. ✅ Copiar y adaptar servicio SMTP
2. ✅ Agregar campos de verificación al modelo User
3. ✅ Crear endpoint `/auth/verify-email`
4. ✅ Modificar flujo de registro
5. ✅ Actualizar frontend Flutter

### **MEDIUM PRIORITY (Siguiente semana)**
1. Endpoint `/auth/resend-verification`
2. Rate limiting y seguridad
3. Logs y monitoreo
4. Tests automatizados

### **LOW PRIORITY (Futuro)**
1. Plantillas de email personalizables
2. Verificación por SMS (opcional)
3. Dashboard de verificaciones admin

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

- [ ] Copiar `email_service.py` del proyecto seguridad
- [ ] Agregar configuración SMTP a `config.py`
- [ ] Modificar modelo User con campos de verificación
- [ ] Crear schemas `VerifyEmailRequest/Response`
- [ ] Implementar endpoint `POST /auth/verify-email`
- [ ] Modificar endpoint `POST /auth/register`
- [ ] Actualizar middleware de login
- [ ] Crear endpoint `POST /auth/resend-verification`
- [ ] Actualizar frontend Flutter
- [ ] Probar flujo completo
- [ ] Documentar para equipo frontend

---

## 🎯 BENEFICIOS ESPERADOS

1. **🔒 Más Seguridad:** Verificación real de email
2. **📧 Control Total:** SMTP propio vs SendGrid
3. **💰 Costo Cero:** Sin dependencias de terceros
4. **🚀 Performance:** Local vs API externa
5. **🛠️ Mantenimiento:** Full control del sistema

---

*Este documento será actualizado durante la implementación*
