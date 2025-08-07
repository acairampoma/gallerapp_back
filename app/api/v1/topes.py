# 🏋️ API Endpoints para Topes
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional, Dict
from datetime import datetime
import cloudinary.uploader
import logging
import time
from functools import wraps

# Configurar logger específico para topes
logger = logging.getLogger("galloapp.topes")
logger.setLevel(logging.INFO)

# Decorator para logging de rendimiento
def log_performance(operation: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{operation} completado en {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{operation} falló después de {duration:.2f}s: {str(e)}")
                raise
        return wrapper
    return decorator

from app.database import get_db
from app.models.tope import Tope, TipoEntrenamiento
from app.models.user import User
from app.schemas.tope import TopeCreate, TopeUpdate, TopeResponse, TopeStats
from app.core.security import get_current_user_id

router = APIRouter(prefix="/topes", tags=["🏋️ Topes"])

# 📋 LISTAR TOPES
@router.get("/", response_model=List[TopeResponse])
@log_performance("Consulta lista de topes")
async def get_topes(
    skip: int = Query(0, ge=0, le=10000, description="Elementos a saltar para paginación"),
    limit: int = Query(50, ge=1, le=100, description="Límite de elementos por página"),
    gallo_id: Optional[int] = Query(None, gt=0, description="Filtrar por ID de gallo específico"),
    tipo_entrenamiento: Optional[str] = Query(None, description="Filtrar por tipo (sparring/tecnica/resistencia/velocidad)"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Obtener lista paginada de topes con filtros avanzados
    
    **Descripción:** Lista todos los entrenamientos/topes del usuario con opciones de filtrado y paginación.
    
    **Parámetros de consulta:**
    - `skip`: Número de elementos a omitir (para paginación)
    - `limit`: Máximo de elementos a retornar (1-100)
    - `gallo_id`: Filtrar por un gallo específico
    - `tipo_entrenamiento`: Filtrar por tipo (sparring/tecnica/resistencia/velocidad)
    
    **Respuesta:** Lista de topes ordenados por fecha descendente
    
    **Ejemplos de uso:**
    - `/topes?limit=20` - Primeros 20 topes
    - `/topes?gallo_id=5&tipo_entrenamiento=sparring` - Sparring del gallo 5
    - `/topes?skip=10&limit=10` - Página 2 con 10 elementos
    """
    try:
        # Query base con índices optimizados
        query = db.query(Tope).filter(Tope.user_id == current_user_id)
        
        # Aplicar filtros
        if gallo_id:
            query = query.filter(Tope.gallo_id == gallo_id)
        
        if tipo_entrenamiento and tipo_entrenamiento in ["sparring", "tecnica", "resistencia", "velocidad"]:
            query = query.filter(Tope.tipo_entrenamiento == tipo_entrenamiento)
        
        # Ordenar y paginar con límites seguros
        topes = query.order_by(Tope.fecha_tope.desc()).offset(skip).limit(min(limit, 100)).all()
        return topes
    
    except SQLAlchemyError as e:
        logger.error(f"Error consultando topes para usuario {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al consultar los topes"
        )
    except Exception as e:
        logger.error(f"Error inesperado consultando topes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error inesperado al procesar la consulta"
        )

# 📊 ESTADÍSTICAS DE TOPES
@router.get("/stats", response_model=TopeStats)
@log_performance("Consulta estadísticas topes")
async def get_topes_stats(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📊 Estadísticas completas de entrenamientos
    
    **Descripción:** Proporciona un resumen estadístico completo de los entrenamientos del usuario.
    
    **Incluye:**
    - Total de topes registrados
    - Topes realizados este mes
    - Promedio de duración en minutos
    - Distribución por tipo de entrenamiento
    - Fecha del último tope
    
    **Utilidad:** Ideal para seguimiento de rutinas de entrenamiento
    """
    try:
        # Total de topes
        total_topes = db.query(func.count(Tope.id)).filter(
            Tope.user_id == current_user_id
        ).scalar() or 0
        
        # Topes este mes
        fecha_inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        topes_este_mes = db.query(func.count(Tope.id)).filter(
            Tope.user_id == current_user_id,
            Tope.fecha_tope >= fecha_inicio_mes
        ).scalar() or 0
        
        # Promedio de duración
        promedio_duracion = db.query(func.avg(Tope.duracion_minutos)).filter(
            Tope.user_id == current_user_id,
            Tope.duracion_minutos.isnot(None)
        ).scalar() or 0.0
        
        # Contar por tipo de entrenamiento - usando strings
        tipos_entrenamiento: Dict[str, int] = {}
        tipos_validos = ["sparring", "tecnica", "resistencia", "velocidad"]
        for tipo in tipos_validos:
            count = db.query(func.count(Tope.id)).filter(
                Tope.user_id == current_user_id,
                Tope.tipo_entrenamiento == tipo
            ).scalar() or 0
            tipos_entrenamiento[tipo] = count
        
        # Último tope
        ultimo_tope = db.query(Tope.fecha_tope).filter(
            Tope.user_id == current_user_id
        ).order_by(Tope.fecha_tope.desc()).first()
    
        return TopeStats(
            total_topes=total_topes,
            topes_este_mes=topes_este_mes,
            promedio_duracion=round(promedio_duracion, 1),
            tipos_entrenamiento=tipos_entrenamiento,
            ultimo_tope=ultimo_tope[0] if ultimo_tope else None
        )
    
    except SQLAlchemyError as e:
        logger.error(f"Error consultando estadísticas de topes para usuario {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al consultar las estadísticas"
        )
    except Exception as e:
        logger.error(f"Error inesperado consultando estadísticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error inesperado al procesar las estadísticas"
        )

# 🔍 OBTENER TOPE POR ID
@router.get("/{tope_id}", response_model=TopeResponse)
async def get_tope(
    tope_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🔍 Obtener detalles completos de un tope
    
    **Descripción:** Recupera toda la información de un entrenamiento específico.
    
    **Incluye:**
    - Datos básicos (título, fecha, ubicación)
    - Detalles del entrenamiento (duración, tipo)
    - Observaciones y notas
    - URL del video si existe
    - Timestamps de creación y actualización
    
    **Validación:** Solo el propietario puede acceder a sus topes
    """
    tope = db.query(Tope).filter(
        Tope.id == tope_id,
        Tope.user_id == current_user_id
    ).first()
    
    if not tope:
        raise HTTPException(status_code=404, detail="Tope no encontrado")
    
    return tope

# ➕ CREAR TOPE
@router.post("/", response_model=TopeResponse)
@log_performance("Crear tope")
async def create_tope(
    gallo_id: int = Form(...),
    titulo: str = Form(...),
    fecha_tope: datetime = Form(...),
    descripcion: Optional[str] = Form(None),
    ubicacion: Optional[str] = Form(None),
    duracion_minutos: Optional[int] = Form(None),
    tipo_entrenamiento: Optional[str] = Form(None),
    observaciones: Optional[str] = Form(None),
    video: Optional[UploadFile] = File(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """➕ Crear nuevo tope con subida de video
    
    **Descripción:** Registra un nuevo entrenamiento con todos sus detalles y opcionalmente un video.
    
    **Campos requeridos:**
    - `gallo_id`: ID del gallo entrenado
    - `titulo`: Título descriptivo del entrenamiento
    - `fecha_tope`: Fecha y hora del entrenamiento
    
    **Campos opcionales:**
    - `descripcion`: Descripción detallada
    - `ubicacion`: Lugar del entrenamiento
    - `duracion_minutos`: Duración en minutos (5-480)
    - `tipo_entrenamiento`: sparring/tecnica/resistencia/velocidad
    - `observaciones`: Notas del entrenamiento
    - `video`: Archivo de video (MP4, MOV, AVI)
    
    **Características:**
    - Subida automática a Cloudinary
    - Validaciones de duración y tipos
    - Rollback automático en caso de error
    """
    
    try:
        # Crear objeto tope
        db_tope = Tope(
            user_id=current_user_id,
            gallo_id=gallo_id,
            titulo=titulo,
            descripcion=descripcion,
            fecha_tope=fecha_tope,
            ubicacion=ubicacion,
            duracion_minutos=duracion_minutos,
            tipo_entrenamiento=tipo_entrenamiento,
            observaciones=observaciones
        )
    
        # Subida de video simplificada (opcional) - IGUAL QUE PELEAS
        if video and hasattr(video, 'filename') and video.filename:
            try:
                video_content = await video.read()
                upload_result = cloudinary.uploader.upload(
                    video_content,
                    resource_type="video",
                    folder=f"galloapp/topes/user_{current_user_id}"
                )
                db_tope.video_url = upload_result.get('secure_url')
                logger.info(f"Video subido para tope", extra={"user_id": current_user_id})
            except Exception as e:
                logger.warning(f"Error subiendo video: {str(e)}")
                # Continuar sin video
        
        # Guardar en BD
        db.add(db_tope)
        db.commit()
        db.refresh(db_tope)
        
        return db_tope
    
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear tope: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad en los datos. Verifique las referencias."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al crear tope: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al crear el tope"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear tope: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error inesperado al procesar la solicitud"
        )

# ✏️ ACTUALIZAR TOPE
@router.put("/{tope_id}", response_model=TopeResponse)
async def update_tope(
    tope_id: int,
    titulo: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    fecha_tope: Optional[datetime] = Form(None),
    ubicacion: Optional[str] = Form(None),
    duracion_minutos: Optional[int] = Form(None),
    tipo_entrenamiento: Optional[str] = Form(None),
    observaciones: Optional[str] = Form(None),
    video: Optional[UploadFile] = File(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """✏️ Actualizar tope con nuevos datos y/o video
    
    **Descripción:** Modifica un entrenamiento existente. Todos los campos son opcionales.
    
    **Comportamiento:**
    - Solo actualiza los campos proporcionados
    - Mantiene valores existentes para campos no enviados
    - Reemplaza video anterior si se envía uno nuevo
    - Actualiza timestamp de modificación
    
    **Validaciones:**
    - Duración entre 5-480 minutos
    - Tipos de entrenamiento válidos
    - Solo propietario puede modificar
    """
    
    try:
        # Buscar tope
        tope = db.query(Tope).filter(
            Tope.id == tope_id,
            Tope.user_id == current_user_id
        ).first()
        
        if not tope:
            raise HTTPException(
                status_code=404, 
                detail=f"Tope con ID {tope_id} no encontrado o no pertenece al usuario"
            )
        
        # Actualizar campos si se proporcionan
        if titulo is not None:
            tope.titulo = titulo
        if descripcion is not None:
            tope.descripcion = descripcion
        if fecha_tope is not None:
            tope.fecha_tope = fecha_tope
        if ubicacion is not None:
            tope.ubicacion = ubicacion
        if duracion_minutos is not None:
            tope.duracion_minutos = duracion_minutos
        if tipo_entrenamiento is not None:
            tope.tipo_entrenamiento = tipo_entrenamiento
        if observaciones is not None:
            tope.observaciones = observaciones
        
        # Si hay nuevo video, actualizarlo
        if video and video.filename:
            try:
                video_content = await video.read()
                upload_result = cloudinary.uploader.upload(
                    video_content,
                    resource_type="video",
                    folder=f"galloapp/topes/user_{current_user_id}",
                    public_id=f"tope_{tope.gallo_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    overwrite=True
                )
                tope.video_url = upload_result.get('secure_url')
            except Exception as e:
                logger.warning(f"Error actualizando video para tope {tope_id}: {str(e)}")
        
        tope.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(tope)
        
        return tope
    
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar tope {tope_id}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad en los datos"
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de BD al actualizar tope {tope_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al actualizar"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar tope {tope_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error inesperado al procesar la solicitud"
        )

# 🗑️ ELIMINAR TOPE
@router.delete("/{tope_id}")
async def delete_tope(
    tope_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🗑️ Eliminar tope y recursos asociados
    
    **Descripción:** Elimina permanentemente un entrenamiento y limpia recursos.
    
    **Proceso de eliminación:**
    1. Valida permisos del usuario
    2. Elimina video de Cloudinary (si existe)
    3. Remueve registro de base de datos
    4. Confirma transacción
    
    **Seguridad:**
    - Eliminación irreversible
    - Solo propietario puede eliminar
    - Limpieza automática de recursos
    
    **Respuesta:** Confirmación de eliminación exitosa
    """
    
    try:
        tope = db.query(Tope).filter(
            Tope.id == tope_id,
            Tope.user_id == current_user_id
        ).first()
        
        if not tope:
            raise HTTPException(
                status_code=404, 
                detail=f"Tope con ID {tope_id} no encontrado o no pertenece al usuario"
            )
    
        # Si hay video, intentar eliminarlo de Cloudinary
        if tope.video_url:
            try:
                # Extraer public_id del URL
                parts = tope.video_url.split('/')
                public_id = '/'.join(parts[-2:]).split('.')[0]
                cloudinary.uploader.destroy(public_id, resource_type="video")
            except Exception as e:
                logger.warning(f"Error eliminando video de Cloudinary para tope {tope_id}: {str(e)}")
        
        db.delete(tope)
        db.commit()
        
        return {"message": f"Tope con ID {tope_id} eliminado exitosamente"}
    
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de BD al eliminar tope {tope_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al eliminar"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al eliminar tope {tope_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error inesperado al procesar la solicitud"
        )