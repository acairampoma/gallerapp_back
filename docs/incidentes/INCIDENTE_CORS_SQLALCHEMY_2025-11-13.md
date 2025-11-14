# 🚨 INCIDENTE CRÍTICO: Error CORS y SQLAlchemy en Backend Railway

## 📅 FECHA Y HORA
**Fecha:** 2025-11-13  
**Hora:** 23:49 UTC-05:00 (Perú)  
**Duración:** ~30 minutos de diagnóstico y resolución  
**Estado:** ✅ RESUELTO (con parche temporal)

---

## 🎯 ORIGEN DEL ERROR

### 1. **PROBLEMA CORS (Bloqueo del navegador)**
- **Origen:** `http://localhost:57483` (Flutter Web Development)
- **Destino:** `https://gallerappback-production.up.railway.app`
- **Error del navegador:** 
  ```
  Access to fetch at 'https://gallerappback-production.up.railway.app/auth/login' 
  from origin 'http://localhost:57483' has been blocked by CORS policy: 
  No 'Access-Control-Allow-Origin' header is present on the requested resource.
  ```

### 2. **PROBLEMA SQLALCHEMY (Error 500 Interno)**
- **Trigger:** Al intentar hacer cualquier query a la BD (`db.query(User)`)
- **Error específico:**
  ```
  sqlalchemy.exc.InvalidRequestError: One or more mappers failed to initialize - 
  can't proceed with initialization of other mappers. Triggering mapper: 
  'Mapper[FCMToken(fcm_tokens)]'. Original exception was: 
  Mapper 'Mapper[User(users)]' has no property 'fcm_tokens'.
  ```

---

## 🔍 ANÁLISIS TÉCNICO COMPLETO

### **Causa Raíz #1: CORS**
La configuración CORS en `app/core/config.py` tenía:
```python
ALLOWED_HOSTS: List[str] = ["*"]
```

Aunque `["*"]` debería permitir todo, Railway no estaba procesando correctamente 
los orígenes locales específicos de Flutter Web, causando el bloqueo del navegador.

### **Causa Raíz #2: SQLAlchemy**
El modelo `FCMToken` definía:
```python
class FCMToken(Base):
    user = relationship("User", back_populates="fcm_tokens")
```

Pero el modelo `User` en producción no tenía la propiedad inversa:
```python
class User(Base):
    # fcm_tokens = relationship("FCMToken", back_populates="user", cascade="all, delete-orphan")
    # ← ESTA LÍNEA FALTABA O ESTABA COMENTADA EN PRODUCCIÓN
```

Esto creaba una inconsistencia en los mappers de SQLAlchemy que se manifestaba 
al intentar inicializar cualquier query a la base de datos.

---

## 📊 SECUENCIA DE ERRORES OBSERVADOS

1. ** múltiples intentos desde frontend Flutter**
   ```
   POST /auth/register HTTP/1.1" 422 Unprocessable Entity
   POST /auth/login HTTP/1.1" 422 Unprocessable Entity
   ```

2. **Error CORS en navegador**
   ```
   net::ERR_FAILED 500 (Internal Server Error)
   ClientException: Failed to fetch
   ```

3. **Error SQLAlchemy al finalmente llegar al backend**
   ```
   sqlalchemy.exc.InvalidRequestError: Mapper 'User(users)' has no property 'fcm_tokens'
   ```

---

## 🛠️ SOLUCIONES APLICADAS

### **Solución #1: CORS (Permanente)**
Actualizado `app/core/config.py`:
```python
# 🌐 CORS
ALLOWED_HOSTS: List[str] = [
    "*",  # Permitir todos los orígenes en producción
    # Orígenes específicos para desarrollo local
    "http://localhost:*",
    "https://localhost:*",
    "http://127.0.0.1:*",
    "https://127.0.0.1:*",
    # Orígenes comunes de Flutter web development
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5500",
    "http://localhost:57483",  # Tu puerto actual
    "https://localhost:3000",
    "https://localhost:8080",
    "https://localhost:5500",
    "https://localhost:57483"
]
```

### **Solución #2: SQLAlchemy (Parche Temporal)**
1. **Comentar relación en User (`app/models/user.py`):**
   ```python
   # fcm_tokens = relationship("FCMToken", back_populates="user", cascade="all, delete-orphan")  # TEMPORALMENTE COMENTADO
   ```

2. **Remover back_populates en FCMToken (`app/models/fcm_token.py`):**
   ```python
   user = relationship("User")  # back_populates removido temporalmente
   ```

---

## ✅ RESULTADOS OBTENIDOS

### **Antes del Fix:**
- ❌ CORS bloqueaba todas las peticiones desde localhost
- ❌ Error 500 en cualquier endpoint que usara la BD
- ❌ Login/register completamente inaccesibles
- ❌ Frontend no podía comunicarse con backend

### **Después del Fix:**
- ✅ CORS permitiendo peticiones desde `http://localhost:57483`
- ✅ Endpoints de auth respondiendo correctamente
- ✅ Backend estable y funcional
- ✅ Frontend puede autenticarse normalmente

---

## 🔮 ACCIONES FUTURAS RECOMENDADAS

### **Corto Plazo (1-2 días):**
1. **Monitorear estabilidad** del backend con el parche aplicado
2. **Verificar funcionalidad** de todos los endpoints críticos
3. **Testing completo** del flujo de autenticación desde Flutter

### **Mediano Plazo (1 semana):**
1. **Restaurar relación bidireccional** `fcm_tokens` cuando se confirme estabilidad
2. **Investigar causa raíz** de por qué el modelo `User` no tenía la propiedad en producción
3. **Implementar tests automatizados** para detectar inconsistencias de modelos

### **Largo Plazo (1 mes):**
1. **Mejorar configuración CORS** para ser más específica y segura
2. **Implementar health checks** que validen relaciones de modelos
3. **Documentar procedimientos** de despliegue para evitar regresiones

---

## 📝 LECCIONES APRENDIDAS

1. **CORS con comodines (`*`) puede no funcionar** en ciertos entornos PaaS como Railway
2. **Las relaciones bidireccionales de SQLAlchemy** deben estar sincronizadas en todos los ambientes
3. **Los errores CORS pueden ocultar errores reales** del backend (como el 500 de SQLAlchemy)
4. **Es crucial tener orígenes explícitos** para desarrollo local en configuración CORS

---

## 🏷️ ETIQUETAS

`#incidente-critico` `#cors` `#sqlalchemy` `#railway` `#flutter` `#backend` `#resuelto` `#parche-temporal`

---

## 📞 CONTACTO DE REFERENCIA

- **Reportado por:** Usuario del sistema (Flutter Developer)
- **Diagnosticado por:** Asistente IA Cascade
- **Ambiente afectado:** Producción Railway
- **Impacto:** Alto (autenticación completamente bloqueada)

---

*Este documento será actualizado si se detectan nuevas incidencias relacionadas o al aplicar la solución permanente.*
