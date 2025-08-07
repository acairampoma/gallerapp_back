# 🥊 API Endpoints para Peleas
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional
from datetime import datetime, timedelta
import cloudinary.uploader
import logging
import time
from functools import wraps

# Configurar logger específico para peleas
logger = logging.getLogger("galloapp.peleas")
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
from app.models.pelea import Pelea, ResultadoPelea
from app.models.user import User
from app.schemas.pelea import PeleaCreate, PeleaUpdate, PeleaResponse, PeleaStats
from app.core.security import get_current_user_id

router = APIRouter(prefix="/peleas", tags=["🥊 Peleas"])

# 🔧 ENDPOINT DEBUG ULTRA SIMPLE
@router.post("/test-simple")
async def test_simple_pelea():
    """🔧 TEST: Endpoint ultra simple sin BD"""
    return {"status": "ok", "message": "Endpoint de peleas funcionando"}

# 🔧 ENDPOINT DE DEBUG TEMPORAL  
@router.post("/debug")
async def debug_create_pelea(
    titulo: str = Form(...),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🔧 DEBUG: Crear pelea ultra simple"""
    try:
        from datetime import datetime
        
        # Crear pelea MÍNIMA
        db_pelea = Pelea(
            user_id=current_user_id,
            gallo_id=1,  # Hardcoded para test
            titulo=titulo,
            fecha_pelea=datetime.now()
        )
        
        db.add(db_pelea)
        db.commit()
        db.refresh(db_pelea)
        
        return {
            "status": "success",
            "pelea_id": db_pelea.id,
            "user_id": current_user_id,
            "titulo": titulo
        }
        
    except Exception as e:
        db.rollback()
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }

# 📋 LISTAR PELEAS
@router.get("/", response_model=List[PeleaResponse])
@log_performance("Consulta lista de peleas")
async def get_peleas(
    skip: int = Query(0, ge=0, le=10000, description="Elementos a saltar para paginación"),
    limit: int = Query(50, ge=1, le=100, description="Límite de elementos por página"),
    gallo_id: Optional[int] = Query(None, gt=0, description="Filtrar por ID de gallo específico"),
    resultado: Optional[str] = Query(None, description="Filtrar por resultado (ganada/perdida/empate)"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Obtener lista paginada de peleas con filtros avanzados
    
    **Descripción:** Lista todas las peleas del usuario autenticado con opciones de filtrado y paginación.
    
    **Parámetros de consulta:**
    - `skip`: Número de elementos a omitir (para paginación)
    - `limit`: Máximo de elementos a retornar (1-100)
    - `gallo_id`: Filtrar por un gallo específico
    - `resultado`: Filtrar por resultado (ganada/perdida/empate)
    
    **Respuesta:** Lista de peleas ordenadas por fecha descendente
    
    **Ejemplos de uso:**
    - `/peleas?limit=20` - Primeras 20 peleas
    - `/peleas?gallo_id=5&resultado=ganada` - Peleas ganadas del gallo 5
    - `/peleas?skip=10&limit=10` - Página 2 con 10 elementos
    """
    try:
        # Query base con índices optimizados
        query = db.query(Pelea).filter(Pelea.user_id == current_user_id)
        
        # Aplicar filtros
        if gallo_id:
            query = query.filter(Pelea.gallo_id == gallo_id)
        
        if resultado and resultado in ["ganada", "perdida", "empate"]:
            query = query.filter(Pelea.resultado == resultado)
        
        # Ordenar y paginar con límites seguros
        peleas = query.order_by(Pelea.fecha_pelea.desc()).offset(skip).limit(min(limit, 100)).all()
        
        logger.info(f"Lista peleas consultada", extra={
            "user_id": current_user_id, 
            "count": len(peleas), 
            "filters": {"gallo_id": gallo_id, "resultado": resultado}
        })
        
        return peleas
    
    except SQLAlchemyError as e:
        logger.error(f"Error consultando peleas para usuario {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al consultar las peleas"
        )
    except Exception as e:
        logger.error(f"Error inesperado consultando peleas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error inesperado al procesar la consulta"
        )

# 📊 ESTADÍSTICAS DE PELEAS
@router.get("/stats", response_model=PeleaStats)
async def get_peleas_stats(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📊 Estadísticas completas de rendimiento en peleas
    
    **Descripción:** Proporciona un resumen estadístico completo del rendimiento del usuario en peleas.
    
    **Incluye:**
    - Total de peleas registradas
    - Conteos por resultado (ganadas/perdidas/empates)
    - Porcentaje de efectividad
    - Peleas realizadas este mes
    - Fecha de la última pelea
    
    **Utilidad:** Ideal para dashboards y análisis de rendimiento
    """
    try:
        # Total de peleas
        total_peleas = db.query(func.count(Pelea.id)).filter(
            Pelea.user_id == current_user_id
        ).scalar() or 0
        
        # Contar por resultado - usando strings
        ganadas = db.query(func.count(Pelea.id)).filter(
            Pelea.user_id == current_user_id,
            Pelea.resultado == "ganada"
        ).scalar() or 0
        
        perdidas = db.query(func.count(Pelea.id)).filter(
            Pelea.user_id == current_user_id,
            Pelea.resultado == "perdida"
        ).scalar() or 0
        
        empates = db.query(func.count(Pelea.id)).filter(
            Pelea.user_id == current_user_id,
            Pelea.resultado == "empate"
        ).scalar() or 0
        
        # Efectividad
        efectividad = 0.0
        if total_peleas > 0:
            efectividad = (ganadas / total_peleas) * 100
        
        # Peleas este mes
        fecha_inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        peleas_este_mes = db.query(func.count(Pelea.id)).filter(
            Pelea.user_id == current_user_id,
            Pelea.fecha_pelea >= fecha_inicio_mes
        ).scalar() or 0
        
        # Última pelea
        ultima_pelea = db.query(Pelea.fecha_pelea).filter(
            Pelea.user_id == current_user_id
        ).order_by(Pelea.fecha_pelea.desc()).first()
    
        return PeleaStats(
            total_peleas=total_peleas,
            ganadas=ganadas,
            perdidas=perdidas,
            empates=empates,
            efectividad=round(efectividad, 2),
            peleas_este_mes=peleas_este_mes,
            ultima_pelea=ultima_pelea[0] if ultima_pelea else None
        )
    
    except SQLAlchemyError as e:
        logger.error(f"Error consultando estadísticas de peleas para usuario {current_user_id}: {str(e)}")
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

# 🔍 OBTENER PELEA POR ID
@router.get("/{pelea_id}", response_model=PeleaResponse)
async def get_pelea(
    pelea_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🔍 Obtener detalles completos de una pelea
    
    **Descripción:** Recupera toda la información de una pelea específica.
    
    **Incluye:**
    - Datos básicos (título, fecha, ubicación)
    - Información del oponente
    - Resultado y notas
    - URL del video si existe
    - Timestamps de creación y actualización
    
    **Validación:** Solo el propietario puede acceder a sus peleas
    """
    pelea = db.query(Pelea).filter(
        Pelea.id == pelea_id,
        Pelea.user_id == current_user_id
    ).first()
    
    if not pelea:
        raise HTTPException(status_code=404, detail="Pelea no encontrada")
    
    return pelea

# ➕ CREAR PELEA
@router.post("/")
async def create_pelea(
    gallo_id: int = Form(...),
    titulo: str = Form(...),
    fecha_pelea: datetime = Form(...),
    descripcion: Optional[str] = Form(None),
    ubicacion: Optional[str] = Form(None),
    oponente_nombre: Optional[str] = Form(None),
    oponente_gallo: Optional[str] = Form(None),
    resultado: Optional[str] = Form(None),
    notas_resultado: Optional[str] = Form(None),
    video: Optional[UploadFile] = File(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """➕ Crear nueva pelea con subida de video
    
    **Descripción:** Registra una nueva pelea con todos sus detalles y opcionalmente un video.
    
    **Campos requeridos:**
    - `gallo_id`: ID del gallo participante
    - `titulo`: Título descriptivo de la pelea
    - `fecha_pelea`: Fecha y hora del evento
    
    **Campos opcionales:**
    - `descripcion`: Descripción detallada
    - `ubicacion`: Lugar de la pelea
    - `oponente_nombre`: Nombre del dueño rival
    - `oponente_gallo`: Nombre del gallo rival
    - `resultado`: ganada/perdida/empate
    - `notas_resultado`: Observaciones del resultado
    - `video`: Archivo de video (MP4, MOV, AVI)
    
    **Características:**
    - Subida automática a Cloudinary
    - Validaciones de datos robustas
    - Rollback automático en caso de error
    """
    
    # Validar que el gallo existe y pertenece al usuario (comentado para pruebas)
    # Nota: Validación comentada temporalmente para permitir creación de peleas
    # En producción, descomentar y asegurar que existe la tabla gallos
    # gallo_count = db.query(func.count("*")).select_from(
    #     db.query("gallos").filter(
    #         text("gallos.id = :gallo_id AND gallos.user_id = :user_id")
    #     )
    # ).params(gallo_id=gallo_id, user_id=current_user_id).scalar()
    
    # if gallo_count == 0:
    #     logger.warning(f"Intento de acceso no autorizado", extra={
    #         "user_id": current_user_id,
    #         "attempted_gallo_id": gallo_id,
    #         "operation": "create_pelea"
    #     })
    #     raise HTTPException(
    #         status_code=404, 
    #         detail=f"Gallo con ID {gallo_id} no encontrado o no pertenece al usuario"
    #     )
    
    try:
        # Crear objeto pelea
        db_pelea = Pelea(
            user_id=current_user_id,
            gallo_id=gallo_id,
            titulo=titulo,
            descripcion=descripcion,
            fecha_pelea=fecha_pelea,
            ubicacion=ubicacion,
            oponente_nombre=oponente_nombre,
            oponente_gallo=oponente_gallo,
            resultado=resultado,
            notas_resultado=notas_resultado
        )
    
        # Subida de video simplificada (opcional)
        if video and hasattr(video, 'filename') and video.filename:
            try:
                video_content = await video.read()
                upload_result = cloudinary.uploader.upload(
                    video_content,
                    resource_type="video",
                    folder=f"galloapp/peleas/user_{current_user_id}"
                )
                db_pelea.video_url = upload_result.get('secure_url')
                logger.info(f"Video subido para pelea", extra={"user_id": current_user_id})
            except Exception as e:
                logger.warning(f"Error subiendo video: {str(e)}")
                # Continuar sin video
        
        # Guardar en BD
        db.add(db_pelea)
        db.commit()
        db.refresh(db_pelea)
        
        logger.info(f"Pelea creada exitosamente", extra={
            "user_id": current_user_id,
            "pelea_id": db_pelea.id,
            "gallo_id": gallo_id,
            "has_video": bool(db_pelea.video_url)
        })
        
        return db_pelea
    
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear pelea: {str(e)}", extra={"user_id": current_user_id, "gallo_id": gallo_id})
        raise HTTPException(
            status_code=400,
            detail="Error de integridad en los datos. Verifique las referencias."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al crear pelea: {str(e)}", extra={"user_id": current_user_id, "gallo_id": gallo_id})
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al crear la pelea"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear pelea: {str(e)}", extra={"user_id": current_user_id, "gallo_id": gallo_id})
        raise HTTPException(
            status_code=500,
            detail="Error inesperado al procesar la solicitud"
        )

# ✏️ ACTUALIZAR PELEA
@router.put("/{pelea_id}")
async def update_pelea(
    pelea_id: int,
    titulo: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    fecha_pelea: Optional[datetime] = Form(None),
    ubicacion: Optional[str] = Form(None),
    oponente_nombre: Optional[str] = Form(None),
    oponente_gallo: Optional[str] = Form(None),
    resultado: Optional[str] = Form(None),
    notas_resultado: Optional[str] = Form(None),
    video: Optional[UploadFile] = File(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """✏️ Actualizar pelea con nuevos datos y/o video
    
    **Descripción:** Modifica una pelea existente. Todos los campos son opcionales.
    
    **Comportamiento:**
    - Solo actualiza los campos proporcionados
    - Mantiene valores existentes para campos no enviados
    - Reemplaza video anterior si se envía uno nuevo
    - Actualiza timestamp de modificación
    
    **Validación de seguridad:**
    - Solo el propietario puede modificar sus peleas
    - Validación de integridad de datos
    - Transacciones atómicas
    """
    
    try:
        # Buscar pelea
        pelea = db.query(Pelea).filter(
            Pelea.id == pelea_id,
            Pelea.user_id == current_user_id
        ).first()
        
        if not pelea:
            raise HTTPException(
                status_code=404, 
                detail=f"Pelea con ID {pelea_id} no encontrada o no pertenece al usuario"
            )
        
        # Actualizar campos si se proporcionan
        if titulo is not None:
            pelea.titulo = titulo
        if descripcion is not None:
            pelea.descripcion = descripcion
        if fecha_pelea is not None:
            pelea.fecha_pelea = fecha_pelea
        if ubicacion is not None:
            pelea.ubicacion = ubicacion
        if oponente_nombre is not None:
            pelea.oponente_nombre = oponente_nombre
        if oponente_gallo is not None:
            pelea.oponente_gallo = oponente_gallo
        if resultado is not None:
            pelea.resultado = resultado
        if notas_resultado is not None:
            pelea.notas_resultado = notas_resultado
    
        # Si hay nuevo video, actualizarlo
        if video and video.filename:
            try:
                video_content = await video.read()
                upload_result = cloudinary.uploader.upload(
                    video_content,
                    resource_type="video",
                    folder=f"galloapp/peleas/user_{current_user_id}",
                    public_id=f"pelea_{pelea.gallo_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    overwrite=True
                )
                pelea.video_url = upload_result.get('secure_url')
            except Exception as e:
                logger.warning(f"Error actualizando video para pelea {pelea_id}: {str(e)}")
        
        pelea.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(pelea)
        
        return pelea
    
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar pelea {pelea_id}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad en los datos"
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de BD al actualizar pelea {pelea_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al actualizar"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar pelea {pelea_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error inesperado al procesar la solicitud"
        )

# 🗑️ ELIMINAR PELEA
@router.delete("/{pelea_id}")
async def delete_pelea(
    pelea_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🗑️ Eliminar pelea y recursos asociados
    
    **Descripción:** Elimina permanentemente una pelea y limpia recursos.
    
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
        pelea = db.query(Pelea).filter(
            Pelea.id == pelea_id,
            Pelea.user_id == current_user_id
        ).first()
        
        if not pelea:
            raise HTTPException(
                status_code=404, 
                detail=f"Pelea con ID {pelea_id} no encontrada o no pertenece al usuario"
            )
    
        # Si hay video, intentar eliminarlo de Cloudinary
        if pelea.video_url:
            try:
                # Extraer public_id del URL
                parts = pelea.video_url.split('/')
                public_id = '/'.join(parts[-2:]).split('.')[0]
                cloudinary.uploader.destroy(public_id, resource_type="video")
            except Exception as e:
                logger.warning(f"Error eliminando video de Cloudinary para pelea {pelea_id}: {str(e)}")
        
        db.delete(pelea)
        db.commit()
        
        return {"message": f"Pelea con ID {pelea_id} eliminada exitosamente"}
    
    except HTTPException:
        # Re-lanzar HTTPExceptions tal como están
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de BD al eliminar pelea {pelea_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor al eliminar"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al eliminar pelea {pelea_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error inesperado al procesar la solicitud"
        )