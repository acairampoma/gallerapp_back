# 📜 Scripts - GalloApp Backend

Esta carpeta contiene todos los scripts de utilidad, deployment y mantenimiento del sistema.

---

## 📂 Estructura de Scripts

### 🚀 **Scripts de Deployment**
- `deploy_epico.sh` - Script principal de deployment
- `deploy_fix.bat` - Script de deployment rápido (Windows)
- `commit_epico.sh` - Script para commits automáticos

### 🧪 **Scripts de Debug y Testing**
- `debug_raza_id.py` - Debug del campo raza_id
- `debug_peleas.py` - Debug de sistema de peleas
- `diagnose_imports.py` - Diagnóstico de imports
- `check_vacunas_db.py` - Verificación de vacunas en BD

### 🔧 **Scripts de Mantenimiento**
- `init_db.py` - Inicialización de base de datos
- `init_peleas_topes.py` - Inicialización de peleas y topes
- `update_passwords.py` - Actualización masiva de passwords
- `validate_syntax.py` - Validación de sintaxis Python

### 📸 **Scripts de Media**
- `subir_fotos.py` - Upload masivo de fotos a Cloudinary
- `subir_fotos.bat` - Upload masivo (Windows)

### 🔥 **Scripts de Tests**
- `test_firebase_api.bat` - Tests de Firebase
- `test_token.bat` - Tests de tokens JWT

### 🗄️ **Scripts SQL**
- `API_MARKETPLACE_TEST_DATA.sql` - Datos de prueba para Marketplace
- `MARKETPLACE_DATABASE_FIX.sql` - Fixes de base de datos Marketplace
- `MARKETPLACE_FINAL_SCRIPT.sql` - Script final de Marketplace
- `SUSCRIPCIONES_FIX.sql` - Fixes de sistema de suscripciones
- `SUSCRIPCIONES_NORMALIZED_FIX.sql` - Fixes normalizados de suscripciones
- `test_fcm_insert.sql` - Tests de inserción FCM

### 🔑 **Configuración**
- `serviceAccountKey.json` - Credenciales de Firebase
- `fix_imports.sh` - Fixes de imports (Linux/Mac)

---

## 🚀 Uso de Scripts

### **Deployment Principal**
```bash
# Linux/Mac
./scripts/deploy_epico.sh

# Windows
./scripts/deploy_fix.bat
```

### **Inicialización de BD**
```bash
python scripts/init_db.py
python scripts/init_peleas_topes.py
```

### **Debug de Issues**
```bash
python scripts/debug_raza_id.py
python scripts/debug_peleas.py
```

### **Validaciones**
```bash
python scripts/validate_syntax.py
python scripts/check_vacunas_db.py
```

---

## ⚠️ Precauciones

1. **Hacer backup** antes de ejecutar scripts SQL
2. **Test en ambiente staging** antes de producción
3. **Revisar variables de entorno** antes de deployment
4. **Documentar cambios** realizados por los scripts

---

## 📝 Agregar Nuevo Script

1. **Categorizar correctamente** (deployment, debug, mantenimiento, etc.)
2. **Documentar propósito y uso**
3. **Incluir manejo de errores**
4. **Probar en ambiente development**

---

*Última actualización: 2025-11-13*
