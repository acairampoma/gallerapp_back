# 📱 FLUTTER - Instrucciones Verificación Email

## 🎯 OBJETIVO
Implementar verificación de email con código de 6 dígitos.

---

## 🔄 NUEVO FLUJO

**ANTES:** Registro → Login directo  
**AHORA:** Registro → Email código → Verificación → Login

---

## 📡 ENDPOINTS API

### 1. Registro (Actualizado)
```http
POST /auth/register
```
**Response nuevo:**
```json
{
  "verification_required": true,
  "next_step": "verify_email"
}
```

### 2. Verificar Email (NUEVO)
```http
POST /auth/verify-email
{
  "email": "usuario@email.com",
  "code": "123456"
}
```
**Response:**
```json
{
  "success": true,
  "verified": true,
  "next_step": "login"
}
```

### 3. Reenviar Código (NUEVO)
```http
POST /auth/resend-verification
{
  "email": "usuario@email.com"
}
```

### 4. Login (Actualizado)
```http
POST /auth/login
```
**Si no verificado:**
```json
{
  "login_success": false,
  "redirect_to": "verify_email"
}
```

---

## 🎨 IMPLEMENTACIÓN FLUTTER

### 1. Nueva Pantalla: `EmailVerificationScreen`

```dart
class EmailVerificationScreen extends StatefulWidget {
  final String email;
  
  const EmailVerificationScreen({Key? key, required this.email}) : super(key: key);

  @override
  _EmailVerificationScreenState createState() => _EmailVerificationScreenState();
}
```

### 2. UI Requerida

- **6 inputs numéricos** para el código
- **Timer** de 2 minutos para reenviar
- **Botón "Reenviar código"**
- **Mensaje:** "Revisa tu email: usuario@email.com"

### 3. Lógica Principal

```dart
// Verificar código
Future<void> _verifyCode() async {
  final code = _codeControllers.map((c) => c.text).join();
  
  final response = await authApi.verifyEmail(widget.email, code);
  
  if (response.verified) {
    Navigator.pushReplacementNamed(context, '/login');
  } else {
    showError(response.message);
  }
}

// Reenviar código
Future<void> _resendCode() async {
  await authApi.resendVerification(widget.email);
  showSuccess('Nuevo código enviado');
  _startTimer();
}
```

---

## 🔄 ACTUALIZAR FLOWS EXISTENTES

### Registro Screen
```dart
// Después de registro exitoso
if (response.verificationRequired) {
  Navigator.pushNamed(context, '/email-verification', arguments: response.user.email);
}
```

### Login Screen
```dart
// Si login falla por no verificado
if (!response.loginSuccess && response.redirectTo == 'verify_email') {
  Navigator.pushNamed(context, '/email-verification', arguments: email);
}
```

---

## 📦 MODELS DART

```dart
class VerifyEmailResponse {
  final bool success;
  final String message;
  final bool verified;
  final String nextStep;
  
  VerifyEmailResponse.fromJson(Map<String, dynamic> json)
      : success = json['success'],
        message = json['message'],
        verified = json['verified'],
        nextStep = json['next_step'];
}

class RegisterResponse {
  final UserResponse user;
  final bool verificationRequired;
  final String nextStep;
  
  RegisterResponse.fromJson(Map<String, dynamic> json)
      : user = UserResponse.fromJson(json['user']),
        verificationRequired = json['verification_required'] ?? false,
        nextStep = json['next_step'];
}
```

---

## ⚠️ REGLAS IMPORTANTES

1. **Código:** Exactamente 6 dígitos numéricos
2. **Timer:** 2 minutos entre reenvíos
3. **Intentos:** Máximo 5 intentos fallidos
4. **Expiración:** 15 minutos de vigencia
5. **Login bloqueado:** Si email no verificado

---

## 🧪 TESTING

```dart
test('Registro requiere verificación', () async {
  final result = await authApi.register(testUser);
  expect(result.verificationRequired, true);
});

test('Verificación exitosa', () async {
  final result = await authApi.verifyEmail(email, '123456');
  expect(result.verified, true);
});

test('Login sin verificación falla', () async {
  final result = await authApi.login(unverifiedEmail, password);
  expect(result.loginSuccess, false);
});
```

---

## 📱 EJEMPLO UI

```dart
Row(
  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
  children: List.generate(6, (index) => 
    SizedBox(
      width: 45,
      height: 45,
      child: TextField(
        controller: _codeControllers[index],
        textAlign: TextAlign.center,
        keyboardType: TextInputType.number,
        maxLength: 1,
        onChanged: (value) {
          if (value.length == 1 && index < 5) {
            FocusScope.of(context).nextFocus();
          }
        },
      ),
    ),
  ),
)
```

---

## 🚀 PRIORIDADES

1. **HIGH:** Pantalla de verificación con 6 inputs
2. **HIGH:** Actualizar servicio API con nuevos endpoints
3. **MEDIUM:** Modificar flujo registro/login
4. **LOW:** Agregar animaciones y mejor UX

---

## 📞 SOPORTE

- **Backend listo:** ✅ Sistema SMTP funcionando
- **Documentación completa:** Ver `docs/INSTRUCCIONES_FLUTTER_VERIFICACION_EMAIL.md`
- **Tests backend:** Ejecutar `python scripts/test_smtp_verification.py`

---

## 🎯 ENTREGABLES

- [ ] Pantalla `EmailVerificationScreen`
- [ ] Servicio API actualizado
- [ ] Flujo registro modificado
- [ ] Flujo login actualizado
- [ ] Tests unitarios
- [ ] Manejo de errores

---

*Listo para implementar* 🚀
