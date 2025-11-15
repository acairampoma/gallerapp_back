# 🥊 API Endpoints para Peleas de Evento - Sistema Completo
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
import logging
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
from app.services.pdf_service_reportlab import pdf_service_reportlab
from app.services.storage import storage_manager  # 🎬 Storage Manager (ImageKit/Cloudinary)

# Configurar logger
logger = logging.getLogger("galloapp.peleas_evento")
router = APIRouter(prefix="/transmisiones/eventos", tags=["🥊 Peleas de Evento"])

# ========================================
# ENDPOINTS PÚBLICOS - VIDEOTECA (DEBE IR PRIMERO)
# ========================================

@router.get("/videoteca", response_model=List[dict])
async def listar_videoteca(
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    coliseo_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    📹 Listar eventos para videoteca

    **Público - No requiere autenticación**

    Retorna eventos con sus peleas (tengan o no video).
    Se puede filtrar por:
    - Rango de fechas (fecha_inicio, fecha_fin)
    - Coliseo (coliseo_id)

    Agrupa las peleas por evento para mejor visualización.
    """
    try:
        logger.info(f"[VIDEOTECA] Obteniendo eventos - Filtros: fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}, coliseo_id={coliseo_id}")

        # Query base: todos los eventos con peleas
        query = db.query(EventoTransmision).join(
            PeleaEvento,
            EventoTransmision.id == PeleaEvento.evento_id
        )

        # Filtro por fechas
        if fecha_inicio:
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                query = query.filter(EventoTransmision.fecha_evento >= fecha_inicio_dt)
                logger.info(f"[VIDEOTECA] Filtrando desde: {fecha_inicio_dt}")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha_inicio inválido. Use: YYYY-MM-DD"
                )

        if fecha_fin:
            try:
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                query = query.filter(EventoTransmision.fecha_evento <= fecha_fin_dt)
                logger.info(f"[VIDEOTECA] Filtrando hasta: {fecha_fin_dt}")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha_fin inválido. Use: YYYY-MM-DD"
                )

        # Filtro por coliseo
        if coliseo_id:
            query = query.filter(EventoTransmision.coliseo_id == coliseo_id)
            logger.info(f"[VIDEOTECA] Filtrando por coliseo_id: {coliseo_id}")

        # Obtener eventos únicos ordenados por fecha descendente
        eventos = query.distinct().order_by(desc(EventoTransmision.fecha_evento)).all()
        logger.info(f"[VIDEOTECA] Eventos encontrados antes de procesar: {len(eventos)}")

        # Construir respuesta con eventos y sus peleas
        resultado = []
        for evento in eventos:
            # Obtener TODAS las peleas del evento
            peleas = db.query(PeleaEvento).filter(
                PeleaEvento.evento_id == evento.id
            ).order_by(PeleaEvento.numero_pelea).all()

            if peleas:
                resultado.append({
                    "id": evento.id,
                    "titulo": evento.titulo,
                    "descripcion": evento.descripcion,
                    "fecha_evento": evento.fecha_evento.isoformat() if evento.fecha_evento else None,
                    "coliseo_id": evento.coliseo_id,
                    "coliseo_nombre": evento.coliseo.nombre if evento.coliseo else None,
                    "thumbnail_url": evento.thumbnail_url,
                    "total_peleas": len(peleas),
                    "peleas": [
                        {
                            "id": p.id,
                            "numero_pelea": p.numero_pelea,
                            "titulo_pelea": p.titulo_pelea,
                            "descripcion_pelea": p.descripcion_pelea,
                            "galpon_izquierda": p.galpon_izquierda,
                            "gallo_izquierda_nombre": p.gallo_izquierda_nombre,
                            "galpon_derecha": p.galpon_derecha,
                            "gallo_derecha_nombre": p.gallo_derecha_nombre,
                            "resultado": p.resultado,
                            "video_url": p.video_url,
                            "thumbnail_pelea_url": p.thumbnail_pelea_url,
                            "duracion_minutos": p.duracion_minutos,
                            "hora_inicio_real": p.hora_inicio_real.isoformat() if p.hora_inicio_real else None,
                        }
                        for p in peleas
                    ]
                })

        logger.info(f"[VIDEOTECA] {len(resultado)} eventos retornados")
        return resultado

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VIDEOTECA] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener videoteca: {str(e)}"
        )


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
        logger.info(f"[CREAR PELEA] Admin {current_user['user_id']} creando pelea #{numero_pelea} para evento {evento_id}")

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
            admin_editor_id=current_user['user_id'],
            estado_video='sin_video'
        )

        db.add(nueva_pelea)
        db.flush()  # Para obtener el ID

        # 🎬 Subir video si se proporcionó - USANDO IMAGEKIT
        if video:
            logger.info(f"[CREAR PELEA] 🎬 Subiendo video a ImageKit...")
            logger.info(f"[CREAR PELEA] Content-Type recibido: {video.content_type}")
            logger.info(f"[CREAR PELEA] Filename: {video.filename}")

            try:
                nueva_pelea.estado_video = 'procesando'
                db.commit()

                # Leer contenido del archivo
                video_content = await video.read()

                # Subir a ImageKit
                upload_result = storage_manager.upload_video(
                    file_content=video_content,
                    file_name=f"pelea_{nueva_pelea.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{video.filename}",
                    folder=f"eventos_peleas/evento_{evento_id}"
                )

                if upload_result:
                    nueva_pelea.video_url = upload_result.url
                    nueva_pelea.file_id = upload_result.file_id  # Guardar file_id para eliminar después
                    nueva_pelea.thumbnail_pelea_url = upload_result.thumbnail_url
                    nueva_pelea.estado_video = 'disponible'

                    logger.info(f"[CREAR PELEA] ✅ Video subido exitosamente a {storage_manager.provider_name}: {nueva_pelea.video_url}")
                    logger.info(f"[CREAR PELEA] 🆔 File ID: {nueva_pelea.file_id}")
                else:
                    raise Exception("ImageKit no retornó resultado de upload")

            except Exception as e:
                logger.error(f"[CREAR PELEA] ❌ Error subiendo video a ImageKit: {e}")
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

        # 🎬 Subir nuevo video si se proporciona - USANDO IMAGEKIT
        if video:
            logger.info(f"[ACTUALIZAR PELEA] 🎬 Subiendo nuevo video a ImageKit...")
            logger.info(f"[ACTUALIZAR PELEA] Content-Type recibido: {video.content_type}")
            logger.info(f"[ACTUALIZAR PELEA] Filename: {video.filename}")

            try:
                pelea.estado_video = 'procesando'
                db.commit()

                # Leer contenido del archivo
                video_content = await video.read()

                # Subir a ImageKit
                upload_result = storage_manager.upload_video(
                    file_content=video_content,
                    file_name=f"pelea_{pelea.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{video.filename}",
                    folder=f"eventos_peleas/evento_{pelea.evento_id}"
                )

                if upload_result:
                    # Eliminar video anterior si existe
                    if pelea.file_id:
                        logger.info(f"[ACTUALIZAR PELEA] 🗑️ Eliminando video anterior: {pelea.file_id}")
                        storage_manager.delete_file(pelea.file_id)
                    
                    pelea.video_url = upload_result.url
                    pelea.file_id = upload_result.file_id  # Guardar nuevo file_id
                    pelea.thumbnail_pelea_url = upload_result.thumbnail_url
                    pelea.estado_video = 'disponible'

                    logger.info(f"[ACTUALIZAR PELEA] ✅ Video actualizado exitosamente en {storage_manager.provider_name}")
                    logger.info(f"[ACTUALIZAR PELEA] 🆔 Nuevo File ID: {pelea.file_id}")
                else:
                    raise Exception("ImageKit no retornó resultado de upload")

            except Exception as e:
                logger.error(f"[ACTUALIZAR PELEA] ❌ Error subiendo video a ImageKit: {e}")
                pelea.estado_video = 'sin_video'

        pelea.admin_editor_id = current_user['user_id']

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
        pelea.admin_editor_id = current_user['user_id']

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


@router.get("/{evento_id}/pdf")
async def generar_pdf_relacion_peleas(
    evento_id: int,
    current_user: dict = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    📄 Generar PDF con relación de peleas del evento

    **Solo ADMIN**

    Genera un PDF con los datos del evento y el detalle de todas sus peleas.
    Retorna el PDF como base64 para compartir por WhatsApp.
    """
    try:
        logger.info(f"[PDF PELEAS] Admin {current_user['user_id']} generando PDF para evento {evento_id}")

        # Verificar que el servicio PDF está disponible
        if not pdf_service_reportlab:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de PDF no disponible - ReportLab no instalado"
            )

        # Obtener evento
        evento = db.query(EventoTransmision).filter(EventoTransmision.id == evento_id).first()
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evento {evento_id} no encontrado"
            )

        # Obtener peleas del evento
        peleas = db.query(PeleaEvento)\
            .filter(PeleaEvento.evento_id == evento_id)\
            .order_by(PeleaEvento.numero_pelea)\
            .all()

        # Preparar datos para el PDF
        datos_evento = {
            "evento": {
                "titulo": evento.titulo,
                "fecha_evento": evento.fecha_evento.isoformat() if evento.fecha_evento else None,
                "coliseo_nombre": evento.coliseo.nombre if evento.coliseo else "No especificado",
                "descripcion": evento.descripcion or "Sin descripción"
            },
            "peleas": [
                {
                    "numero_pelea": p.numero_pelea,
                    "titulo_pelea": p.titulo_pelea,
                    "galpon_izquierda": p.galpon_izquierda,
                    "gallo_izquierda_nombre": p.gallo_izquierda_nombre,
                    "galpon_derecha": p.galpon_derecha,
                    "gallo_derecha_nombre": p.gallo_derecha_nombre,
                    "hora_inicio_estimada": p.hora_inicio_estimada.isoformat() if p.hora_inicio_estimada else None,
                    "resultado": p.resultado
                }
                for p in peleas
            ],
            "metadata": {
                "fecha_generacion": datetime.now().isoformat(),
                "usuario_id": current_user['user_id'],
                "version": "v1.0"
            }
        }

        # Generar PDF
        pdf_bytes = pdf_service_reportlab.generar_relacion_peleas_pdf(datos_evento)

        if not pdf_bytes:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al generar PDF"
            )

        # Convertir a base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        logger.info(f"[PDF PELEAS] PDF generado exitosamente - {len(pdf_bytes)} bytes")

        return {
            "success": True,
            "message": "PDF generado exitosamente",
            "pdf_base64": pdf_base64,
            "evento_titulo": evento.titulo,
            "total_peleas": len(peleas)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[PDF PELEAS] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar PDF: {str(e)}"
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

        # Eliminar video del storage si existe
        if pelea.file_id:
            try:
                success = storage_manager.delete_file(pelea.file_id)
                if success:
                    logger.info(f"[ELIMINAR PELEA] ✅ Video eliminado de {storage_manager.provider_name}: {pelea.file_id}")
                else:
                    logger.warning(f"[ELIMINAR PELEA] ⚠️ No se pudo eliminar video de {storage_manager.provider_name}")
            except Exception as e:
                logger.warning(f"[ELIMINAR PELEA] ❌ Error eliminando video: {e}")

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
