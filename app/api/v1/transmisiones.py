# 📺 API Endpoints para Transmisiones - Sistema Completo
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, or_, text
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging

from app.database import get_db
from app.core.security import get_current_user_id, get_current_user
from app.models.coliseo import Coliseo
from app.models.evento_transmision import EventoTransmision
from app.models.user import User
from app.schemas.transmision import (
    ColiseoResponse, ColiseoCreate, ColiseoUpdate,
    EventoTransmisionResponse, EventoTransmisionCreate, EventoTransmisionUpdate,
    EventoFiltros, EventosResponse, EstadisticasTransmision
)

# Configurar logger
logger = logging.getLogger("galloapp.transmisiones")
router = APIRouter(prefix="/transmisiones", tags=["📺 Transmisiones"])

# ========================================
# ENDPOINTS PÚBLICOS (USUARIOS NORMALES)
# ========================================

@router.get("/eventos", response_model=EventosResponse)
async def listar_eventos(
    pagina: int = Query(1, ge=1, description="Número de página"),
    por_pagina: int = Query(10, ge=1, le=50, description="Eventos por página"),
    coliseo_id: Optional[int] = Query(None, description="Filtrar por coliseo"),
    fecha: Optional[str] = Query(None, description="Fecha en formato YYYY-MM-DD"),
    estado: Optional[str] = Query(None, description="Estado del evento"),
    solo_hoy: bool = Query(False, description="Solo eventos de hoy"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    📺 Listar eventos de transmisión con filtros

    Retorna eventos paginados con información del coliseo incluida.
    Filtros disponibles: coliseo, fecha, estado, solo_hoy.
    """
    try:
        # Construir query base
        query = db.query(EventoTransmision).join(Coliseo)

        # Aplicar filtros
        if coliseo_id:
            query = query.filter(EventoTransmision.coliseo_id == coliseo_id)

        if solo_hoy:
            hoy = date.today()
            query = query.filter(func.date(EventoTransmision.fecha_evento) == hoy)
        elif fecha:
            try:
                fecha_filtro = datetime.strptime(fecha, '%Y-%m-%d').date()
                query = query.filter(func.date(EventoTransmision.fecha_evento) == fecha_filtro)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha inválido. Use YYYY-MM-DD"
                )

        if estado:
            query = query.filter(EventoTransmision.estado == estado)

        # Solo eventos activos y coliseos activos
        query = query.filter(Coliseo.activo == True)

        # Contar total
        total = query.count()

        # Aplicar paginación y ordenamiento
        eventos = query.order_by(desc(EventoTransmision.fecha_evento))\
                      .offset((pagina - 1) * por_pagina)\
                      .limit(por_pagina)\
                      .all()

        # Calcular total de páginas
        total_paginas = (total + por_pagina - 1) // por_pagina

        return EventosResponse(
            eventos=eventos,
            total=total,
            pagina=pagina,
            por_pagina=por_pagina,
            total_paginas=total_paginas
        )

    except Exception as e:
        logger.error(f"Error listando eventos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener eventos"
        )

@router.get("/eventos/hoy", response_model=List[EventoTransmisionResponse])
async def eventos_hoy(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    📺 Obtener eventos del día actual

    Retorna todos los eventos programados para hoy ordenados por hora.
    """
    try:
        hoy = date.today()
        eventos = db.query(EventoTransmision)\
                   .join(Coliseo)\
                   .filter(
                       and_(
                           func.date(EventoTransmision.fecha_evento) == hoy,
                           Coliseo.activo == True
                       )
                   )\
                   .order_by(EventoTransmision.fecha_evento)\
                   .all()

        return eventos

    except Exception as e:
        logger.error(f"Error obteniendo eventos de hoy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener eventos de hoy"
        )

@router.get("/eventos/{evento_id}", response_model=EventoTransmisionResponse)
async def obtener_evento(
    evento_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    📺 Obtener detalles de un evento específico

    Retorna la información completa del evento incluyendo datos del coliseo.
    """
    try:
        evento = db.query(EventoTransmision)\
                  .join(Coliseo)\
                  .filter(
                      and_(
                          EventoTransmision.id == evento_id,
                          Coliseo.activo == True
                      )
                  )\
                  .first()

        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )

        return evento

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo evento {evento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener evento"
        )

@router.get("/coliseos", response_model=List[ColiseoResponse])
async def listar_coliseos(
    activo: bool = Query(True, description="Solo coliseos activos"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    📺 Listar coliseos disponibles

    Retorna lista de coliseos para filtros y selección.
    """
    try:
        query = db.query(Coliseo)

        if activo:
            query = query.filter(Coliseo.activo == True)

        coliseos = query.order_by(Coliseo.nombre).all()

        return coliseos

    except Exception as e:
        logger.error(f"Error listando coliseos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener coliseos"
        )

# ========================================
# ENDPOINTS ADMIN
# ========================================

@router.post("/admin/coliseos", response_model=ColiseoResponse)
async def crear_coliseo(
    coliseo_data: ColiseoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    👨‍💼 [ADMIN] Crear nuevo coliseo

    Solo usuarios admin pueden crear coliseos.
    """
    if not current_user.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores."
        )

    try:
        # Verificar si ya existe un coliseo con el mismo nombre en la misma ciudad
        coliseo_existente = db.query(Coliseo).filter(
            and_(
                Coliseo.nombre == coliseo_data.nombre,
                Coliseo.ciudad == coliseo_data.ciudad
            )
        ).first()

        if coliseo_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un coliseo con ese nombre en esa ciudad"
            )

        nuevo_coliseo = Coliseo(**coliseo_data.dict())
        db.add(nuevo_coliseo)
        db.commit()
        db.refresh(nuevo_coliseo)

        logger.info(f"Coliseo creado por admin {current_user.id}: {nuevo_coliseo.nombre}")
        return nuevo_coliseo

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creando coliseo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear coliseo"
        )

@router.put("/admin/coliseos/{coliseo_id}", response_model=ColiseoResponse)
async def actualizar_coliseo(
    coliseo_id: int,
    coliseo_data: ColiseoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    👨‍💼 [ADMIN] Actualizar coliseo existente
    """
    if not current_user.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores."
        )

    try:
        coliseo = db.query(Coliseo).filter(Coliseo.id == coliseo_id).first()

        if not coliseo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coliseo no encontrado"
            )

        # Actualizar campos que no son None
        for campo, valor in coliseo_data.dict(exclude_unset=True).items():
            setattr(coliseo, campo, valor)

        coliseo.updated_at = datetime.now()
        db.commit()
        db.refresh(coliseo)

        logger.info(f"Coliseo {coliseo_id} actualizado por admin {current_user.id}")
        return coliseo

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error actualizando coliseo {coliseo_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar coliseo"
        )

@router.post("/admin/eventos", response_model=EventoTransmisionResponse)
async def crear_evento(
    evento_data: EventoTransmisionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    👨‍💼 [ADMIN] Crear nuevo evento de transmisión
    """
    if not current_user.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores."
        )

    try:
        # Verificar que el coliseo existe
        coliseo = db.query(Coliseo).filter(Coliseo.id == evento_data.coliseo_id).first()
        if not coliseo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coliseo no encontrado"
            )

        nuevo_evento = EventoTransmision(
            **evento_data.dict(),
            admin_creador_id=current_user.id
        )

        db.add(nuevo_evento)
        db.commit()
        db.refresh(nuevo_evento)

        logger.info(f"Evento creado por admin {current_user.id}: {nuevo_evento.titulo}")
        return nuevo_evento

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creando evento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear evento"
        )

@router.put("/admin/eventos/{evento_id}", response_model=EventoTransmisionResponse)
async def actualizar_evento(
    evento_id: int,
    evento_data: EventoTransmisionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    👨‍💼 [ADMIN] Actualizar evento existente
    """
    if not current_user.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores."
        )

    try:
        evento = db.query(EventoTransmision).filter(EventoTransmision.id == evento_id).first()

        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )

        # Actualizar campos
        for campo, valor in evento_data.dict(exclude_unset=True).items():
            setattr(evento, campo, valor)

        evento.updated_at = datetime.now()
        db.commit()
        db.refresh(evento)

        logger.info(f"Evento {evento_id} actualizado por admin {current_user.id}")
        return evento

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error actualizando evento {evento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar evento"
        )

@router.put("/admin/eventos/{evento_id}/estado")
async def cambiar_estado_evento(
    evento_id: int,
    estado: str = Query(..., regex="^(programado|en_vivo|finalizado|cancelado)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    👨‍💼 [ADMIN] Cambiar estado de evento

    Estados válidos: programado, en_vivo, finalizado, cancelado
    """
    if not current_user.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores."
        )

    try:
        evento = db.query(EventoTransmision).filter(EventoTransmision.id == evento_id).first()

        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )

        evento.estado = estado
        evento.updated_at = datetime.now()
        db.commit()

        logger.info(f"Estado de evento {evento_id} cambiado a '{estado}' por admin {current_user.id}")
        return {"message": f"Estado cambiado a '{estado}'", "evento_id": evento_id}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error cambiando estado del evento {evento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al cambiar estado del evento"
        )

@router.get("/admin/estadisticas", response_model=EstadisticasTransmision)
async def obtener_estadisticas(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    👨‍💼 [ADMIN] Obtener estadísticas del sistema de transmisiones
    """
    if not current_user.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores."
        )

    try:
        hoy = date.today()

        # Contar eventos
        total_eventos = db.query(func.count(EventoTransmision.id)).scalar()
        eventos_hoy = db.query(func.count(EventoTransmision.id))\
                       .filter(func.date(EventoTransmision.fecha_evento) == hoy)\
                       .scalar()
        eventos_en_vivo = db.query(func.count(EventoTransmision.id))\
                           .filter(EventoTransmision.estado == 'en_vivo')\
                           .scalar()
        eventos_programados = db.query(func.count(EventoTransmision.id))\
                               .filter(EventoTransmision.estado == 'programado')\
                               .scalar()

        # Contar coliseos
        total_coliseos = db.query(func.count(Coliseo.id)).scalar()
        coliseos_activos = db.query(func.count(Coliseo.id))\
                           .filter(Coliseo.activo == True)\
                           .scalar()

        return EstadisticasTransmision(
            total_eventos=total_eventos,
            eventos_hoy=eventos_hoy,
            eventos_en_vivo=eventos_en_vivo,
            eventos_programados=eventos_programados,
            total_coliseos=total_coliseos,
            coliseos_activos=coliseos_activos
        )

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener estadísticas"
        )