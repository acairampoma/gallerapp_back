# 🛒 REFACTORIZACIÓN: Marketplace Service

## 🚨 PROBLEMA IDENTIFICADO

El archivo `marketplace.py` tiene **937 líneas** con SQL crudo y lógica de negocio mezclada en la capa API.

### Violaciones de Arquitectura:

1. ❌ **SQL RAW en endpoints** (líneas 78-206, 305-369, 703-746, 834-846)
2. ❌ **Lógica de negocio en API** (procesamiento de fotos, validaciones)
3. ❌ **Construcción dinámica de SQL** (riesgo de SQL injection)
4. ❌ **Código duplicado** (queries similares repetidas)
5. ❌ **Sin separación de responsabilidades**
6. ❌ **Difícil de testear**
7. ❌ **Difícil de mantener**

---

## 🎯 SOLUCIÓN: Crear MarketplaceService

### Estructura Propuesta:

```
app/services/
├── marketplace_service.py         # Servicio principal
├── marketplace_query_builder.py   # Constructor de queries (opcional)
└── marketplace_validator.py       # Validaciones de negocio
```

---

## 📋 PLAN DE REFACTORIZACIÓN

### FASE 1: Crear MarketplaceService Base

**Archivo:** `app/services/marketplace_service.py`

**Métodos a implementar:**

```python
class MarketplaceService:
    """Servicio para lógica de negocio del Marketplace"""
    
    # ========================================
    # PUBLICACIONES
    # ========================================
    
    @staticmethod
    def listar_publicaciones_publicas(
        db: Session,
        filtros: MarketplaceFiltros,
        current_user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Listar publicaciones públicas con filtros
        
        REEMPLAZA: marketplace.py líneas 34-283
        """
        pass
    
    @staticmethod
    def listar_mis_publicaciones(
        db: Session,
        user_id: int,
        estado: Optional[str] = None,
        estados: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Listar publicaciones del usuario
        
        REEMPLAZA: marketplace.py líneas 290-424
        """
        pass
    
    @staticmethod
    def crear_publicacion(
        db: Session,
        user_id: int,
        publicacion_data: MarketplacePublicacionCreate
    ) -> Dict[str, Any]:
        """
        Crear nueva publicación
        
        REEMPLAZA: marketplace.py líneas 427-517
        """
        pass
    
    @staticmethod
    def actualizar_publicacion(
        db: Session,
        publicacion_id: int,
        user_id: int,
        update_data: MarketplacePublicacionUpdate
    ) -> Dict[str, Any]:
        """
        Actualizar publicación existente
        
        REEMPLAZA: marketplace.py líneas 520-569
        """
        pass
    
    @staticmethod
    def eliminar_publicacion(
        db: Session,
        publicacion_id: int,
        user_id: int
    ) -> bool:
        """
        Eliminar publicación
        
        REEMPLAZA: marketplace.py líneas 572-617
        """
        pass
    
    # ========================================
    # FAVORITOS
    # ========================================
    
    @staticmethod
    def toggle_favorito(
        db: Session,
        user_id: int,
        publicacion_id: int
    ) -> Dict[str, Any]:
        """
        Marcar/desmarcar favorito
        
        REEMPLAZA: marketplace.py líneas 624-687
        """
        pass
    
    @staticmethod
    def listar_favoritos(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Listar favoritos del usuario
        
        REEMPLAZA: marketplace.py líneas 690-791
        """
        pass
    
    # ========================================
    # VALIDACIONES Y LÍMITES
    # ========================================
    
    @staticmethod
    def verificar_limites_marketplace(
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Verificar límites del plan del usuario
        
        REEMPLAZA: función auxiliar en marketplace.py
        """
        pass
    
    @staticmethod
    def obtener_estadisticas(db: Session) -> Dict[str, Any]:
        """
        Estadísticas generales del marketplace
        
        REEMPLAZA: marketplace.py líneas 824-891
        """
        pass
    
    # ========================================
    # HELPERS PRIVADOS
    # ========================================
    
    @staticmethod
    def _procesar_fotos_gallo(fotos_json: Any) -> List[Dict]:
        """Procesar JSON de fotos del gallo"""
        pass
    
    @staticmethod
    def _construir_query_publicaciones(
        filtros: MarketplaceFiltros,
        user_id: Optional[int] = None,
        solo_mis_publicaciones: bool = False
    ) -> Tuple[str, Dict]:
        """Construir query dinámico con filtros"""
        pass
    
    @staticmethod
    def _aplicar_ordenamiento(
        query: str,
        ordenar_por: str
    ) -> str:
        """Aplicar ordenamiento al query"""
        pass
```

---

### FASE 2: Usar SQLAlchemy ORM en lugar de SQL RAW

**Antes (SQL RAW):**
```python
# ❌ MALO - SQL crudo
query = """
SELECT mp.id, mp.precio, g.nombre
FROM marketplace_publicaciones mp
INNER JOIN gallos g ON mp.gallo_id = g.id
WHERE mp.estado = :estado
"""
results = db.execute(text(query), {"estado": "venta"}).fetchall()
```

**Después (ORM):**
```python
# ✅ BUENO - SQLAlchemy ORM
from sqlalchemy.orm import joinedload

publicaciones = db.query(MarketplacePublicacion)\
    .join(Gallo, MarketplacePublicacion.gallo_id == Gallo.id)\
    .filter(MarketplacePublicacion.estado == "venta")\
    .options(joinedload(MarketplacePublicacion.gallo))\
    .all()
```

**Ventajas:**
- ✅ Type-safe
- ✅ Previene SQL injection
- ✅ Más fácil de testear
- ✅ Mejor manejo de relaciones
- ✅ Código más limpio

---

### FASE 3: Refactorizar Endpoints

**Antes (marketplace.py líneas 34-283):**
```python
@router.get("/publicaciones")
async def listar_publicaciones_publicas(
    precio_min: Optional[Decimal] = Query(None),
    precio_max: Optional[Decimal] = Query(None),
    # ... 20 parámetros más
    db: Session = Depends(get_db)
):
    # 250 LÍNEAS DE LÓGICA AQUÍ
    base_query = """SELECT ..."""
    # Construcción dinámica de SQL
    # Procesamiento de resultados
    # etc.
```

**Después (LIMPIO):**
```python
@router.get("/publicaciones")
async def listar_publicaciones_publicas(
    filtros: MarketplaceFiltros = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user_id: Optional[int] = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🛒 Listar publicaciones públicas"""
    try:
        resultado = MarketplaceService.listar_publicaciones_publicas(
            db=db,
            filtros=filtros,
            current_user_id=current_user_id,
            skip=skip,
            limit=limit
        )
        
        return {
            "success": True,
            "data": resultado
        }
        
    except Exception as e:
        logger.error(f"Error listando publicaciones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
```

**Reducción:** De 250 líneas a ~20 líneas por endpoint

---

## 📊 COMPARACIÓN ANTES/DESPUÉS

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Líneas en API | 937 | ~200 | -78% |
| Líneas en Service | 0 | ~500 | +500 |
| SQL RAW | 5 queries | 0 | -100% |
| Lógica en API | Sí | No | ✅ |
| Testeable | Difícil | Fácil | ✅ |
| Mantenible | No | Sí | ✅ |
| Type-safe | No | Sí | ✅ |

---

## 🔧 IMPLEMENTACIÓN PASO A PASO

### Paso 1: Crear MarketplaceService (1 día)
- [ ] Crear archivo `marketplace_service.py`
- [ ] Implementar método `listar_publicaciones_publicas()`
- [ ] Implementar método `listar_mis_publicaciones()`
- [ ] Implementar método `crear_publicacion()`
- [ ] Implementar método `actualizar_publicacion()`
- [ ] Implementar método `eliminar_publicacion()`

### Paso 2: Migrar Favoritos (0.5 días)
- [ ] Implementar `toggle_favorito()`
- [ ] Implementar `listar_favoritos()`

### Paso 3: Migrar Validaciones (0.5 días)
- [ ] Implementar `verificar_limites_marketplace()`
- [ ] Implementar `obtener_estadisticas()`

### Paso 4: Refactorizar Endpoints (1 día)
- [ ] Actualizar endpoint `/publicaciones`
- [ ] Actualizar endpoint `/mis-publicaciones`
- [ ] Actualizar endpoint POST `/publicaciones`
- [ ] Actualizar endpoint PUT `/publicaciones/{id}`
- [ ] Actualizar endpoint DELETE `/publicaciones/{id}`
- [ ] Actualizar endpoints de favoritos
- [ ] Actualizar endpoints de límites

### Paso 5: Testing (0.5 días)
- [ ] Tests unitarios del service
- [ ] Tests de integración de endpoints
- [ ] Validar que todo funciona igual

### Paso 6: Documentación (0.5 días)
- [ ] Documentar MarketplaceService
- [ ] Actualizar README si es necesario

**TOTAL ESTIMADO: 4 días**

---

## 🎯 BENEFICIOS ESPERADOS

### Técnicos:
1. ✅ **Separación de responsabilidades** (API vs Service)
2. ✅ **Código más limpio y mantenible**
3. ✅ **Más fácil de testear** (unit tests del service)
4. ✅ **Type-safe** con SQLAlchemy ORM
5. ✅ **Prevención de SQL injection**
6. ✅ **Reutilización de código**

### De Negocio:
1. ✅ **Más rápido agregar features**
2. ✅ **Menos bugs**
3. ✅ **Más fácil onboarding de nuevos devs**
4. ✅ **Mejor performance** (queries optimizados)

---

## 📝 EJEMPLO DE REFACTORIZACIÓN

### ANTES (marketplace.py líneas 427-517):

```python
@router.post("/publicaciones", response_model=Dict[str, Any])
async def crear_publicacion(
    publicacion: MarketplacePublicacionCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        # 1. Verificar que el gallo existe y pertenece al usuario
        gallo_query = text("""
            SELECT id, nombre, codigo_identificacion
            FROM gallos
            WHERE id = :gallo_id AND user_id = :user_id
        """)
        gallo_result = db.execute(gallo_query, {
            "gallo_id": publicacion.gallo_id,
            "user_id": current_user_id
        }).first()
        
        if not gallo_result:
            raise HTTPException(404, "Gallo no encontrado")
        
        # 2. Verificar límites del plan
        limites = await verificar_limites_marketplace(current_user_id, db)
        if not limites["puede_publicar"]:
            raise HTTPException(403, "Límite alcanzado")
        
        # 3. Verificar que el gallo no esté ya publicado
        existe_query = text("""
            SELECT COUNT(*) as count
            FROM marketplace_publicaciones
            WHERE gallo_id = :gallo_id AND estado = 'venta'
        """)
        existe_result = db.execute(existe_query, {"gallo_id": publicacion.gallo_id}).first()
        if existe_result.count > 0:
            raise HTTPException(400, "Gallo ya publicado")
        
        # 4. Crear la publicación
        nueva_publicacion = MarketplacePublicacion(
            user_id=current_user_id,
            gallo_id=publicacion.gallo_id,
            precio=publicacion.precio,
            estado=publicacion.estado,
            icono_ejemplo=publicacion.icono_ejemplo,
            created_by=current_user_id,
            updated_by=current_user_id
        )
        
        db.add(nueva_publicacion)
        db.commit()
        db.refresh(nueva_publicacion)
        
        return {
            "success": True,
            "message": "Publicación creada",
            "data": {...}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, str(e))
```

### DESPUÉS (LIMPIO):

**marketplace.py (endpoint):**
```python
@router.post("/publicaciones", response_model=Dict[str, Any])
async def crear_publicacion(
    publicacion: MarketplacePublicacionCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🛒 Crear nueva publicación"""
    try:
        resultado = MarketplaceService.crear_publicacion(
            db=db,
            user_id=current_user_id,
            publicacion_data=publicacion
        )
        
        return {
            "success": True,
            "message": "Publicación creada exitosamente",
            "data": resultado
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error creando publicación: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**marketplace_service.py (lógica):**
```python
@staticmethod
def crear_publicacion(
    db: Session,
    user_id: int,
    publicacion_data: MarketplacePublicacionCreate
) -> Dict[str, Any]:
    """Crear nueva publicación en el marketplace"""
    
    # 1. Verificar que el gallo existe y pertenece al usuario
    gallo = db.query(Gallo).filter(
        Gallo.id == publicacion_data.gallo_id,
        Gallo.user_id == user_id
    ).first()
    
    if not gallo:
        raise ValueError("Gallo no encontrado o no tienes permisos")
    
    # 2. Verificar límites del plan
    limites = MarketplaceService.verificar_limites_marketplace(db, user_id)
    if not limites["puede_publicar"]:
        raise PermissionError(
            f"Has alcanzado el límite de {limites['publicaciones_permitidas']} "
            f"publicaciones de tu plan {limites['plan_nombre']}"
        )
    
    # 3. Verificar que el gallo no esté ya publicado
    existe_publicacion = db.query(MarketplacePublicacion).filter(
        MarketplacePublicacion.gallo_id == publicacion_data.gallo_id,
        MarketplacePublicacion.estado == 'venta'
    ).first()
    
    if existe_publicacion:
        raise ValueError("Este gallo ya tiene una publicación activa")
    
    # 4. Crear la publicación
    nueva_publicacion = MarketplacePublicacion(
        user_id=user_id,
        gallo_id=publicacion_data.gallo_id,
        precio=publicacion_data.precio,
        estado=publicacion_data.estado,
        icono_ejemplo=publicacion_data.icono_ejemplo,
        created_by=user_id,
        updated_by=user_id
    )
    
    db.add(nueva_publicacion)
    db.commit()
    db.refresh(nueva_publicacion)
    
    logger.info(f"✅ Publicación creada: ID {nueva_publicacion.id} para gallo {gallo.nombre}")
    
    return {
        "publicacion_id": nueva_publicacion.id,
        "gallo_nombre": gallo.nombre,
        "precio": float(nueva_publicacion.precio),
        "estado": nueva_publicacion.estado,
        "fecha_publicacion": nueva_publicacion.fecha_publicacion.isoformat()
    }
```

---

## ✅ CHECKLIST DE REFACTORIZACIÓN

### Preparación:
- [ ] Crear branch `refactor/marketplace-service`
- [ ] Backup de `marketplace.py` actual
- [ ] Crear tests para comportamiento actual

### Implementación:
- [ ] Crear `marketplace_service.py`
- [ ] Migrar lógica de publicaciones
- [ ] Migrar lógica de favoritos
- [ ] Migrar validaciones y límites
- [ ] Actualizar endpoints
- [ ] Eliminar código duplicado

### Testing:
- [ ] Tests unitarios del service
- [ ] Tests de integración
- [ ] Validar con Postman/curl
- [ ] Performance testing

### Documentación:
- [ ] Documentar MarketplaceService
- [ ] Actualizar README
- [ ] Comentarios en código

### Deploy:
- [ ] Code review
- [ ] Merge a develop
- [ ] Deploy a staging
- [ ] Validar en staging
- [ ] Deploy a producción

---

## 🎓 LECCIONES APRENDIDAS

### ❌ **NO HACER:**
1. SQL RAW en endpoints
2. Lógica de negocio en API
3. Construcción dinámica de SQL con strings
4. Código duplicado
5. Endpoints de 200+ líneas

### ✅ **SÍ HACER:**
1. Usar SQLAlchemy ORM
2. Separar lógica en Services
3. Endpoints delgados (thin controllers)
4. Reutilizar código
5. Type hints y validaciones

---

**Documento creado:** 2025-11-15
**Última actualización:** 2025-11-15
**Estado:** 📋 Plan de refactorización completo
**Prioridad:** 🔴 ALTA (deuda técnica crítica)
