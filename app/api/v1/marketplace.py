# 🛒 API Endpoints para Marketplace - Sistema Completo
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, text, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging
import json
from decimal import Decimal

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.marketplace import MarketplacePublicacion, MarketplaceFavorito
from app.schemas.marketplace import (
    MarketplacePublicacionCreate,
    MarketplacePublicacionUpdate,
    MarketplacePublicacionResponse,
    MarketplaceFavoritoCreate,
    MarketplaceFavoritoResponse,
    MarketplaceFiltros,
    MarketplaceLimites,
    MarketplaceListResponse,
    MarketplaceStatsResponse
)

# Configurar logger
logger = logging.getLogger("galloapp.marketplace")
router = APIRouter(prefix="/marketplace", tags=["🛒 Marketplace"])

# ========================================
# ENDPOINTS PÚBLICOS (VER TODAS LAS PUBLICACIONES)
# ========================================

@router.get("/publicaciones", response_model=Dict[str, Any])
async def listar_publicaciones_publicas(
    # Filtros básicos
    precio_min: Optional[Decimal] = Query(None, ge=0, description="Precio mínimo"),
    precio_max: Optional[Decimal] = Query(None, ge=0, description="Precio máximo"),
    estado: Optional[str] = Query("venta", description="Estado (venta, vendido, pausado)"),
    buscar: Optional[str] = Query(None, max_length=100, description="Buscar en nombre de gallo"),

    # Filtros avanzados por gallo
    raza_id: Optional[str] = Query(None, description="ID de raza del gallo"),
    peso_min: Optional[float] = Query(None, ge=0, description="Peso mínimo del gallo"),
    peso_max: Optional[float] = Query(None, ge=0, description="Peso máximo del gallo"),
    color_gallo: Optional[str] = Query(None, description="Color del gallo"),

    # Filtros por fecha
    fecha_desde: Optional[date] = Query(None, description="Fecha de publicación desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha de publicación hasta"),

    # Ordenamiento
    ordenar_por: Optional[str] = Query("fecha_desc", description="precio_asc, precio_desc, fecha_asc, fecha_desc"),

    # Paginación
    skip: int = Query(default=0, ge=0, description="Registros a saltar"),
    limit: int = Query(default=20, ge=1, le=100, description="Límite de registros"),

    # Usuario actual (opcional para favoritos)
    current_user_id: Optional[int] = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🛒 LISTAR TODAS LAS PUBLICACIONES PÚBLICAS DEL MARKETPLACE

    Permite ver publicaciones de todos los usuarios con filtros avanzados:
    - Filtros por precio, raza, peso, color del gallo
    - Filtros por fecha de publicación
    - Búsqueda por nombre de gallo
    - Ordenamiento flexible
    - Paginación
    - Incluye datos del gallo y vendedor (JOINs)
    """
    try:
        logger.info(f"🔍 Listando publicaciones públicas - Usuario: {current_user_id}")

        # Query base con JOINs
        base_query = """
        SELECT
            -- Datos de la publicación
            mp.id, mp.user_id, mp.gallo_id, mp.precio, mp.estado,
            mp.fecha_publicacion, mp.icono_ejemplo,
            mp.created_at, mp.updated_at,

            -- Datos del gallo (JOIN)
            g.nombre as gallo_nombre,
            g.codigo_identificacion as gallo_codigo,
            g.raza_id as gallo_raza_id,
            g.peso as gallo_peso,
            g.altura as gallo_altura,
            g.color as gallo_color,
            g.color_placa as gallo_color_placa,
            g.color_patas as gallo_color_patas,
            g.color_plumaje as gallo_color_plumaje,
            g.fecha_nacimiento as gallo_fecha_nacimiento,
            g.foto_principal_url as gallo_foto_principal,
            g.url_foto_cloudinary as gallo_foto_optimizada,
            g.fotos_adicionales as gallo_fotos_json,
            g.procedencia as gallo_procedencia,

            -- Datos del vendedor (JOIN con users y profiles)
            u.email as vendedor_email,
            COALESCE(p.nombre_completo, u.email) as vendedor_nombre,
            p.telefono as vendedor_telefono,
            p.ciudad as vendedor_ubicacion,

            -- Datos de la raza (directo del gallo, sin JOIN)
            g.raza_id as raza_nombre,

            -- ¿Es favorito del usuario actual?
            CASE WHEN mf.id IS NOT NULL THEN true ELSE false END as es_favorito,

            -- Conteo de favoritos totales
            (SELECT COUNT(*) FROM marketplace_favoritos mf2 WHERE mf2.publicacion_id = mp.id) as total_favoritos

        FROM marketplace_publicaciones mp
        INNER JOIN gallos g ON mp.gallo_id = g.id
        INNER JOIN users u ON mp.user_id = u.id
        LEFT JOIN profiles p ON u.id = p.user_id
        LEFT JOIN marketplace_favoritos mf ON (mp.id = mf.publicacion_id AND mf.user_id = :current_user_id)

        WHERE 1=1
        """

        # Construir condiciones WHERE
        where_conditions = []
        params = {'current_user_id': current_user_id or 0}

        # Filtro por estado
        if estado:
            where_conditions.append("AND mp.estado = :estado")
            params['estado'] = estado

        # Filtros de precio
        if precio_min is not None:
            where_conditions.append("AND mp.precio >= :precio_min")
            params['precio_min'] = precio_min

        if precio_max is not None:
            where_conditions.append("AND mp.precio <= :precio_max")
            params['precio_max'] = precio_max

        # Filtro por raza
        if raza_id:
            where_conditions.append("AND g.raza_id = :raza_id")
            params['raza_id'] = raza_id

        # Filtros de peso del gallo
        if peso_min is not None:
            where_conditions.append("AND g.peso >= :peso_min")
            params['peso_min'] = peso_min

        if peso_max is not None:
            where_conditions.append("AND g.peso <= :peso_max")
            params['peso_max'] = peso_max

        # Filtro por color del gallo
        if color_gallo:
            where_conditions.append("AND LOWER(g.color) LIKE LOWER(:color_gallo)")
            params['color_gallo'] = f"%{color_gallo}%"

        # Filtros de fecha
        if fecha_desde:
            where_conditions.append("AND DATE(mp.fecha_publicacion) >= :fecha_desde")
            params['fecha_desde'] = fecha_desde

        if fecha_hasta:
            where_conditions.append("AND DATE(mp.fecha_publicacion) <= :fecha_hasta")
            params['fecha_hasta'] = fecha_hasta

        # Filtro de búsqueda
        if buscar:
            where_conditions.append("AND (LOWER(g.nombre) LIKE LOWER(:buscar) OR LOWER(g.codigo_identificacion) LIKE LOWER(:buscar))")
            params['buscar'] = f"%{buscar}%"

        # Construir query completo
        full_query = base_query + " ".join(where_conditions)

        # Ordenamiento
        if ordenar_por == "precio_asc":
            full_query += " ORDER BY mp.precio ASC"
        elif ordenar_por == "precio_desc":
            full_query += " ORDER BY mp.precio DESC"
        elif ordenar_por == "fecha_asc":
            full_query += " ORDER BY mp.fecha_publicacion ASC"
        else:  # fecha_desc (default)
            full_query += " ORDER BY mp.fecha_publicacion DESC"

        # Contar total
        count_query = f"""
        SELECT COUNT(*) as total
        FROM marketplace_publicaciones mp
        INNER JOIN gallos g ON mp.gallo_id = g.id
        WHERE 1=1 {" ".join(where_conditions)}
        """

        total_result = db.execute(text(count_query), params).first()
        total_registros = total_result.total if total_result else 0

        # Agregar paginación
        full_query += " LIMIT :limit OFFSET :skip"
        params['limit'] = limit
        params['skip'] = skip

        # Ejecutar query principal
        results = db.execute(text(full_query), params).fetchall()

        # Procesar resultados
        publicaciones = []
        for row in results:
            # Procesar fotos del gallo
            fotos_gallo = []
            if row.gallo_fotos_json:
                try:
                    fotos_parsed = json.loads(row.gallo_fotos_json) if isinstance(row.gallo_fotos_json, str) else row.gallo_fotos_json
                    if isinstance(fotos_parsed, list):
                        fotos_gallo = fotos_parsed
                except (json.JSONDecodeError, TypeError):
                    pass

            # Fallback a foto principal
            if not fotos_gallo and row.gallo_foto_principal:
                fotos_gallo = [{
                    "url": row.gallo_foto_principal,
                    "url_optimized": row.gallo_foto_optimizada or row.gallo_foto_principal,
                    "orden": 1,
                    "es_principal": True,
                    "descripcion": "Foto principal"
                }]

            publicacion = {
                "id": row.id,
                "user_id": row.user_id,
                "gallo_id": row.gallo_id,
                "precio": float(row.precio),
                "estado": row.estado,
                "fecha_publicacion": row.fecha_publicacion.isoformat() if row.fecha_publicacion else None,
                "icono_ejemplo": row.icono_ejemplo,
                "es_favorito": row.es_favorito,
                "total_favoritos": row.total_favoritos,
                "gallo_info": {
                    "id": row.gallo_id,
                    "nombre": row.gallo_nombre,
                    "codigo_identificacion": row.gallo_codigo,
                    "raza_id": row.gallo_raza_id,
                    "raza_nombre": row.raza_nombre,
                    "peso": float(row.gallo_peso) if row.gallo_peso else None,
                    "altura": row.gallo_altura,
                    "color": row.gallo_color,
                    "color_placa": row.gallo_color_placa,
                    "color_patas": row.gallo_color_patas,
                    "color_plumaje": row.gallo_color_plumaje,
                    "fecha_nacimiento": row.gallo_fecha_nacimiento.isoformat() if row.gallo_fecha_nacimiento else None,
                    "fotos_adicionales": fotos_gallo,
                    "total_fotos": len(fotos_gallo)
                },
                "vendedor_info": {
                    "user_id": row.user_id,
                    "nombre": row.vendedor_nombre,
                    "email": row.vendedor_email,
                    "telefono": row.vendedor_telefono,
                    "ubicacion": row.vendedor_ubicacion
                }
            }
            publicaciones.append(publicacion)

        return {
            "success": True,
            "data": {
                "publicaciones": publicaciones,
                "total": total_registros,
                "skip": skip,
                "limit": limit,
                "has_next": skip + limit < total_registros
            }
        }

    except Exception as e:
        logger.error(f"💥 Error listando publicaciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo publicaciones: {str(e)}"
        )


# ========================================
# ENDPOINTS PRIVADOS (MIS PUBLICACIONES)
# ========================================

@router.get("/mis-publicaciones", response_model=Dict[str, Any])
async def listar_mis_publicaciones(
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    estados: Optional[str] = Query(None, description="Filtrar por múltiples estados separados por coma"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🛒 LISTAR MIS PUBLICACIONES

    Solo muestra las publicaciones del usuario actual con datos del gallo
    """
    try:
        query = """
        SELECT
            mp.id, mp.user_id, mp.gallo_id, mp.precio, mp.estado,
            mp.fecha_publicacion, mp.icono_ejemplo, mp.created_at, mp.updated_at,
            g.nombre as gallo_nombre,
            g.codigo_identificacion as gallo_codigo,
            g.raza_id as gallo_raza_id,
            g.peso as gallo_peso,
            g.altura as gallo_altura,
            g.color as gallo_color,
            g.color_placa as gallo_color_placa,
            g.color_patas as gallo_color_patas,
            g.color_plumaje as gallo_color_plumaje,
            g.fecha_nacimiento as gallo_fecha_nacimiento,
            g.foto_principal_url as gallo_foto_principal,
            g.fotos_adicionales as gallo_fotos_json,
            (SELECT COUNT(*) FROM marketplace_favoritos mf WHERE mf.publicacion_id = mp.id) as total_favoritos
        FROM marketplace_publicaciones mp
        INNER JOIN gallos g ON mp.gallo_id = g.id
        WHERE mp.user_id = :user_id
        """

        params = {'user_id': current_user_id}

        # 🔥 NUEVO: Filtro por múltiples estados o estado único
        estado_filter = ""
        if estados:
            # Múltiples estados separados por coma
            estados_list = [estado.strip() for estado in estados.split(',')]
            # Manejar el caso de 'null' que debe ser IS NULL
            if 'null' in estados_list:
                otros_estados = [e for e in estados_list if e != 'null']
                if otros_estados:
                    estado_filter = f" AND (mp.estado IS NULL OR mp.estado IN ({','.join([f':estado_{i}' for i, _ in enumerate(otros_estados)])}))"
                    for i, est in enumerate(otros_estados):
                        params[f'estado_{i}'] = est
                else:
                    estado_filter = " AND mp.estado IS NULL"
            else:
                estado_filter = f" AND mp.estado IN ({','.join([f':estado_{i}' for i, _ in enumerate(estados_list)])})"
                for i, est in enumerate(estados_list):
                    params[f'estado_{i}'] = est
        elif estado:
            # Estado único (backward compatibility)
            if estado == 'null':
                estado_filter = " AND mp.estado IS NULL"
            else:
                estado_filter = " AND mp.estado = :estado"
                params['estado'] = estado

        query += estado_filter

        # Contar total
        count_query = f"SELECT COUNT(*) as total FROM marketplace_publicaciones mp WHERE mp.user_id = :user_id"
        count_query += estado_filter

        total_result = db.execute(text(count_query), params).first()
        total_registros = total_result.total

        # Agregar ordenamiento y paginación
        query += " ORDER BY mp.fecha_publicacion DESC LIMIT :limit OFFSET :skip"
        params['limit'] = limit
        params['skip'] = skip

        results = db.execute(text(query), params).fetchall()

        publicaciones = []
        for row in results:
            fotos_gallo = []
            if row.gallo_fotos_json:
                try:
                    fotos_parsed = json.loads(row.gallo_fotos_json) if isinstance(row.gallo_fotos_json, str) else row.gallo_fotos_json
                    if isinstance(fotos_parsed, list):
                        fotos_gallo = fotos_parsed
                except:
                    pass

            publicacion = {
                "id": row.id,
                "gallo_id": row.gallo_id,
                "precio": float(row.precio),
                "estado": row.estado,
                "fecha_publicacion": row.fecha_publicacion.isoformat() if row.fecha_publicacion else None,
                "icono_ejemplo": row.icono_ejemplo,
                "total_favoritos": row.total_favoritos,
                "gallo_info": {
                    "nombre": row.gallo_nombre,
                    "codigo_identificacion": row.gallo_codigo,
                    "raza_id": row.gallo_raza_id,
                    "peso": float(row.gallo_peso) if row.gallo_peso else None,
                    "altura": row.gallo_altura,
                    "color": row.gallo_color,
                    "color_placa": row.gallo_color_placa,
                    "color_patas": row.gallo_color_patas,
                    "color_plumaje": row.gallo_color_plumaje,
                    "fecha_nacimiento": row.gallo_fecha_nacimiento.isoformat() if row.gallo_fecha_nacimiento else None,
                    "foto_principal_url": row.gallo_foto_principal,
                    "fotos_adicionales": fotos_gallo,
                    "total_fotos": len(fotos_gallo)
                }
            }
            publicaciones.append(publicacion)

        return {
            "success": True,
            "data": {
                "publicaciones": publicaciones,
                "total": total_registros,
                "skip": skip,
                "limit": limit,
                "has_next": skip + limit < total_registros
            }
        }

    except Exception as e:
        logger.error(f"💥 Error listando mis publicaciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo mis publicaciones: {str(e)}"
        )


@router.post("/publicaciones", response_model=Dict[str, Any])
async def crear_publicacion(
    publicacion: MarketplacePublicacionCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🛒 CREAR NUEVA PUBLICACIÓN

    Crea una publicación desde un gallo existente del usuario
    Verifica límites del plan antes de crear
    """
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado o no tienes permisos"
            )

        # 2. Verificar límites del plan
        limites = await verificar_limites_marketplace(current_user_id, db)
        if not limites["puede_publicar"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Has alcanzado el límite de {limites['publicaciones_permitidas']} publicaciones de tu plan {limites['plan_nombre']}"
            )

        # 3. Verificar que el gallo no esté ya publicado en venta
        existe_query = text("""
            SELECT COUNT(*) as count
            FROM marketplace_publicaciones
            WHERE gallo_id = :gallo_id AND estado = 'venta'
        """)

        existe_result = db.execute(existe_query, {"gallo_id": publicacion.gallo_id}).first()
        if existe_result.count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este gallo ya tiene una publicación activa en el marketplace"
            )

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

        logger.info(f"✅ Publicación creada: ID {nueva_publicacion.id} para gallo {gallo_result.nombre}")

        return {
            "success": True,
            "message": "Publicación creada exitosamente",
            "data": {
                "publicacion_id": nueva_publicacion.id,
                "gallo_nombre": gallo_result.nombre,
                "precio": float(nueva_publicacion.precio),
                "estado": nueva_publicacion.estado,
                "fecha_publicacion": nueva_publicacion.fecha_publicacion.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"💥 Error creando publicación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando publicación: {str(e)}"
        )


@router.put("/publicaciones/{publicacion_id}", response_model=Dict[str, Any])
async def actualizar_publicacion(
    publicacion_id: int,
    publicacion: MarketplacePublicacionUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🛒 ACTUALIZAR PUBLICACIÓN

    Solo el propietario puede actualizar su publicación
    """
    try:
        # Buscar publicación
        pub_existente = db.query(MarketplacePublicacion).filter(
            MarketplacePublicacion.id == publicacion_id,
            MarketplacePublicacion.user_id == current_user_id
        ).first()

        if not pub_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada o no tienes permisos"
            )

        # Actualizar campos
        update_data = publicacion.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pub_existente, field, value)

        pub_existente.updated_by = current_user_id

        db.commit()
        db.refresh(pub_existente)

        return {
            "success": True,
            "message": "Publicación actualizada exitosamente",
            "data": pub_existente.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"💥 Error actualizando publicación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando publicación: {str(e)}"
        )


@router.delete("/publicaciones/{publicacion_id}", response_model=Dict[str, Any])
async def eliminar_publicacion(
    publicacion_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🛒 ELIMINAR PUBLICACIÓN

    Solo el propietario puede eliminar su publicación
    """
    try:
        pub_existente = db.query(MarketplacePublicacion).filter(
            MarketplacePublicacion.id == publicacion_id,
            MarketplacePublicacion.user_id == current_user_id
        ).first()

        if not pub_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada o no tienes permisos"
            )

        # Eliminar favoritos asociados primero
        db.query(MarketplaceFavorito).filter(
            MarketplaceFavorito.publicacion_id == publicacion_id
        ).delete()

        # Eliminar publicación
        db.delete(pub_existente)
        db.commit()

        return {
            "success": True,
            "message": "Publicación eliminada exitosamente"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"💥 Error eliminando publicación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando publicación: {str(e)}"
        )


# ========================================
# ENDPOINTS DE FAVORITOS
# ========================================

@router.post("/publicaciones/{publicacion_id}/favorito", response_model=Dict[str, Any])
async def marcar_favorito(
    publicacion_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    ⭐ MARCAR/DESMARCAR FAVORITO

    Si ya es favorito lo quita, si no lo agrega
    """
    try:
        # Verificar que la publicación existe
        publicacion = db.query(MarketplacePublicacion).filter(
            MarketplacePublicacion.id == publicacion_id
        ).first()

        if not publicacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada"
            )

        # Buscar favorito existente
        favorito_existente = db.query(MarketplaceFavorito).filter(
            MarketplaceFavorito.user_id == current_user_id,
            MarketplaceFavorito.publicacion_id == publicacion_id
        ).first()

        if favorito_existente:
            # Quitar favorito
            db.delete(favorito_existente)
            accion = "removido"
            es_favorito = False
        else:
            # Agregar favorito
            nuevo_favorito = MarketplaceFavorito(
                user_id=current_user_id,
                publicacion_id=publicacion_id
            )
            db.add(nuevo_favorito)
            accion = "agregado"
            es_favorito = True

        db.commit()

        return {
            "success": True,
            "message": f"Favorito {accion} exitosamente",
            "data": {
                "publicacion_id": publicacion_id,
                "es_favorito": es_favorito
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"💥 Error con favorito: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando favorito: {str(e)}"
        )


@router.get("/favoritos", response_model=Dict[str, Any])
async def listar_favoritos(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    ⭐ LISTAR MIS FAVORITOS

    Retorna las publicaciones marcadas como favoritas por el usuario
    """
    try:
        query = """
        SELECT
            mf.id as favorito_id,
            mf.created_at as fecha_favorito,
            mp.id as publicacion_id,
            mp.precio,
            mp.estado,
            mp.fecha_publicacion,
            g.nombre as gallo_nombre,
            g.codigo_identificacion as gallo_codigo,
            g.raza_id as gallo_raza_id,
            g.peso as gallo_peso,
            g.altura as gallo_altura,
            g.color as gallo_color,
            g.color_placa as gallo_color_placa,
            g.color_patas as gallo_color_patas,
            g.color_plumaje as gallo_color_plumaje,
            g.fecha_nacimiento as gallo_fecha_nacimiento,
            g.foto_principal_url as gallo_foto
        FROM marketplace_favoritos mf
        INNER JOIN marketplace_publicaciones mp ON mf.publicacion_id = mp.id
        INNER JOIN gallos g ON mp.gallo_id = g.id
        WHERE mf.user_id = :user_id
        ORDER BY mf.created_at DESC
        LIMIT :limit OFFSET :skip
        """

        # Contar total
        count_query = """
        SELECT COUNT(*) as total
        FROM marketplace_favoritos mf
        WHERE mf.user_id = :user_id
        """

        params = {
            'user_id': current_user_id,
            'limit': limit,
            'skip': skip
        }

        total_result = db.execute(text(count_query), params).first()
        total_registros = total_result.total

        results = db.execute(text(query), params).fetchall()

        favoritos = []
        for row in results:
            favorito = {
                "favorito_id": row.favorito_id,
                "fecha_favorito": row.fecha_favorito.isoformat() if row.fecha_favorito else None,
                "publicacion": {
                    "id": row.publicacion_id,
                    "precio": float(row.precio),
                    "estado": row.estado,
                    "fecha_publicacion": row.fecha_publicacion.isoformat() if row.fecha_publicacion else None,
                    "gallo_info": {
                        "nombre": row.gallo_nombre,
                        "codigo_identificacion": row.gallo_codigo,
                        "raza_id": row.gallo_raza_id,
                        "peso": float(row.gallo_peso) if row.gallo_peso else None,
                        "altura": row.gallo_altura,
                        "color": row.gallo_color,
                        "color_placa": row.gallo_color_placa,
                        "color_patas": row.gallo_color_patas,
                        "color_plumaje": row.gallo_color_plumaje,
                        "fecha_nacimiento": row.gallo_fecha_nacimiento.isoformat() if row.gallo_fecha_nacimiento else None,
                        "foto_principal_url": row.gallo_foto
                    }
                }
            }
            favoritos.append(favorito)

        return {
            "success": True,
            "data": {
                "favoritos": favoritos,
                "total": total_registros,
                "skip": skip,
                "limit": limit,
                "has_next": skip + limit < total_registros
            }
        }

    except Exception as e:
        logger.error(f"💥 Error listando favoritos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo favoritos: {str(e)}"
        )


# ========================================
# ENDPOINTS DE LÍMITES Y VALIDACIÓN
# ========================================

@router.get("/limites", response_model=Dict[str, Any])
async def obtener_limites_marketplace(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    📊 OBTENER LÍMITES DE MARKETPLACE DEL USUARIO

    Retorna información sobre límites del plan actual
    """
    try:
        limites = await verificar_limites_marketplace(current_user_id, db)

        return {
            "success": True,
            "data": limites
        }

    except Exception as e:
        logger.error(f"💥 Error obteniendo límites: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo límites: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def obtener_estadisticas_marketplace(
    db: Session = Depends(get_db)
):
    """
    📊 ESTADÍSTICAS GENERALES DEL MARKETPLACE

    Estadísticas públicas para todos los usuarios
    """
    try:
        query = """
        SELECT
            COUNT(*) as total_publicaciones,
            COUNT(CASE WHEN estado = 'venta' THEN 1 END) as publicaciones_activas,
            COUNT(CASE WHEN estado = 'vendido' THEN 1 END) as publicaciones_vendidas,
            COUNT(CASE WHEN estado = 'pausado' THEN 1 END) as publicaciones_pausadas,
            AVG(precio) as precio_promedio,
            MIN(precio) as precio_minimo,
            MAX(precio) as precio_maximo
        FROM marketplace_publicaciones
        """

        result = db.execute(text(query)).first()

        return {
            "success": True,
            "data": {
                "total_publicaciones": result.total_publicaciones,
                "publicaciones_activas": result.publicaciones_activas,
                "publicaciones_vendidas": result.publicaciones_vendidas,
                "publicaciones_pausadas": result.publicaciones_pausadas,
                "precio_promedio": float(result.precio_promedio) if result.precio_promedio else 0,
                "precio_minimo": float(result.precio_minimo) if result.precio_minimo else 0,
                "precio_maximo": float(result.precio_maximo) if result.precio_maximo else 0
            }
        }

    except Exception as e:
        logger.error(f"💥 Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )


# ========================================
# FUNCIONES AUXILIARES
# ========================================

async def verificar_limites_marketplace(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Función auxiliar para verificar límites del marketplace
    """
    try:
        # Obtener suscripción y plan actual
        suscripcion_query = """
        SELECT
            s.status as suscripcion_status,
            pc.codigo as plan_codigo,
            pc.nombre as plan_nombre,
            pc.marketplace_publicaciones_max as limite_publicaciones
        FROM suscripciones s
        INNER JOIN planes_catalogo pc ON s.plan_type = pc.codigo
        WHERE s.user_id = :user_id AND s.status = 'active'
        ORDER BY s.created_at DESC
        LIMIT 1
        """

        suscripcion_result = db.execute(text(suscripcion_query), {"user_id": user_id}).first()

        if not suscripcion_result:
            # Usuario sin suscripción activa, usar plan gratuito
            plan_gratuito = db.execute(text("""
                SELECT codigo, nombre, marketplace_publicaciones_max as limite_publicaciones
                FROM planes_catalogo
                WHERE codigo = 'gratuito'
            """)).first()

            if not plan_gratuito:
                raise HTTPException(status_code=500, detail="Plan gratuito no configurado")

            limite_publicaciones = plan_gratuito.limite_publicaciones
            plan_codigo = plan_gratuito.codigo
            plan_nombre = plan_gratuito.nombre
        else:
            limite_publicaciones = suscripcion_result.limite_publicaciones
            plan_codigo = suscripcion_result.plan_codigo
            plan_nombre = suscripcion_result.plan_nombre

        # Contar publicaciones activas del usuario
        count_query = """
        SELECT COUNT(*) as count
        FROM marketplace_publicaciones
        WHERE user_id = :user_id AND estado IN ('venta', 'pausado')
        """

        count_result = db.execute(text(count_query), {"user_id": user_id}).first()
        publicaciones_activas = count_result.count

        publicaciones_disponibles = max(0, limite_publicaciones - publicaciones_activas)
        puede_publicar = publicaciones_disponibles > 0

        return {
            "publicaciones_permitidas": limite_publicaciones,
            "publicaciones_activas": publicaciones_activas,
            "publicaciones_disponibles": publicaciones_disponibles,
            "puede_publicar": puede_publicar,
            "plan_codigo": plan_codigo,
            "plan_nombre": plan_nombre
        }

    except Exception as e:
        logger.error(f"💥 Error verificando límites: {str(e)}")
        raise e