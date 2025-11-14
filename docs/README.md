# 📚 Documentación - GalloApp Backend

Bienvenido a la documentación central del backend de GalloApp. Aquí encontrarás toda la información técnica sobre incidentes, APIs, deployments y mejores prácticas.

---

## 📂 Estructura de Documentación

### 🔥 [**incidentes/**](./incidentes/)
Registro detallado de incidentes críticos y soluciones aplicadas:
- **INCIDENTE_CORS_SQLALCHEMY_2025-11-13.md** - Error CORS y SQLAlchemy en Railway
- Plantillas para futuros incidentes
- Análisis post-mortem y lecciones aprendidas

### 🚀 [**deployments/**](./deployments/)
Guías y procedimientos de despliegue:
- Configuración Railway
- Variables de entorno
- Procedimientos de deploy
- Health checks y monitoreo

### 📡 [**api/**](./api/)
Documentación técnica de APIs:
- Endpoints disponibles
- Schemas y modelos
- Ejemplos de uso
- Guías de integración

---

## 📋 Documentación Rápida

### 🔐 Endpoints Principales
- **Auth:** `/auth/login`, `/auth/register`, `/auth/refresh`
- **Gallos:** `/api/v1/gallos/*`
- **Perfiles:** `/profiles/*`
- **Notificaciones:** `/api/v1/notifications/*`

### 🛠️ Configuración Clave
- **Database:** PostgreSQL (Railway)
- **Storage:** Cloudinary
- **Auth:** JWT Tokens
- **Notifications:** Firebase FCM
- **Deploy:** Railway PaaS

### 🚨 Incidentes Recientes
Ver [incidentes/INCIDENTE_CORS_SQLALCHEMY_2025-11-13.md](./incidentes/INCIDENTE_CORS_SQLALCHEMY_2025-11-13.md) para el último incidente crítico resuelto.

---

## 📝 Convenciones de Documentación

### 📅 Formato de Incidentes
```
# 🚨 INCIDENTE: [Título]
## 📅 Fecha y Hora
## 🎯 Origen del Error
## 🔍 Análisis Técnico
## 🛠️ Soluciones Aplicadas
## ✅ Resultados
## 🔮 Acciones Futuras
```

### 📝 Formato de API
```
# 📡 [Endpoint]
## Descripción
## Parámetros
## Ejemplos
## Errores Comunes
```

---

## 🔄 Mantenimiento

### Actualización Semanal
- Revisar logs de incidentes
- Actualizar documentación de APIs
- Verificar procedimientos de deploy

### Actualización Mensual
- Análisis de tendencias de errores
- Actualización de arquitectura
- Revisión de seguridad

---

## 📞 Contacto

- **Backend Team:** Documentación técnica
- **DevOps:** Issues de deployment
- **Frontend Team:** Integración de APIs

---

*Última actualización: 2025-11-13*  
*Versión: 1.0.0*
