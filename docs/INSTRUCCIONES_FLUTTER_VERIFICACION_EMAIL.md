# 📱 INSTRUCCIONES FLUTTER - Nuevo Flujo de Verificación por Email

## 📅 Fecha de Actualización
**2025-11-14**

---

## 🎯 OBJETIVO
Implementar el nuevo flujo de registro con verificación de email mediante código de 6 dígitos usando SMTP propio.

---

## 🔄 NUEVO FLUJO DE REGISTRO

### **ANTES (Flujo Anterior)**
```
Registro → Login Directo (sin verificación)
```

### **AHORA (Nuevo Flujo)**
```
Registro → Email con Código → Verificación → Login Permitido
```

---

## 📡 ENDPOINTS API NUEVOS

### **1. Registro con Verificación**
```http
POST /auth/register
Content-Type: application/json

{
  "email": "usuario@email.com",
  "password": "password123",
  "nombre_completo": "Juan Pérez",
  "telefono": "987654321",
  "nombre_galpon": "Mi Gallo",
  "ciudad": "Lima",
  "ubigeo": "150101"
}
```

**Response:**
```json
{
  "user": {
    "id": 123,
    "email": "usuario@email.com",
    "is_verified": false,
    "is_active": true,
    "is_premium": false,
    "es_admin": false,
    "created_at": "2025-11-14T12:00:00Z"
  },
  "profile": {
    "id": 456,
    "nombre_completo": "Juan Pérez",
    "telefono": "987654321",
    "nombre_galpon": "Mi Gallo",
    "ciudad": "Lima",
    "ubigeo": "150101"
  },
  "message": "Usuario usuario@email.com registrado. Revisa tu email para verificar tu cuenta.",
  "verification_required": true,
  "next_step": "verify_email"
}
```

### **2. Verificar Código de Email**
```http
POST /auth/verify-email
Content-Type: application/json

{
  "email": "usuario@email.com",
  "code": "123456"
}
```

**Response Exitoso:**
```json
{
  "success": true,
  "message": "¡Email verificado exitosamente! Ya puedes iniciar sesión.",
  "verified": true,
  "next_step": "login",
  "user_data": {
    "email": "usuario@email.com",
    "is_verified": true
  }
}
```

**Response Error:**
```json
{
  "success": false,
  "message": "Código inválido o expirado. Intento 1/5",
  "verified": false,
  "next_step": "verify"
}
```

### **3. Reenviar Código de Verificación**
```http
POST /auth/resend-verification
Content-Type: application/json

{
  "email": "usuario@email.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Nuevo código de verificación enviado a tu email"
}
```

### **4. Verificar Estado de Verificación**
```http
GET /auth/verification-status/usuario@email.com
```

**Response:**
```json
{
  "email": "usuario@email.com",
  "is_verified": false,
  "verification_sent": true,
  "can_resend": false,
  "message": "Email pendiente de verificación"
}
```

### **5. Login con Verificación Requerida**
```http
POST /auth/login
Content-Type: application/json

{
  "email": "usuario@email.com",
  "password": "password123"
}
```

**Response si NO está verificado:**
```json
{
  "user": {
    "id": 123,
    "email": "usuario@email.com",
    "is_verified": false
  },
  "profile": null,
  "token": null,
  "message": "Debes verificar tu email antes de iniciar sesión. Revisa tu bandeja de entrada.",
  "login_success": false,
  "redirect_to": "verify_email"
}
```

**Response si SÍ está verificado:**
```json
{
  "user": { ... },
  "profile": { ... },
  "token": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 30
  },
  "message": "Bienvenido Juan Pérez",
  "login_success": true,
  "redirect_to": "home"
}
```

---

## 🎨 IMPLEMENTACIÓN FLUTTER

### **1. Nuevo Servicio API**
```dart
class AuthApiService {
  final Dio _dio;

  AuthApiService(this._dio);

  // 📧 Registro con verificación
  Future<RegisterResponse> register(UserRegisterData data) async {
    try {
      final response = await _dio.post('/auth/register', data: data.toJson());
      return RegisterResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw AuthException(e.response?.data['message'] ?? 'Error en registro');
    }
  }

  // 📧 Verificar email
  Future<VerifyEmailResponse> verifyEmail(String email, String code) async {
    try {
      final response = await _dio.post('/auth/verify-email', data: {
        'email': email,
        'code': code,
      });
      return VerifyEmailResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw AuthException(e.response?.data['message'] ?? 'Error verificando email');
    }
  }

  // 📧 Reenviar código
  Future<MessageResponse> resendVerification(String email) async {
    try {
      final response = await _dio.post('/auth/resend-verification', data: {
        'email': email,
      });
      return MessageResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw AuthException(e.response?.data['message'] ?? 'Error reenviando código');
    }
  }

  // 📧 Verificar estado
  Future<VerificationStatusResponse> getVerificationStatus(String email) async {
    try {
      final response = await _dio.get('/auth/verification-status/$email');
      return VerificationStatusResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw AuthException(e.response?.data['message'] ?? 'Error verificando estado');
    }
  }

  // 🔐 Login (actualizado)
  Future<LoginResponse> login(String email, String password) async {
    try {
      final response = await _dio.post('/auth/login', data: {
        'email': email,
        'password': password,
      });
      return LoginResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw AuthException(e.response?.data['message'] ?? 'Error en login');
    }
  }
}
```

### **2. Models Dart**
```dart
class RegisterResponse {
  final UserResponse user;
  final ProfileResponse? profile;
  final String message;
  final bool verificationRequired;
  final String nextStep;

  RegisterResponse.fromJson(Map<String, dynamic> json)
      : user = UserResponse.fromJson(json['user']),
        profile = json['profile'] != null ? ProfileResponse.fromJson(json['profile']) : null,
        message = json['message'],
        verificationRequired = json['verification_required'] ?? false,
        nextStep = json['next_step'];
}

class VerifyEmailResponse {
  final bool success;
  final String message;
  final bool verified;
  final String nextStep;
  final Map<String, dynamic>? userData;

  VerifyEmailResponse.fromJson(Map<String, dynamic> json)
      : success = json['success'],
        message = json['message'],
        verified = json['verified'],
        nextStep = json['next_step'],
        userData = json['user_data'];
}

class VerificationStatusResponse {
  final String email;
  final bool isVerified;
  final bool verificationSent;
  final bool canResend;
  final String message;

  VerificationStatusResponse.fromJson(Map<String, dynamic> json)
      : email = json['email'],
        isVerified = json['is_verified'],
        verificationSent = json['verification_sent'],
        canResend = json['can_resend'],
        message = json['message'];
}
```

### **3. UI - Pantalla de Verificación**
```dart
class EmailVerificationScreen extends StatefulWidget {
  final String email;
  
  const EmailVerificationScreen({Key? key, required this.email}) : super(key: key);

  @override
  _EmailVerificationScreenState createState() => _EmailVerificationScreenState();
}

class _EmailVerificationScreenState extends State<EmailVerificationScreen> {
  final List<TextEditingController> _codeControllers = List.generate(6, (_) => TextEditingController());
  bool _isLoading = false;
  int _resendTimer = 0;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _startResendTimer();
  }

  void _startResendTimer() {
    setState(() => _resendTimer = 120);
    _timer = Timer.periodic(Duration(seconds: 1), (timer) {
      if (_resendTimer > 0) {
        setState(() => _resendTimer--);
      } else {
        timer.cancel();
      }
    });
  }

  Future<void> _verifyCode() async {
    final code = _codeControllers.map((c) => c.text).join();
    
    if (code.length != 6) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ingresa el código completo de 6 dígitos')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final response = await authApiService.verifyEmail(widget.email, code);
      
      if (response.verified) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('¡Email verificado exitosamente!')),
        );
        Navigator.pushReplacementNamed(context, '/login');
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(response.message)),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _resendCode() async {
    if (_resendTimer > 0) return;

    setState(() => _isLoading = true);

    try {
      await authApiService.resendVerification(widget.email);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Nuevo código enviado')),
      );
      _startResendTimer();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Verificar Email')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Icon(Icons.email_outlined, size: 80, color: Theme.of(context).primaryColor),
            SizedBox(height: 16),
            Text(
              'Verifica tu email',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            SizedBox(height: 8),
            Text(
              'Hemos enviado un código a ${widget.email}',
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 32),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: List.generate(6, (index) => 
                Container(
                  width: 45,
                  height: 45,
                  child: TextField(
                    controller: _codeControllers[index],
                    textAlign: TextAlign.center,
                    keyboardType: TextInputType.number,
                    maxLength: 1,
                    decoration: InputDecoration(
                      counterText: '',
                      border: OutlineInputBorder(),
                    ),
                    onChanged: (value) {
                      if (value.length == 1 && index < 5) {
                        FocusScope.of(context).nextFocus();
                      }
                    },
                  ),
                ),
              ),
            ),
            SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _verifyCode,
                child: _isLoading 
                  ? CircularProgressIndicator(color: Colors.white)
                  : Text('Verificar Email'),
              ),
            ),
            SizedBox(height: 16),
            TextButton(
              onPressed: _resendTimer > 0 || _isLoading ? null : _resendCode,
              child: Text(
                _resendTimer > 0 
                  ? 'Reenviar código en ${_resendTimer}s'
                  : 'Reenviar código',
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _timer?.cancel();
    for (var controller in _codeControllers) {
      controller.dispose();
    }
    super.dispose();
  }
}
```

### **4. Navegación Actualizada**
```dart
// En tu registro screen
Future<void> _handleRegister(UserRegisterData userData) async {
  try {
    final response = await authApiService.register(userData);
    
    if (response.verificationRequired) {
      // Navegar a pantalla de verificación
      Navigator.pushReplacementNamed(
        context,
        '/email-verification',
        arguments: {'email': userData.email},
      );
    } else {
      // Flujo antiguo (ya no debería ocurrir)
      Navigator.pushReplacementNamed(context, '/login');
    }
  } catch (e) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Error: ${e.toString()}')),
    );
  }
}

// En tu login screen
Future<void> _handleLogin(String email, String password) async {
  try {
    final response = await authApiService.login(email, password);
    
    if (response.loginSuccess) {
      // Login exitoso
      Navigator.pushReplacementNamed(context, '/home');
    } else {
      // Email no verificado
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(response.message)),
      );
      Navigator.pushReplacementNamed(
        context,
        '/email-verification',
        arguments: {'email': email},
      );
    }
  } catch (e) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Error: ${e.toString()}')),
    );
  }
}
```

---

## ⚠️ CONSIDERACIONES IMPORTANTES

### **1. Manejo de Errores**
- **Código inválido:** Mostrar contador de intentos (5 máximo)
- **Código expirado:** Ofrecer reenviar automáticamente
- **Email no llega:** Botón de reenviar con timer de 2 minutos
- **Usuario ya verificado:** Redirigir directamente al login

### **2. UX/UI Recomendaciones**
- **Input de 6 dígitos:** Campos separados o un solo campo con formateo
- **Auto-focus:** Pasar al siguiente campo automáticamente
- **Timer visual:** Mostrar cuenta regresiva para reenvío
- **Feedback claro:** Estados de loading y mensajes de error

### **3. Seguridad**
- **Rate limiting:** El backend ya maneja límites de intentos
- **Validación frontend:** Verificar formato de 6 dígitos antes de enviar
- **Timeout:** Considerar expiración local de 15 minutos

### **4. Testing**
```dart
// Test cases para implementar
test('Registro exitoso envía a verificación', () async {
  final result = await authApiService.register(testUser);
  expect(result.verificationRequired, true);
  expect(result.nextStep, 'verify_email');
});

test('Verificación con código correcto', () async {
  final result = await authApiService.verifyEmail(email, correctCode);
  expect(result.verified, true);
  expect(result.nextStep, 'login');
});

test('Login sin verificación es rechazado', () async {
  final result = await authApiService.login(unverifiedEmail, password);
  expect(result.loginSuccess, false);
  expect(result.redirectTo, 'verify_email');
});
```

---

## 🚀 DESPLIEGUE

### **1. Configuración**
- No se requiere configuración adicional en el app
- El backend maneja el cambio de SendGrid a SMTP automáticamente

### **2. Compatibilidad**
- **Usuarios existentes:** Ya verificados, no afectados
- **Nuevos usuarios:** Requerirán verificación obligatoria
- **Offline:** Mostrar mensaje claro de requerir conexión

### **3. Monitoreo**
- Registrar tasas de verificación exitosas
- Medir tiempo promedio de verificación
- Trackear reenvíos de código

---

## 📞 SOPORTE

### **Problemas Comunes:**
1. **Email no llega:** Verificar carpeta de spam
2. **Código incorrecto:** Ofrecer reenviar después de 2 minutos
3. **Código expirado:** Generar nuevo código automáticamente
4. **Usuario bloqueado:** Contactar soporte después de 5 intentos

### **Contacto Backend:**
- **Logs:** Revisar logs de SMTP en Railway
- **Configuración:** Variables de entorno SMTP configuradas
- **Monitoreo:** Dashboard de Railway para errores

---

## 🎯 RESUMEN

✅ **Backend listo:** SMTP configurado y endpoints funcionando  
✅ **Frontend requerido:** Implementar nuevo flujo de UI  
✅ **Testing:** Scripts de prueba disponibles  
✅ **Documentación:** Guía completa implementada  

**Próximo paso:** Implementar UI de verificación en Flutter y probar flujo completo.

---

*Última actualización: 2025-11-14*  
*Responsable: Backend Team*
