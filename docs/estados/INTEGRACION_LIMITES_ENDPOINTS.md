# 🔧 Guía de Integración - Validación de Límites en Endpoints Existentes

## 📋 Resumen
Esta guía muestra cómo integrar la validación de límites de suscripción en los endpoints existentes de gallos, topes, peleas y vacunas.

## 🛠️ Opción 1: Usando Decoradores (Recomendado)

### Ejemplo: Endpoint Crear Gallo

```python
# En app/api/v1/gallos.py
from app.middlewares.limite_middleware import validar_limite_gallos

@router.post("/", response_model=GalloResponse)
@validar_limite_gallos  # ← Agregar este decorator
async def crear_gallo(
    gallo_data: GalloCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # El middleware validará automáticamente el límite antes de ejecutar
    nuevo_gallo = Gallo(**gallo_data.dict(), user_id=current_user_id)
    db.add(nuevo_gallo)
    db.commit()
    return nuevo_gallo
```

### Ejemplo: Endpoint Crear Tope

```python
# En app/api/v1/topes.py
from app.middlewares.limite_middleware import validar_limite_topes

@router.post("/", response_model=TopeResponse)
@validar_limite_topes("gallo_id")  # ← Especificar parámetro del gallo_id
async def crear_tope(
    tope_data: TopeCreate,  # Debe incluir gallo_id
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    nuevo_tope = Tope(**tope_data.dict(), user_id=current_user_id)
    db.add(nuevo_tope)
    db.commit()
    return nuevo_tope
```

## 🛠️ Opción 2: Validación Manual en Endpoint

```python
from app.middlewares.limite_middleware import verificar_limite_antes_crear
from app.schemas.suscripcion import RecursoTipo

@router.post("/", response_model=PeleaResponse)
async def crear_pelea(
    pelea_data: PeleaCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Validar límite manualmente
    await verificar_limite_antes_crear(
        user_id=current_user_id,
        recurso_tipo=RecursoTipo.PELEAS,
        gallo_id=pelea_data.gallo_id,
        db=db
    )
    
    # Crear pelea si pasa la validación
    nueva_pelea = Pelea(**pelea_data.dict(), user_id=current_user_id)
    db.add(nueva_pelea)
    db.commit()
    return nueva_pelea
```

## 📱 Respuestas de Error para Flutter

Cuando se supera un límite, el endpoint devuelve **HTTP 402 Payment Required**:

```json
{
  "detail": {
    "detail": "Límite de gallos alcanzado (5/5)",
    "limite_info": {
      "recurso_tipo": "gallos",
      "limite_actual": 5,
      "cantidad_usada": 5,
      "plan_recomendado": "premium",
      "upgrade_disponible": true
    },
    "accion_requerida": "upgrade_plan"
  }
}
```

## 🚀 Flutter - Manejo de Respuestas

```dart
// En Flutter, manejar el error 402
try {
  await api.crearGallo(galloData);
} catch (e) {
  if (e.statusCode == 402) {
    // Mostrar popup de upgrade
    showUpgradeDialog(
      context: context,
      limiteInfo: e.data['limite_info'],
      planRecomendado: e.data['limite_info']['plan_recomendado']
    );
  }
}
```

## ⚡ Endpoints que Requieren Integración

### 1. Gallos
- `POST /api/v1/gallos/` ← Aplicar `@validar_limite_gallos`

### 2. Topes  
- `POST /api/v1/topes/` ← Aplicar `@validar_limite_topes()`

### 3. Peleas
- `POST /api/v1/peleas/` ← Aplicar `@validar_limite_peleas()`

### 4. Vacunas
- `POST /api/v1/vacunas/` ← Aplicar `@validar_limite_vacunas()`

## 🔍 Testing Manual

Puedes probar los límites:

1. **Crear usuario de prueba**
2. **Crear 5 gallos** (límite plan gratuito)
3. **Intentar crear el 6to gallo** → Debe devolver HTTP 402
4. **Upgrade a plan premium**
5. **Crear más gallos** → Debe funcionar

## 📊 Logs de Validación

El sistema generará logs como:
```
INFO: Validación de límite pasada para user 123, recurso gallos
WARNING: Usuario 123 alcanzó límite de topes para gallo 456
ERROR: Error en middleware de límites: ValidationError
```

## 🎯 Próximos Pasos

1. ✅ Aplicar decoradores en endpoints existentes
2. ✅ Actualizar schemas si es necesario
3. ✅ Probar con CURLs
4. ✅ Implementar en Flutter
5. ✅ Configurar push notifications para admins