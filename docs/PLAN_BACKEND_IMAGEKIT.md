# 🚀 Plan de Tareas Backend - ImageKit y Suscripciones

## 📋 Resumen Ejecutivo

Este documento detalla todas las tareas de **BACKEND** necesarias para:
1. Migrar de Cloudinary a ImageKit
2. Mejorar sistema de suscripciones
3. Implementar control de cuotas por plan
4. Agregar tracking de movimientos

---

## 🎯 FASE 1: Configuración de ImageKit

### Tarea 1.1: Configurar credenciales ImageKit
**Prioridad:** 🔴 CRÍTICA

**Archivos a modificar:**
- `app/core/config.py`
- `.env`

**Cambios:**
```python
# app/core/config.py
class Settings(BaseSettings):
    # 📸 ImageKit Configuration
    IMAGEKIT_PUBLIC_KEY: str = config("IMAGEKIT_PUBLIC_KEY")
    IMAGEKIT_PRIVATE_KEY: str = config("IMAGEKIT_PRIVATE_KEY")
    IMAGEKIT_URL_ENDPOINT: str = config("IMAGEKIT_URL_ENDPOINT")
    IMAGEKIT_FOLDER_GALLOS: str = "gallos"
    IMAGEKIT_FOLDER_PELEAS: str = "peleas"
    IMAGEKIT_FOLDER_TOPES: str = "topes"
    IMAGEKIT_FOLDER_MARKETPLACE: str = "marketplace"
    IMAGEKIT_FOLDER_COMPROBANTES: str = "comprobantes"
```

**Variables de entorno (.env):**
```env
IMAGEKIT_PUBLIC_KEY=public_xxx
IMAGEKIT_PRIVATE_KEY=private_xxx
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/tu_id
```

---

### Tarea 1.2: Expandir servicio ImageKit existente
**Prioridad:** 🔴 CRÍTICA

**Archivo existente:** `app/services/imagekit_service.py` ✅

**Estado actual:**
- ✅ Ya existe servicio para **videos** (usado en peleas_evento)
- ✅ Métodos: `upload_video()`, `delete_video()`
- ✅ Configuración con credenciales de settings
- ✅ Manejo de errores y logging

**Implementación actual:**
```python
class ImageKitService:
    def __init__(self):
        self.imagekit = ImageKit(
            private_key=settings.IMAGEKIT_PRIVATE_KEY,
            public_key=settings.IMAGEKIT_PUBLIC_KEY,
            url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
        )
    
    def upload_video(
        self, file_content: bytes, file_name: str, folder: str
    ) -> Optional[Dict[str, Any]]:
        """✅ YA IMPLEMENTADO - Subir video a ImageKit"""
        # Convierte a base64 y sube
        # Retorna: url, file_id, thumbnail_url, file_path
    
    def delete_video(self, file_id: str) -> bool:
        """✅ YA IMPLEMENTADO - Eliminar video de ImageKit"""
```

**Funcionalidades a AGREGAR:**
```python
# NUEVOS MÉTODOS PARA IMÁGENES

def upload_image(
    self, 
    file_content: bytes, 
    file_name: str,
    folder: str = "gallos"
) -> Optional[Dict[str, Any]]:
    """🆕 Upload imagen a ImageKit (similar a upload_video)"""
    pass

def upload_multiple_images(
    self,
    files_data: List[Tuple[bytes, str]],  # (content, filename)
    folder: str
) -> List[Dict[str, Any]]:
    """🆕 Upload múltiples imágenes"""
    pass

def delete_image(self, file_id: str) -> bool:
    """🆕 Eliminar imagen (alias de delete_video)"""
    return self.delete_video(file_id)  # Mismo método

def get_optimized_url(
    self,
    url: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    quality: int = 80
) -> str:
    """🆕 Generar URL optimizada con transformaciones"""
    # ImageKit permite transformaciones en URL
    # Ejemplo: https://ik.imagekit.io/demo/tr:w-400,h-300,q-80/image.jpg
    pass

def get_thumbnail_url(self, url: str, size: int = 200) -> str:
    """🆕 Generar thumbnail"""
    return self.get_optimized_url(url, width=size, height=size)
```

**Patrón de uso (basado en peleas_evento.py):**
```python
# CREAR PELEA CON VIDEO (líneas 228-260)
if video:
    video_content = await video.read()
    upload_result = imagekit_service.upload_video(
        file_content=video_content,
        file_name=f"pelea_{pelea.id}_{timestamp}_{video.filename}",
        folder=f"eventos_peleas/evento_{evento_id}"
    )
    
    if upload_result:
        pelea.video_url = upload_result.get('url')
        pelea.thumbnail_pelea_url = upload_result.get('thumbnail_url')
        pelea.estado_video = 'disponible'
```

**Aplicar mismo patrón para imágenes de gallos:**
```python
# CREAR GALLO CON IMÁGENES
if imagenes:
    for idx, imagen in enumerate(imagenes):
        imagen_content = await imagen.read()
        upload_result = imagekit_service.upload_image(
            file_content=imagen_content,
            file_name=f"gallo_{gallo.id}_{idx}_{imagen.filename}",
            folder=f"gallos/usuario_{user_id}"
        )
        
        if upload_result:
            gallo_imagen = GalloImagen(
                gallo_id=gallo.id,
                url=upload_result.get('url'),
                file_id=upload_result.get('file_id'),
                orden=idx,
                es_principal=(idx == 0)
            )
            db.add(gallo_imagen)
```

---

## 🎯 FASE 2: Migración de Modelos de Datos

### Tarea 2.1: Actualizar modelo GalloSimple
**Prioridad:** 🔴 CRÍTICA

**Archivo:** `app/models/gallo_simple.py`

**Cambios:**
```python
class GalloSimple(Base):
    # ... campos existentes ...
    
    # 📸 Imágenes con ImageKit
    foto_principal = Column(String(500))  # URL de ImageKit
    imagenes = relationship("GalloImagen", back_populates="gallo", cascade="all, delete-orphan")

class GalloImagen(Base):
    """Tabla para múltiples imágenes por gallo"""
    __tablename__ = "gallo_imagenes"
    
    id = Column(Integer, primary_key=True)
    gallo_id = Column(Integer, ForeignKey("gallos_simples.id", ondelete="CASCADE"))
    url = Column(String(500), nullable=False)  # URL de ImageKit
    file_id = Column(String(255))  # ID de ImageKit para eliminar
    orden = Column(Integer, default=0)  # Orden en carrusel
    es_principal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    gallo = relationship("GalloSimple", back_populates="imagenes")
```

**Migración Alembic:**
```bash
alembic revision --autogenerate -m "add gallo_imagenes table with imagekit support"
```

---

### Tarea 2.2: Actualizar modelo Pelea
**Prioridad:** 🟡 IMPORTANTE

**Archivo:** `app/models/pelea.py`

**Cambios:**
```python
class Pelea(Base):
    # ... campos existentes ...
    imagenes = relationship("PeleaImagen", back_populates="pelea", cascade="all, delete-orphan")

class PeleaImagen(Base):
    __tablename__ = "pelea_imagenes"
    
    id = Column(Integer, primary_key=True)
    pelea_id = Column(Integer, ForeignKey("peleas.id", ondelete="CASCADE"))
    url = Column(String(500), nullable=False)
    file_id = Column(String(255))
    orden = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    
    pelea = relationship("Pelea", back_populates="imagenes")
```

---

### Tarea 2.3: Actualizar modelo Tope
**Prioridad:** 🟡 IMPORTANTE

**Archivo:** `app/models/tope.py`

**Similar a Pelea:**
```python
class TopeImagen(Base):
    __tablename__ = "tope_imagenes"
    # ... mismo esquema que PeleaImagen
```

---

## 🎯 FASE 3: Endpoints de ImageKit

### Tarea 3.1: Endpoint de upload múltiple
**Prioridad:** 🔴 CRÍTICA

**Archivo:** `app/api/v1/imagekit.py` (nuevo)

```python
@router.post("/upload-images")
async def upload_images(
    files: List[UploadFile],
    folder: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """📸 Upload múltiples imágenes a ImageKit"""
    
    # Validar cuota de suscripción
    suscripcion = get_user_suscripcion(db, current_user.id)
    if not puede_subir_imagenes(suscripcion, len(files)):
        raise HTTPException(400, "Límite de imágenes alcanzado")
    
    # Upload a ImageKit
    imagekit = ImageKitService()
    results = await imagekit.upload_multiple_images(files, folder)
    
    return {
        "success": True,
        "images": results,
        "message": f"{len(results)} imágenes subidas exitosamente"
    }
```

---

### Tarea 3.2: Endpoint de eliminación
**Prioridad:** 🟡 IMPORTANTE

```python
@router.delete("/delete-image/{file_id}")
async def delete_image(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """🗑️ Eliminar imagen de ImageKit"""
    
    imagekit = ImageKitService()
    success = await imagekit.delete_image(file_id)
    
    return {
        "success": success,
        "message": "Imagen eliminada" if success else "Error eliminando imagen"
    }
```

---

## 🎯 FASE 4: Sistema de Suscripciones

### Tarea 4.1: Crear tabla de movimientos
**Prioridad:** 🔴 CRÍTICA

**Archivo:** `app/models/suscripcion_movimiento.py` (nuevo)

```python
class SuscripcionMovimiento(Base):
    """Auditoría de movimientos de suscripciones"""
    __tablename__ = "suscripcion_movimientos"
    
    id = Column(Integer, primary_key=True)
    suscripcion_id = Column(Integer, ForeignKey("suscripciones.id"))
    usuario_id = Column(Integer, ForeignKey("users.id"))
    tipo_movimiento = Column(String(50))  # creacion, renovacion, cancelacion, expiracion
    plan_anterior_id = Column(Integer, ForeignKey("planes_catalogo.id"))
    plan_nuevo_id = Column(Integer, ForeignKey("planes_catalogo.id"))
    fecha_movimiento = Column(DateTime, default=func.now())
    detalles = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    
    suscripcion = relationship("Suscripcion")
    usuario = relationship("User")
    plan_anterior = relationship("PlanCatalogo", foreign_keys=[plan_anterior_id])
    plan_nuevo = relationship("PlanCatalogo", foreign_keys=[plan_nuevo_id])
```

**Migración:**
```bash
alembic revision --autogenerate -m "add suscripcion_movimientos table"
```

---

### Tarea 4.2: Crear tabla de límites por plan
**Prioridad:** 🔴 CRÍTICA

**Archivo:** `app/models/plan_limite.py` (nuevo)

```python
class PlanLimite(Base):
    """Límites y features por plan"""
    __tablename__ = "plan_limites"
    
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("planes_catalogo.id"), unique=True)
    
    # Límites de contenido
    max_gallos = Column(Integer, default=5)
    max_peleas_mes = Column(Integer, default=10)
    max_topes_mes = Column(Integer, default=10)
    max_imagenes_por_gallo = Column(Integer, default=3)
    max_favoritos = Column(Integer, default=10)
    
    # Features booleanos
    acceso_marketplace = Column(Boolean, default=False)
    acceso_transmisiones = Column(Boolean, default=False)
    acceso_reportes_avanzados = Column(Boolean, default=False)
    soporte_prioritario = Column(Boolean, default=False)
    sin_watermark = Column(Boolean, default=False)
    
    # Relación
    plan = relationship("PlanCatalogo", back_populates="limites")
```

---

### Tarea 4.3: Endpoints de suscripciones
**Prioridad:** 🔴 CRÍTICA

**Archivo:** `app/api/v1/suscripciones.py`

**Endpoints a crear/mejorar:**

```python
@router.get("/mi-suscripcion")
async def get_mi_suscripcion(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """📊 Obtener suscripción actual del usuario"""
    suscripcion = db.query(Suscripcion).filter(
        Suscripcion.usuario_id == current_user.id,
        Suscripcion.estado == "activa"
    ).first()
    
    if not suscripcion:
        # Crear suscripción gratuita por defecto
        suscripcion = crear_suscripcion_gratuita(db, current_user.id)
    
    return {
        "suscripcion": suscripcion,
        "plan": suscripcion.plan,
        "limites": suscripcion.plan.limites,
        "dias_restantes": (suscripcion.fecha_fin - datetime.now()).days
    }

@router.get("/cuota-disponible")
async def get_cuota_disponible(
    recurso: str,  # gallos, peleas, imagenes, etc.
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """📈 Obtener cuota disponible de un recurso"""
    suscripcion = get_user_suscripcion(db, current_user.id)
    limites = suscripcion.plan.limites
    
    if recurso == "gallos":
        usado = db.query(GalloSimple).filter(
            GalloSimple.usuario_id == current_user.id
        ).count()
        return {
            "usado": usado,
            "limite": limites.max_gallos,
            "disponible": limites.max_gallos - usado,
            "porcentaje": (usado / limites.max_gallos) * 100
        }
    
    # Similar para otros recursos...

@router.post("/validar-acceso")
async def validar_acceso(
    feature: str,  # marketplace, transmisiones, etc.
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """🔐 Validar si el usuario tiene acceso a una feature"""
    suscripcion = get_user_suscripcion(db, current_user.id)
    limites = suscripcion.plan.limites
    
    tiene_acceso = getattr(limites, f"acceso_{feature}", False)
    
    return {
        "tiene_acceso": tiene_acceso,
        "plan_actual": suscripcion.plan.nombre,
        "requiere_upgrade": not tiene_acceso
    }

@router.get("/historial")
async def get_historial_movimientos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """📜 Historial de movimientos de suscripción"""
    movimientos = db.query(SuscripcionMovimiento).filter(
        SuscripcionMovimiento.usuario_id == current_user.id
    ).order_by(SuscripcionMovimiento.fecha_movimiento.desc()).all()
    
    return {
        "movimientos": movimientos,
        "total": len(movimientos)
    }
```

---

## 🎯 FASE 5: Servicios de Validación

### Tarea 5.1: Servicio de validación de cuotas
**Prioridad:** 🔴 CRÍTICA

**Archivo:** `app/services/cuota_service.py` (nuevo)

```python
class CuotaService:
    @staticmethod
    def puede_crear_gallo(db: Session, user_id: int) -> Tuple[bool, str]:
        """Validar si puede crear un gallo"""
        suscripcion = get_user_suscripcion(db, user_id)
        limites = suscripcion.plan.limites
        
        gallos_actuales = db.query(GalloSimple).filter(
            GalloSimple.usuario_id == user_id
        ).count()
        
        if gallos_actuales >= limites.max_gallos:
            return False, f"Límite de {limites.max_gallos} gallos alcanzado. Mejora tu plan."
        
        return True, "OK"
    
    @staticmethod
    def puede_subir_imagenes(
        db: Session, 
        user_id: int, 
        gallo_id: int,
        cantidad: int
    ) -> Tuple[bool, str]:
        """Validar si puede subir más imágenes"""
        suscripcion = get_user_suscripcion(db, user_id)
        limites = suscripcion.plan.limites
        
        imagenes_actuales = db.query(GalloImagen).filter(
            GalloImagen.gallo_id == gallo_id
        ).count()
        
        if imagenes_actuales + cantidad > limites.max_imagenes_por_gallo:
            return False, f"Límite de {limites.max_imagenes_por_gallo} imágenes por gallo alcanzado"
        
        return True, "OK"
    
    @staticmethod
    def puede_acceder_marketplace(db: Session, user_id: int) -> Tuple[bool, str]:
        """Validar acceso a marketplace"""
        suscripcion = get_user_suscripcion(db, user_id)
        
        if not suscripcion.plan.limites.acceso_marketplace:
            return False, "Marketplace requiere plan Premium o superior"
        
        return True, "OK"
```

---

## 🎯 FASE 6: Migración de Datos

### Tarea 6.1: Script de migración de imágenes
**Prioridad:** 🟡 IMPORTANTE

**Archivo:** `scripts/migrate_images_to_imagekit.py` (nuevo)

```python
async def migrate_cloudinary_to_imagekit():
    """Migrar imágenes de Cloudinary a ImageKit"""
    
    db = SessionLocal()
    imagekit = ImageKitService()
    
    try:
        # 1. Migrar gallos
        gallos = db.query(GalloSimple).all()
        for gallo in gallos:
            if gallo.foto_principal and "cloudinary" in gallo.foto_principal:
                # Descargar de Cloudinary
                response = requests.get(gallo.foto_principal)
                
                # Subir a ImageKit
                result = await imagekit.upload_image(
                    file=response.content,
                    folder="gallos",
                    file_name=f"gallo_{gallo.id}"
                )
                
                # Actualizar BD
                gallo.foto_principal = result["url"]
                db.commit()
                
                print(f"✅ Gallo {gallo.id} migrado")
        
        # 2. Similar para peleas, topes, etc.
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()
```

---

## 🎯 FASE 7: Actualizar Endpoints Existentes

### Tarea 7.1: Actualizar endpoint de creación de gallo
**Prioridad:** 🔴 CRÍTICA

**Archivo:** `app/api/v1/gallos_con_pedigri.py`

**Cambios:**
```python
@router.post("/gallos")
async def create_gallo(
    # ... parámetros existentes ...
    imagenes: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """🐓 Crear gallo con imágenes en ImageKit"""
    
    # 1. Validar cuota de gallos
    puede, mensaje = CuotaService.puede_crear_gallo(db, current_user.id)
    if not puede:
        raise HTTPException(400, mensaje)
    
    # 2. Validar cuota de imágenes
    if imagenes:
        puede, mensaje = CuotaService.puede_subir_imagenes(
            db, current_user.id, None, len(imagenes)
        )
        if not puede:
            raise HTTPException(400, mensaje)
    
    # 3. Crear gallo
    gallo = GalloSimple(...)
    db.add(gallo)
    db.commit()
    
    # 4. Subir imágenes a ImageKit
    if imagenes:
        imagekit = ImageKitService()
        for idx, imagen in enumerate(imagenes):
            result = await imagekit.upload_image(
                file=imagen,
                folder="gallos",
                file_name=f"gallo_{gallo.id}_{idx}"
            )
            
            # Guardar en BD
            gallo_imagen = GalloImagen(
                gallo_id=gallo.id,
                url=result["url"],
                file_id=result["fileId"],
                orden=idx,
                es_principal=(idx == 0)
            )
            db.add(gallo_imagen)
        
        db.commit()
    
    return {"success": True, "gallo": gallo}
```

---

## 📊 Resumen de Cambios en BD

### Nuevas Tablas
1. ✅ `gallo_imagenes` - Múltiples imágenes por gallo
2. ✅ `pelea_imagenes` - Múltiples imágenes por pelea
3. ✅ `tope_imagenes` - Múltiples imágenes por tope
4. ✅ `suscripcion_movimientos` - Auditoría de suscripciones
5. ✅ `plan_limites` - Límites y features por plan

### Tablas a Modificar
1. `gallos_simples` - Agregar relación con `gallo_imagenes`
2. `peleas` - Agregar relación con `pelea_imagenes`
3. `topes` - Agregar relación con `tope_imagenes`
4. `planes_catalogo` - Agregar relación con `plan_limites`

---

## 🔧 Configuración Inicial

### 1. Instalar dependencias
```bash
pip install imagekitio
```

### 2. Crear datos iniciales de planes
```python
# scripts/seed_plan_limites.py
def seed_plan_limites():
    db = SessionLocal()
    
    # Plan Gratuito
    PlanLimite(
        plan_id=1,  # ID del plan gratuito
        max_gallos=5,
        max_peleas_mes=10,
        max_topes_mes=10,
        max_imagenes_por_gallo=3,
        acceso_marketplace=False,
        acceso_transmisiones=False
    )
    
    # Plan Básico
    PlanLimite(
        plan_id=2,
        max_gallos=20,
        max_peleas_mes=50,
        max_imagenes_por_gallo=5,
        acceso_marketplace=True
    )
    
    # Plan Premium
    PlanLimite(
        plan_id=3,
        max_gallos=50,
        max_peleas_mes=200,
        max_imagenes_por_gallo=10,
        acceso_marketplace=True,
        acceso_transmisiones=True,
        acceso_reportes_avanzados=True
    )
    
    db.commit()
```

---

## ✅ Checklist de Implementación

### Configuración
- [ ] Agregar credenciales ImageKit a `.env`
- [ ] Actualizar `config.py` con variables ImageKit
- [ ] Instalar librería `imagekitio`

### Modelos
- [ ] Crear `GalloImagen`, `PeleaImagen`, `TopeImagen`
- [ ] Crear `SuscripcionMovimiento`
- [ ] Crear `PlanLimite`
- [ ] Ejecutar migraciones Alembic

### Servicios
- [ ] Crear `ImageKitService`
- [ ] Crear `CuotaService`
- [ ] Actualizar `SuscripcionService`

### Endpoints
- [ ] Crear endpoints de ImageKit (`/imagekit/*`)
- [ ] Actualizar endpoints de suscripciones
- [ ] Actualizar endpoints de gallos/peleas/topes

### Migración
- [ ] Script de migración de imágenes
- [ ] Seed de `plan_limites`
- [ ] Validar migración

### Testing
- [ ] Test de upload a ImageKit
- [ ] Test de validación de cuotas
- [ ] Test de endpoints de suscripciones

---

## 📚 REFERENCIA: Implementación Actual en peleas_evento.py

### ✅ Patrón EXITOSO de ImageKit (ya funcionando)

**Archivo:** `app/api/v1/peleas_evento.py`

#### 1. Import del servicio (línea 23)
```python
from app.services.imagekit_service import imagekit_service  # 🎬 ImageKit para videos
```

#### 2. Upload de video en CREATE (líneas 228-260)
```python
# 🎬 Subir video si se proporcionó - USANDO IMAGEKIT
if video:
    logger.info(f"[CREAR PELEA] 🎬 Subiendo video a ImageKit...")
    
    try:
        nueva_pelea.estado_video = 'procesando'
        db.commit()
        
        # Leer contenido del archivo
        video_content = await video.read()
        
        # Subir a ImageKit
        upload_result = imagekit_service.upload_video(
            file_content=video_content,
            file_name=f"pelea_{nueva_pelea.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{video.filename}",
            folder=f"eventos_peleas/evento_{evento_id}"
        )
        
        if upload_result:
            nueva_pelea.video_url = upload_result.get('url')
            nueva_pelea.thumbnail_pelea_url = upload_result.get('thumbnail_url')
            nueva_pelea.estado_video = 'disponible'
            
            logger.info(f"[CREAR PELEA] ✅ Video subido exitosamente a ImageKit: {nueva_pelea.video_url}")
        else:
            raise Exception("ImageKit no retornó resultado de upload")
            
    except Exception as e:
        logger.error(f"[CREAR PELEA] ❌ Error subiendo video a ImageKit: {e}")
        nueva_pelea.estado_video = 'sin_video'
        # No fallar la creación si falla el video
```

#### 3. Upload de video en UPDATE (líneas 438-470)
```python
# 🎬 Subir nuevo video si se proporciona - USANDO IMAGEKIT
if video:
    logger.info(f"[ACTUALIZAR PELEA] 🎬 Subiendo nuevo video a ImageKit...")
    
    try:
        pelea.estado_video = 'procesando'
        db.commit()
        
        # Leer contenido del archivo
        video_content = await video.read()
        
        # Subir a ImageKit
        upload_result = imagekit_service.upload_video(
            file_content=video_content,
            file_name=f"pelea_{pelea.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{video.filename}",
            folder=f"eventos_peleas/evento_{pelea.evento_id}"
        )
        
        if upload_result:
            pelea.video_url = upload_result.get('url')
            pelea.thumbnail_pelea_url = upload_result.get('thumbnail_url')
            pelea.estado_video = 'disponible'
            
            logger.info(f"[ACTUALIZAR PELEA] ✅ Video actualizado exitosamente en ImageKit")
        else:
            raise Exception("ImageKit no retornó resultado de upload")
            
    except Exception as e:
        logger.error(f"[ACTUALIZAR PELEA] ❌ Error subiendo video a ImageKit: {e}")
        pelea.estado_video = 'sin_video'
```

#### 4. Eliminación (líneas 675-686) - PENDIENTE MIGRAR
```python
# ⚠️ TODAVÍA USA CLOUDINARY - MIGRAR A IMAGEKIT
if pelea.video_url:
    try:
        # Extraer public_id del URL
        public_id = pelea.video_url.split('/')[-1].split('.')[0]
        cloudinary.uploader.destroy(
            f"peleas_evento/{pelea.evento_id}/{public_id}",
            resource_type="video"
        )
        logger.info(f"[ELIMINAR PELEA] Video eliminado de Cloudinary")
    except Exception as e:
        logger.warning(f"[ELIMINAR PELEA] No se pudo eliminar video de Cloudinary: {e}")
```

**DEBE CAMBIAR A:**
```python
# ✅ USAR IMAGEKIT
if pelea.video_url and pelea.file_id:  # Necesita guardar file_id
    try:
        success = imagekit_service.delete_video(pelea.file_id)
        if success:
            logger.info(f"[ELIMINAR PELEA] Video eliminado de ImageKit")
        else:
            logger.warning(f"[ELIMINAR PELEA] No se pudo eliminar video de ImageKit")
    except Exception as e:
        logger.warning(f"[ELIMINAR PELEA] Error eliminando video: {e}")
```

### 🎯 Lecciones Aprendidas

1. **Siempre leer el archivo como bytes:** `await file.read()`
2. **Usar nombres únicos con timestamp:** `f"pelea_{id}_{timestamp}_{filename}"`
3. **Organizar en carpetas:** `folder=f"eventos_peleas/evento_{id}"`
4. **Guardar file_id para eliminar:** `file_id = upload_result.get('file_id')`
5. **No fallar el proceso si falla el upload:** Try-catch con logging
6. **Estado de procesamiento:** `estado_video = 'procesando'` → `'disponible'` / `'sin_video'`
7. **Thumbnail automático:** ImageKit retorna `thumbnail_url`

### 📋 Checklist de Migración por Módulo

Usar este patrón para migrar cada módulo:

**Gallos:**
- [ ] Agregar campo `file_id` a `GalloImagen`
- [ ] Usar `imagekit_service.upload_image()` en CREATE
- [ ] Usar `imagekit_service.upload_image()` en UPDATE
- [ ] Usar `imagekit_service.delete_image()` en DELETE
- [ ] Organizar en carpeta `gallos/usuario_{user_id}`

**Peleas:**
- [ ] Agregar tabla `PeleaImagen` con `file_id`
- [ ] Usar `imagekit_service.upload_image()` en CREATE
- [ ] Usar `imagekit_service.upload_image()` en UPDATE
- [ ] Usar `imagekit_service.delete_image()` en DELETE
- [ ] Organizar en carpeta `peleas/usuario_{user_id}`

**Topes:**
- [ ] Agregar tabla `TopeImagen` con `file_id`
- [ ] Usar `imagekit_service.upload_image()` en CREATE
- [ ] Usar `imagekit_service.upload_image()` en UPDATE
- [ ] Usar `imagekit_service.delete_image()` en DELETE
- [ ] Organizar en carpeta `topes/usuario_{user_id}`

---

**Documento creado:** 2025-11-14
**Última actualización:** 2025-11-14
**Estado:** 📋 Listo para implementación - Con referencia de peleas_evento.py
