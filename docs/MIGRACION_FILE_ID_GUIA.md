# 🔧 GUÍA DE MIGRACIÓN: Agregar columnas file_id

## ⚠️ PROBLEMA DETECTADO

```
ERROR: relation "pelea_eventos" does not exist
```

**Causa:** El nombre de la tabla es **`peleas_evento`** (singular), no `pelea_eventos` (plural).

---

## ✅ SOLUCIÓN: Nombres Correctos de Tablas

| Modelo | Tabla en BD | Campo a agregar |
|--------|-------------|-----------------|
| `Pelea` | `peleas` | `file_id` |
| `Tope` | `topes` | `file_id` |
| `PeleaEvento` | `peleas_evento` | `file_id` |
| `PagoPendiente` | `pagos_pendientes` | `comprobante_file_id` |

---

## 🚀 OPCIÓN 1: Script Python Automático (RECOMENDADO)

### Paso 1: Ejecutar script
```bash
python run_migration_file_id.py
```

### Paso 2: Confirmar
```
⚠️  IMPORTANTE: Esta migración agregará columnas a la base de datos
   Asegúrate de tener un backup antes de continuar

¿Deseas continuar? (si/no): si
```

### Paso 3: Verificar resultado
```
✅ MIGRACIÓN COMPLETADA EXITOSAMENTE

📊 Columnas agregadas:
   ✅ pagos_pendientes.comprobante_file_id (varchar, nullable=YES)
   ✅ peleas.file_id (varchar, nullable=YES)
   ✅ peleas_evento.file_id (varchar, nullable=YES)
   ✅ topes.file_id (varchar, nullable=YES)
```

---

## 🗄️ OPCIÓN 2: SQL Manual

### Conectar a tu base de datos:
```bash
# PostgreSQL
psql -U usuario -d nombre_base_datos

# MySQL
mysql -u usuario -p nombre_base_datos
```

### Ejecutar SQL:
```sql
-- 1. Peleas
ALTER TABLE peleas 
ADD COLUMN IF NOT EXISTS file_id VARCHAR(255);

-- 2. Topes
ALTER TABLE topes 
ADD COLUMN IF NOT EXISTS file_id VARCHAR(255);

-- 3. Peleas Evento (NOMBRE CORRECTO)
ALTER TABLE peleas_evento 
ADD COLUMN IF NOT EXISTS file_id VARCHAR(255);

-- 4. Pagos Pendientes
ALTER TABLE pagos_pendientes 
ADD COLUMN IF NOT EXISTS comprobante_file_id VARCHAR(255);
```

### Verificar:
```sql
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name IN ('peleas', 'topes', 'peleas_evento', 'pagos_pendientes')
  AND column_name IN ('file_id', 'comprobante_file_id')
ORDER BY table_name, column_name;
```

**Resultado esperado:**
```
table_name          | column_name           | data_type      | is_nullable
--------------------|-----------------------|----------------|-------------
pagos_pendientes    | comprobante_file_id   | varchar        | YES
peleas              | file_id               | varchar        | YES
peleas_evento       | file_id               | varchar        | YES
topes               | file_id               | varchar        | YES
```

---

## 🔄 ROLLBACK (Si algo sale mal)

### Script Python:
```python
# Editar run_migration_file_id.py y cambiar ADD por DROP
# O ejecutar manualmente:
```

### SQL Manual:
```sql
ALTER TABLE peleas DROP COLUMN IF EXISTS file_id;
ALTER TABLE topes DROP COLUMN IF EXISTS file_id;
ALTER TABLE peleas_evento DROP COLUMN IF EXISTS file_id;
ALTER TABLE pagos_pendientes DROP COLUMN IF EXISTS comprobante_file_id;
```

---

## 📋 CHECKLIST PRE-MIGRACIÓN

- [ ] **Backup de base de datos** realizado
- [ ] **Ambiente de desarrollo** (no producción)
- [ ] **Conexión a BD** verificada
- [ ] **Nombres de tablas** confirmados
- [ ] **Script de migración** revisado

---

## 🧪 TESTING POST-MIGRACIÓN

### 1. Verificar columnas:
```bash
python -c "
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'peleas' AND column_name = 'file_id'
    '''))
    print('✅ Columna existe' if result.fetchone() else '❌ Columna NO existe')
"
```

### 2. Probar API:
```bash
# Crear pelea con video
curl -X POST "http://localhost:8000/api/v1/peleas" \
  -H "Authorization: Bearer TOKEN" \
  -F "nombre=Test" \
  -F "video=@test.mp4"

# Verificar que file_id se guardó
curl "http://localhost:8000/api/v1/peleas/123" \
  -H "Authorization: Bearer TOKEN"
```

### 3. Verificar en BD:
```sql
SELECT id, video_url, file_id 
FROM peleas 
WHERE id = 123;
```

**Resultado esperado:**
```
id  | video_url                          | file_id
----|------------------------------------|---------
123 | https://ik.imagekit.io/video.mp4   | abc123xyz
```

---

## ❓ PREGUNTAS FRECUENTES

### ¿Por qué `peleas_evento` y no `pelea_eventos`?

El modelo usa `__tablename__ = "peleas_evento"` (singular). Siempre usa el nombre definido en el modelo.

### ¿Qué pasa con los registros existentes?

Las columnas se agregan con `NULL` por defecto. Los registros existentes tendrán `file_id = NULL` hasta que se actualicen.

### ¿Afecta al frontend?

**NO.** El `file_id` es interno del backend. El frontend sigue funcionando igual.

### ¿Puedo ejecutar la migración en producción?

**SÍ**, pero:
1. Haz backup primero
2. Ejecuta en horario de bajo tráfico
3. Prueba en desarrollo primero
4. Ten plan de rollback listo

---

## 📊 IMPACTO

### Base de Datos:
- ✅ 4 columnas nuevas
- ✅ Todas nullable (no rompe datos existentes)
- ✅ Sin índices (por ahora)
- ✅ Sin foreign keys

### Performance:
- ✅ Sin impacto (columnas simples)
- ✅ Sin locks largos
- ✅ Ejecución rápida (<1 segundo)

### Aplicación:
- ✅ Backend listo para usar file_id
- ✅ Frontend sin cambios
- ✅ APIs funcionan igual

---

**Documento creado:** 2025-11-15 11:25 AM
**Última actualización:** 2025-11-15 11:25 AM
**Estado:** ✅ Listo para ejecutar
