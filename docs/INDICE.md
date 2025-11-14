# 📋 ÍNDICE DE DOCUMENTACIÓN - GalloApp Backend

## 📁 Estructura Completa

```
docs/
├── README.md                           # 📚 Guía principal de documentación
├── incidentes/                         # 🚨 Registro de incidentes
│   ├── INCIDENTE_CORS_SQLALCHEMY_2025-11-13.md  # Último incidente crítico
│   ├── TEST_NOTIFICATIONS.md           # 📧 Issues con notificaciones
│   └── PLANTILLA_INCIDENTE.md          # 📝 Plantilla para nuevos incidentes
├── api/                                # 📡 Documentación de APIs
│   ├── API_MARKETPLACE_CURLS.md        # 🛒 Ejemplos Marketplace
│   ├── API_PELEAS_EVENTO.md            # 🥊 API de peleas de evento
│   └── API_PELEAS_EVENTO_CURLS.md      # 🥊 Ejemplos peleas de evento
└── deployments/                        # 🚀 Guías de deployment
    ├── API_MARKETPLACE_RAILWAY.md      # 🛒 Deploy Marketplace en Railway
    └── RAILWAY_ENV_VARIABLES.txt       # 🔧 Variables de entorno Railway
```

---

## 🚨 Incidentes Críticos Recientes

### **[2025-11-13] INCIDENTE CORS + SQLAlchemy**
- **Estado:** ✅ RESUELTO
- **Impacto:** Alto (autenticación bloqueada)
- **Solución:** Parche temporal + configuración CORS
- **Archivo:** `incidentes/INCIDENTE_CORS_SQLALCHEMY_2025-11-13.md`

---

## 📡 Documentación de APIs

### **Endpoints Principales**
| Categoría | Endpoint | Documentación |
|-----------|----------|---------------|
| 🔐 Auth | `/auth/*` | Ver en código fuente |
| 🐓 Gallos | `/api/v1/gallos/*` | Ver en código fuente |
| 👤 Perfiles | `/profiles/*` | Ver en código fuente |
| 🛒 Marketplace | `/api/v1/marketplace/*` | `api/API_MARKETPLACE_CURLS.md` |
| 🥊 Peleas Evento | `/api/v1/peleas-evento/*` | `api/API_PELEAS_EVENTO.md` |

### **Ejemplos de Uso**
- **Marketplace:** `api/API_MARKETPLACE_CURLS.md`
- **Peleas de Evento:** `api/API_PELEAS_EVENTO_CURLS.md`

---

## 🚀 Guías de Deployment

### **Railway PaaS**
- **Configuración:** `deployments/API_MARKETPLACE_RAILWAY.md`
- **Variables de Entorno:** `deployments/RAILWAY_ENV_VARIABLES.txt`

### **Procedimientos**
1. **Deploy Principal:** Push a main branch → Auto-deploy en Railway
2. **Variables:** Configurar en Railway dashboard
3. **Health Check:** `/health` endpoint

---

## 📝 Procedimientos de Documentación

### **Para Nuevo Incidente**
1. Copiar `incidentes/PLANTILLA_INCIDENTE.md`
2. Renombrar con formato: `INCIDENTE_[TIPO]_YYYY-MM-DD.md`
3. Completar todas las secciones
4. Actualizar este índice

### **Para Nueva API**
1. Crear archivo en `api/` con formato: `API_[NOMBRE].md`
2. Incluir: descripción, endpoints, ejemplos, errores comunes
3. Actualizar tabla de APIs en este índice

### **Para Nuevo Deployment**
1. Crear archivo en `deployments/` con formato: `[PLATAFORMA]_[SERVICIO].md`
2. Incluir: requisitos, configuración, pasos, troubleshooting
3. Actualizar sección de deployments en este índice

---

## 🔍 Búsqueda Rápida

### **Por Tipo de Error**
- **CORS:** Ver incidente 2025-11-13
- **SQLAlchemy:** Ver incidente 2025-11-13
- **Autenticación:** Ver incidente 2025-11-13
- **Notificaciones:** Ver `TEST_NOTIFICATIONS.md`

### **Por Servicio**
- **Auth:** Endpoints `/auth/*`
- **Marketplace:** `api/API_MARKETPLACE_*.md`
- **Peleas:** `api/API_PELEAS_*.md`
- **FCM:** Ver código fuente y tests

### **Por Plataforma**
- **Railway:** `deployments/*_RAILWAY.*`
- **Cloudinary:** Ver configuración en código
- **Firebase:** Ver notificaciones y tests

---

## 📞 Contacto para Documentación

- **Issues de Documentación:** Crear issue en repositorio
- **Incidentes Críticos:** Contactar al equipo de backend
- **Actualización de APIs:** Equipo de desarrollo
- **Problemas de Deployment:** Equipo DevOps

---

*Última actualización: 2025-11-13*  
*Mantenido por: Backend Team GalloApp*
