# 🥊 API Endpoints para Peleas
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import datetime, timedelta
import cloudinary.uploader

from app.database import get_db
from app.models.pelea import Pelea, ResultadoPelea
from app.models.user import User
from app.schemas.pelea import PeleaCreate, PeleaUpdate, PeleaResponse, PeleaStats
from app.core.security import get_current_user_id

router = APIRouter(prefix="/peleas", tags=["peleas"])

# 📋 LISTAR PELEAS
@router.get("/", response_model=List[PeleaResponse])
async def get_peleas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    gallo_id: Optional[int] = None,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obtener lista de peleas del usuario"""
    query = db.query(Pelea).filter(Pelea.user_id == current_user_id)
    
    if gallo_id:
        query = query.filter(Pelea.gallo_id == gallo_id)
    
    peleas = query.order_by(Pelea.fecha_pelea.desc()).offset(skip).limit(limit).all()
    return peleas

# 📊 ESTADÍSTICAS DE PELEAS
@router.get("/stats", response_model=PeleaStats)
async def get_peleas_stats(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de peleas del usuario"""
    # Total de peleas
    total_peleas = db.query(func.count(Pelea.id)).filter(
        Pelea.user_id == current_user_id
    ).scalar() or 0
    
    # Contar por resultado
    ganadas = db.query(func.count(Pelea.id)).filter(
        Pelea.user_id == current_user_id,
        Pelea.resultado == ResultadoPelea.GANADA
    ).scalar() or 0
    
    perdidas = db.query(func.count(Pelea.id)).filter(
        Pelea.user_id == current_user_id,
        Pelea.resultado == ResultadoPelea.PERDIDA
    ).scalar() or 0
    
    empates = db.query(func.count(Pelea.id)).filter(
        Pelea.user_id == current_user_id,
        Pelea.resultado == ResultadoPelea.EMPATE
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

# 🔍 OBTENER PELEA POR ID
@router.get("/{pelea_id}", response_model=PeleaResponse)
async def get_pelea(
    pelea_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Obtener una pelea específica"""
    pelea = db.query(Pelea).filter(
        Pelea.id == pelea_id,
        Pelea.user_id == current_user_id
    ).first()
    
    if not pelea:
        raise HTTPException(status_code=404, detail="Pelea no encontrada")
    
    return pelea

# ➕ CREAR PELEA
@router.post("/", response_model=PeleaResponse)
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
    """Crear nueva pelea con video opcional"""
    
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
        resultado=ResultadoPelea(resultado) if resultado else None,
        notas_resultado=notas_resultado
    )
    
    # Si hay video, subirlo a Cloudinary
    if video and video.filename:
        try:
            # Leer contenido del video
            video_content = await video.read()
            
            # Subir a Cloudinary (configuración para videos)
            upload_result = cloudinary.uploader.upload(
                video_content,
                resource_type="video",
                folder=f"galloapp/peleas/user_{current_user_id}",
                public_id=f"pelea_{gallo_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                overwrite=True
            )
            
            db_pelea.video_url = upload_result.get('secure_url')
            
        except Exception as e:
            print(f"Error subiendo video: {str(e)}")
            # No fallar si el video no se puede subir
    
    # Guardar en BD
    db.add(db_pelea)
    db.commit()
    db.refresh(db_pelea)
    
    return db_pelea

# ✏️ ACTUALIZAR PELEA
@router.put("/{pelea_id}", response_model=PeleaResponse)
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
    """Actualizar pelea existente"""
    
    # Buscar pelea
    pelea = db.query(Pelea).filter(
        Pelea.id == pelea_id,
        Pelea.user_id == current_user_id
    ).first()
    
    if not pelea:
        raise HTTPException(status_code=404, detail="Pelea no encontrada")
    
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
        pelea.resultado = ResultadoPelea(resultado) if resultado else None
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
            print(f"Error actualizando video: {str(e)}")
    
    pelea.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(pelea)
    
    return pelea

# 🗑️ ELIMINAR PELEA
@router.delete("/{pelea_id}")
async def delete_pelea(
    pelea_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Eliminar pelea"""
    
    pelea = db.query(Pelea).filter(
        Pelea.id == pelea_id,
        Pelea.user_id == current_user_id
    ).first()
    
    if not pelea:
        raise HTTPException(status_code=404, detail="Pelea no encontrada")
    
    # Si hay video, intentar eliminarlo de Cloudinary
    if pelea.video_url:
        try:
            # Extraer public_id del URL
            parts = pelea.video_url.split('/')
            public_id = '/'.join(parts[-2:]).split('.')[0]
            cloudinary.uploader.destroy(public_id, resource_type="video")
        except Exception as e:
            print(f"Error eliminando video: {str(e)}")
    
    db.delete(pelea)
    db.commit()
    
    return {"message": "Pelea eliminada exitosamente"}