# 🏋️ API Endpoints para Topes
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from datetime import datetime
import cloudinary.uploader

from app.database import get_db
from app.models.tope import Tope, TipoEntrenamiento
from app.models.user import User
from app.schemas.tope import TopeCreate, TopeUpdate, TopeResponse, TopeStats
from app.core.security import get_current_user_id

router = APIRouter(prefix="/topes", tags=["topes"])

# 📋 LISTAR TOPES
@router.get("/", response_model=List[TopeResponse])
async def get_topes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    gallo_id: Optional[int] = None,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obtener lista de topes del usuario"""
    query = db.query(Tope).filter(Tope.user_id == current_user_id)
    
    if gallo_id:
        query = query.filter(Tope.gallo_id == gallo_id)
    
    topes = query.order_by(Tope.fecha_tope.desc()).offset(skip).limit(limit).all()
    return topes

# 📊 ESTADÍSTICAS DE TOPES
@router.get("/stats", response_model=TopeStats)
async def get_topes_stats(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de topes del usuario"""
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
    
    # Contar por tipo de entrenamiento
    tipos_entrenamiento: Dict[str, int] = {}
    for tipo in TipoEntrenamiento:
        count = db.query(func.count(Tope.id)).filter(
            Tope.user_id == current_user_id,
            Tope.tipo_entrenamiento == tipo
        ).scalar() or 0
        tipos_entrenamiento[tipo.value] = count
    
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

# 🔍 OBTENER TOPE POR ID
@router.get("/{tope_id}", response_model=TopeResponse)
async def get_tope(
    tope_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obtener un tope específico"""
    tope = db.query(Tope).filter(
        Tope.id == tope_id,
        Tope.user_id == current_user_id
    ).first()
    
    if not tope:
        raise HTTPException(status_code=404, detail="Tope no encontrado")
    
    return tope

# ➕ CREAR TOPE
@router.post("/", response_model=TopeResponse)
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
    """Crear nuevo tope con video opcional"""
    
    # Crear objeto tope
    db_tope = Tope(
        user_id=current_user_id,
        gallo_id=gallo_id,
        titulo=titulo,
        descripcion=descripcion,
        fecha_tope=fecha_tope,
        ubicacion=ubicacion,
        duracion_minutos=duracion_minutos,
        tipo_entrenamiento=TipoEntrenamiento(tipo_entrenamiento) if tipo_entrenamiento else None,
        observaciones=observaciones
    )
    
    # Si hay video, subirlo a Cloudinary
    if video and video.filename:
        try:
            # Leer contenido del video
            video_content = await video.read()
            
            # Subir a Cloudinary
            upload_result = cloudinary.uploader.upload(
                video_content,
                resource_type="video",
                folder=f"galloapp/topes/user_{current_user_id}",
                public_id=f"tope_{gallo_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                overwrite=True
            )
            
            db_tope.video_url = upload_result.get('secure_url')
            
        except Exception as e:
            print(f"Error subiendo video: {str(e)}")
            # No fallar si el video no se puede subir
    
    # Guardar en BD
    db.add(db_tope)
    db.commit()
    db.refresh(db_tope)
    
    return db_tope

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
    """Actualizar tope existente"""
    
    # Buscar tope
    tope = db.query(Tope).filter(
        Tope.id == tope_id,
        Tope.user_id == current_user_id
    ).first()
    
    if not tope:
        raise HTTPException(status_code=404, detail="Tope no encontrado")
    
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
        tope.tipo_entrenamiento = TipoEntrenamiento(tipo_entrenamiento) if tipo_entrenamiento else None
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
            print(f"Error actualizando video: {str(e)}")
    
    tope.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(tope)
    
    return tope

# 🗑️ ELIMINAR TOPE
@router.delete("/{tope_id}")
async def delete_tope(
    tope_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Eliminar tope"""
    
    tope = db.query(Tope).filter(
        Tope.id == tope_id,
        Tope.user_id == current_user_id
    ).first()
    
    if not tope:
        raise HTTPException(status_code=404, detail="Tope no encontrado")
    
    # Si hay video, intentar eliminarlo de Cloudinary
    if tope.video_url:
        try:
            # Extraer public_id del URL
            parts = tope.video_url.split('/')
            public_id = '/'.join(parts[-2:]).split('.')[0]
            cloudinary.uploader.destroy(public_id, resource_type="video")
        except Exception as e:
            print(f"Error eliminando video: {str(e)}")
    
    db.delete(tope)
    db.commit()
    
    return {"message": "Tope eliminado exitosamente"}