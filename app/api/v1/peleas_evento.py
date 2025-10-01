# 🥊 API Endpoints para Peleas de Evento - Sistema Completo
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
import logging
import cloudinary
import cloudinary.uploader
from datetime import datetime, time

from app.database import get_db
from app.core.security import get_current_user_id, get_admin_user
from app.models.pelea_evento import PeleaEvento
from app.models.evento_transmision import EventoTransmision
from app.schemas.pelea_evento import (
    PeleaEventoCreate,
    PeleaEventoUpdate,
    PeleaEventoResponse,
    PeleaEventoOrdenUpdate
)

# Configurar logger
logger = logging.getLogger("galloapp.peleas_evento")
router = APIRouter(prefix="/transmisiones/eventos", tags=["🥊 Peleas de Evento"])

# ========================================
# ENDPOINTS DE PELEAS DE EVENTO
# ========================================

@router.post("/{evento_id}/peleas", response_model=PeleaEventoResponse, status_code=status.HTTP_201_CREATED)
async def crear_pelea_evento(
    evento_id: int,
    numero_pelea: int = Form(..., description="Número de la pelea"),
    titulo_pelea: str = Form(..., description="Título de la pelea"),
    galpon_izquierda: str = Form(..., description="Galpón lado izquierdo"),
    gallo_izquierda_nombre: str = Form(..., description="Gallo lado izquierdo"),
    galpon_derecha: str = Form(..., description="Galpón lado derecho"),
    gallo_derecha_nombre: str = Form(..., description="Gallo lado derecho"),
    descripcion_pelea: Optional[str] = Form(None, description="Descripción opcional"),
    hora_inicio_estimada: Optional[str] = Form(None, description="Hora estimada HH:MM:SS"),
    video: Optional[UploadFile] = File(None, description="Video de la pelea"),
    current_user: dict = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    🥊 Crear nueva pelea para un evento

    **Solo ADMIN**

    Crea una pelea asociada a un evento de transmisión.
    Opcionalmente puede subir video a Cloudinary.
    """
    try:
        logger.info(f"[CREAR PELEA] Admin {current_user['id']} creando pelea #{numero_pelea} para evento {evento_id}")

        # Verificar que el evento existe
        evento = db.query(EventoTransmision).filter(EventoTransmision.id == evento_id).first()
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evento {evento_id} no encontrado"
            )

        # Verificar que no existe otra pelea con el mismo número en este evento
        pelea_existente = db.query(PeleaEvento).filter(
            and_(
                PeleaEvento.evento_id == evento_id,
                PeleaEvento.numero_pelea == numero_pelea
            )
        ).first()

        if pelea_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una pelea #{numero_pelea} en este evento"
            )

        # Procesar hora_inicio_estimada
        hora_obj = None
        if hora_inicio_estimada:
            try:
                hora_obj = datetime.strptime(hora_inicio_estimada, "%H:%M:%S").time()
            except ValueError:
                try:
                    hora_obj = datetime.strptime(hora_inicio_estimada, "%H:%M").time()
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Formato de hora inválido. Use HH:MM o HH:MM:SS"
                    )

        # Crear pelea
        nueva_pelea = PeleaEvento(
            evento_id=evento_id,
            numero_pelea=numero_pelea,
            titulo_pelea=titulo_pelea,
            descripcion_pelea=descripcion_pelea,
            galpon_izquierda=galpon_izquierda,
            gallo_izquierda_nombre=gallo_izquierda_nombre,
            galpon_derecha=galpon_derecha,
            gallo_derecha_nombre=gallo_derecha_nombre,
            hora_inicio_estimada=hora_obj,
            admin_editor_id=current_user['id'],
            estado_video='sin_video'
        )

        db.add(nueva_pelea)
        db.flush()  # Para obtener el ID

        # Subir video si se proporcionó
        if video:
            logger.info(f"[CREAR PELEA] Subiendo video a Cloudinary...")

            # Validar tipo de archivo
            if not video.content_type.startswith('video/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El archivo debe ser un video"
                )

            # Subir a Cloudinary
            try:
                nueva_pelea.estado_video = 'procesando'
                db.commit()

                upload_result = cloudinary.uploader.upload(
                    video.file,
                    resource_type="video",
                    folder=f"peleas_evento/{evento_id}",
                    public_id=f"pelea_{nueva_pelea.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    eager=[
                        {"width": 1280, "height": 720, "crop": "limit", "quality": "auto"},
                        {"width": 640, "height": 360, "crop": "limit", "quality": "auto:low"}
                    ],
                    eager_async=True
                )

                nueva_pelea.video_url = upload_result.get('secure_url')
                nueva_pelea.thumbnail_pelea_url = upload_result.get('thumbnail_url')
                nueva_pelea.estado_video = 'disponible'

                logger.info(f"[CREAR PELEA] Video subido exitosamente: {nueva_pelea.video_url}")

            except Exception as e:
                logger.error(f"[CREAR PELEA] Error subiendo video: {e}")
                nueva_pelea.estado_video = 'sin_video'
                # No fallar la creación si falla el video

        db.commit()
        db.refresh(nueva_pelea)

        logger.info(f"[CREAR PELEA] Pelea #{numero_pelea} creada exitosamente (ID: {nueva_pelea.id})")
        return nueva_pelea

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[CREAR PELEA] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear pelea: {str(e)}"
        )


@router.get("/{evento_id}/peleas", response_model=List[PeleaEventoResponse])
async def listar_peleas_evento(
    evento_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    📋 Listar todas las peleas de un evento

    Retorna las peleas ordenadas por numero_pelea.
    """
    try:
        # Verificar que el evento existe
        evento = db.query(EventoTransmision).filter(EventoTransmision.id == evento_id).first()
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evento {evento_id} no encontrado"
            )

        # Obtener peleas ordenadas
        peleas = db.query(PeleaEvento)\
            .filter(PeleaEvento.evento_id == evento_id)\
            .order_by(PeleaEvento.numero_pelea)\
            .all()

        logger.info(f"[LISTAR PELEAS] {len(peleas)} peleas encontradas para evento {evento_id}")
        return peleas

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[LISTAR PELEAS] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar peleas: {str(e)}"
        )


@router.get("/peleas/{pelea_id}", response_model=PeleaEventoResponse)
async def obtener_pelea(
    pelea_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🔍 Obtener detalles de una pelea específica
    """
    try:
        pelea = db.query(PeleaEvento).filter(PeleaEvento.id == pelea_id).first()

        if not pelea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pelea {pelea_id} no encontrada"
            )

        return pelea

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[OBTENER PELEA] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener pelea: {str(e)}"
        )


@router.put("/peleas/{pelea_id}", response_model=PeleaEventoResponse)
async def actualizar_pelea(
    pelea_id: int,
    numero_pelea: Optional[int] = Form(None),
    titulo_pelea: Optional[str] = Form(None),
    descripcion_pelea: Optional[str] = Form(None),
    galpon_izquierda: Optional[str] = Form(None),
    gallo_izquierda_nombre: Optional[str] = Form(None),
    galpon_derecha: Optional[str] = Form(None),
    gallo_derecha_nombre: Optional[str] = Form(None),
    hora_inicio_estimada: Optional[str] = Form(None),
    resultado: Optional[str] = Form(None),
    video: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    ✏️ Actualizar una pelea existente

    **Solo ADMIN**

    Permite actualizar cualquier campo de la pelea.
    Si se proporciona un nuevo video, reemplaza el anterior.
    """
    try:
        pelea = db.query(PeleaEvento).filter(PeleaEvento.id == pelea_id).first()

        if not pelea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pelea {pelea_id} no encontrada"
            )

        # Verificar conflicto de número de pelea
        if numero_pelea and numero_pelea != pelea.numero_pelea:
            pelea_conflicto = db.query(PeleaEvento).filter(
                and_(
                    PeleaEvento.evento_id == pelea.evento_id,
                    PeleaEvento.numero_pelea == numero_pelea,
                    PeleaEvento.id != pelea_id
                )
            ).first()

            if pelea_conflicto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otra pelea #{numero_pelea} en este evento"
                )

            pelea.numero_pelea = numero_pelea

        # Actualizar campos si se proporcionan
        if titulo_pelea is not None:
            pelea.titulo_pelea = titulo_pelea

        if descripcion_pelea is not None:
            pelea.descripcion_pelea = descripcion_pelea

        if galpon_izquierda is not None:
            pelea.galpon_izquierda = galpon_izquierda

        if gallo_izquierda_nombre is not None:
            pelea.gallo_izquierda_nombre = gallo_izquierda_nombre

        if galpon_derecha is not None:
            pelea.galpon_derecha = galpon_derecha

        if gallo_derecha_nombre is not None:
            pelea.gallo_derecha_nombre = gallo_derecha_nombre

        if hora_inicio_estimada is not None:
            try:
                pelea.hora_inicio_estimada = datetime.strptime(hora_inicio_estimada, "%H:%M:%S").time()
            except ValueError:
                try:
                    pelea.hora_inicio_estimada = datetime.strptime(hora_inicio_estimada, "%H:%M").time()
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Formato de hora inválido. Use HH:MM o HH:MM:SS"
                    )

        if resultado is not None:
            if resultado not in ['izquierda', 'derecha', 'empate', '']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Resultado debe ser: izquierda, derecha, o empate"
                )
            pelea.resultado = resultado if resultado else None

        # Subir nuevo video si se proporciona
        if video:
            logger.info(f"[ACTUALIZAR PELEA] Subiendo nuevo video...")

            if not video.content_type.startswith('video/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El archivo debe ser un video"
                )

            try:
                pelea.estado_video = 'procesando'
                db.commit()

                upload_result = cloudinary.uploader.upload(
                    video.file,
                    resource_type="video",
                    folder=f"peleas_evento/{pelea.evento_id}",
                    public_id=f"pelea_{pelea.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    eager=[
                        {"width": 1280, "height": 720, "crop": "limit", "quality": "auto"},
                        {"width": 640, "height": 360, "crop": "limit", "quality": "auto:low"}
                    ],
                    eager_async=True
                )

                pelea.video_url = upload_result.get('secure_url')
                pelea.thumbnail_pelea_url = upload_result.get('thumbnail_url')
                pelea.estado_video = 'disponible'

                logger.info(f"[ACTUALIZAR PELEA] Video actualizado exitosamente")

            except Exception as e:
                logger.error(f"[ACTUALIZAR PELEA] Error subiendo video: {e}")
                pelea.estado_video = 'sin_video'

        pelea.admin_editor_id = current_user['id']

        db.commit()
        db.refresh(pelea)

        logger.info(f"[ACTUALIZAR PELEA] Pelea {pelea_id} actualizada exitosamente")
        return pelea

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[ACTUALIZAR PELEA] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar pelea: {str(e)}"
        )


@router.put("/peleas/{pelea_id}/orden", response_model=PeleaEventoResponse)
async def cambiar_orden_pelea(
    pelea_id: int,
    nuevo_numero: int = Form(..., description="Nuevo número de orden"),
    current_user: dict = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    🔄 Cambiar el orden de una pelea

    **Solo ADMIN**

    Cambia el numero_pelea para reordenar las peleas del evento.
    """
    try:
        pelea = db.query(PeleaEvento).filter(PeleaEvento.id == pelea_id).first()

        if not pelea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pelea {pelea_id} no encontrada"
            )

        if nuevo_numero < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de pelea debe ser mayor a 0"
            )

        # Verificar conflicto
        if nuevo_numero != pelea.numero_pelea:
            pelea_conflicto = db.query(PeleaEvento).filter(
                and_(
                    PeleaEvento.evento_id == pelea.evento_id,
                    PeleaEvento.numero_pelea == nuevo_numero,
                    PeleaEvento.id != pelea_id
                )
            ).first()

            if pelea_conflicto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otra pelea #{nuevo_numero} en este evento. Cambie primero el orden de la otra pelea."
                )

        pelea.numero_pelea = nuevo_numero
        pelea.admin_editor_id = current_user['id']

        db.commit()
        db.refresh(pelea)

        logger.info(f"[CAMBIAR ORDEN] Pelea {pelea_id} ahora es #{nuevo_numero}")
        return pelea

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[CAMBIAR ORDEN] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar orden: {str(e)}"
        )


@router.delete("/peleas/{pelea_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_pelea(
    pelea_id: int,
    current_user: dict = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    🗑️ Eliminar una pelea

    **Solo ADMIN**

    Elimina permanentemente una pelea del evento.
    """
    try:
        pelea = db.query(PeleaEvento).filter(PeleaEvento.id == pelea_id).first()

        if not pelea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pelea {pelea_id} no encontrada"
            )

        # Eliminar video de Cloudinary si existe
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

        db.delete(pelea)
        db.commit()

        logger.info(f"[ELIMINAR PELEA] Pelea {pelea_id} eliminada exitosamente")
        return None

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[ELIMINAR PELEA] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar pelea: {str(e)}"
        )
