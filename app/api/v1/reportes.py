# 📊🐓 API Endpoints Épicos para Reportes con Filtros (RÁPIDO)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, Optional
import logging
import time
from datetime import datetime

# Logger
logger = logging.getLogger("galloapp.reportes")
logger.setLevel(logging.INFO)

from app.database import get_db
from app.core.security import get_current_user_id

router = APIRouter(prefix="/reportes", tags=["📊 Reportes Épicos"])

# 🎯 ENDPOINT PRINCIPAL - DASHBOARD CON FILTROS
@router.get("/dashboard")
async def get_dashboard_filtrado(
    año: Optional[int] = Query(None, description="Año a filtrar (ej: 2024, 2025)"),
    mes: Optional[int] = Query(None, ge=1, le=12, description="Mes a filtrar (1-12)"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📊 Dashboard Épico con Filtros Dinámicos
    
    **Filtros disponibles:**
    - `año`: Año específico (ej: 2024, 2025). Si no se envía, usa año actual
    - `mes`: Mes específico (1-12). Si no se envía, usa mes actual
    
    **Ejemplos:**
    - `/reportes/dashboard` - Mes actual
    - `/reportes/dashboard?año=2024` - Todo el 2024 (mes actual del 2024)
    - `/reportes/dashboard?año=2024&mes=12` - Diciembre 2024
    - `/reportes/dashboard?mes=6` - Junio del año actual
    
    **Respuesta incluye:**
    - 📊 Resumen del período seleccionado
    - 💰 Finanzas del período
    - 🏆 Top gallos del período  
    - 📈 Evolución 6 meses desde el período
    """
    
    try:
        start_time = time.time()
        
        # 🎯 LLAMADA A LA FUNCIÓN CON FILTROS
        query = text("""
            SELECT get_dashboard_filtrado(:año, :mes, :user_id) as dashboard_data
        """)
        
        result = db.execute(query, {
            "año": año,
            "mes": mes, 
            "user_id": current_user_id
        }).fetchone()
        
        if not result or not result.dashboard_data:
            # 🆘 FALLBACK SIMPLE
            logger.warning(f"Dashboard filtrado falló para usuario {current_user_id}")
            
            return {
                "timestamp": time.time(),
                "error": "No hay datos para el período seleccionado",
                "filtros_aplicados": {
                    "año": año or datetime.now().year,
                    "mes": mes or datetime.now().month,
                    "user_id": current_user_id
                },
                "resumen_periodo": {
                    "total_gallos": 0,
                    "peleas_periodo": 0,
                    "ganadas_periodo": 0,
                    "efectividad_periodo": 0
                }
            }
        
        duration = time.time() - start_time
        logger.info(f"📊 Dashboard filtrado generado en {duration:.2f}s", extra={
            "user_id": current_user_id,
            "año": año,
            "mes": mes,
            "duration": duration
        })
        
        return result.dashboard_data
    
    except Exception as e:
        logger.error(f"Error en dashboard filtrado: {str(e)}", extra={
            "user_id": current_user_id,
            "año": año, 
            "mes": mes
        })
        raise HTTPException(
            status_code=500,
            detail=f"Error generando dashboard: {str(e)}"
        )

# 🏆 ENDPOINT RANKINGS CON FILTROS
@router.get("/rankings")
async def get_rankings_filtrado(
    tipo: str = Query("gallos", description="Tipo: gallos, padrillos, madres"),
    año: Optional[int] = Query(None, description="Filtrar por año"),
    mes: Optional[int] = Query(None, ge=1, le=12, description="Filtrar por mes"),
    limite: int = Query(10, ge=5, le=50, description="Número de resultados"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🏆 Rankings con Filtros de Período
    
    **Filtra rankings por:**
    - `año`: Solo peleas/datos del año especificado
    - `mes`: Solo del mes especificado 
    - `tipo`: gallos, padrillos, madres
    
    **Diferencia con dashboard:**
    - Dashboard: Métricas generales del período
    - Rankings: Top performers del período específico
    """
    
    try:
        # Construir filtros WHERE dinámicos
        filtro_fecha = ""
        params = {"user_id": current_user_id, "limite": limite}
        
        if año and mes:
            filtro_fecha = "AND EXTRACT(YEAR FROM p.fecha_pelea) = :año AND EXTRACT(MONTH FROM p.fecha_pelea) = :mes"
            params.update({"año": año, "mes": mes})
        elif año:
            filtro_fecha = "AND EXTRACT(YEAR FROM p.fecha_pelea) = :año"
            params["año"] = año
        elif mes:
            filtro_fecha = f"AND EXTRACT(MONTH FROM p.fecha_pelea) = :mes AND EXTRACT(YEAR FROM p.fecha_pelea) = {datetime.now().year}"
            params["mes"] = mes
        
        if tipo == "gallos":
            query = text(f"""
                WITH ranking_calculado AS (
                    SELECT 
                        ROW_NUMBER() OVER (ORDER BY ROUND(COALESCE(COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END)::numeric / NULLIF(COUNT(p.id), 0) * 100, 0), 1) DESC, COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END) DESC) as ranking,
                        g.id,
                        g.nombre,
                        g.raza_id,
                        g.codigo_identificacion,
                        COUNT(p.id) as total_peleas,
                        COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END) as peleas_ganadas,
                        ROUND(COALESCE(COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END)::numeric / NULLIF(COUNT(p.id), 0) * 100, 0), 1) as efectividad,
                        COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END) * 3000 as ingresos_estimados
                    FROM gallos g
                    LEFT JOIN peleas p ON g.id = p.gallo_id {filtro_fecha}
                    WHERE g.user_id = :user_id AND g.estado = 'activo'
                    GROUP BY g.id, g.nombre, g.raza_id, g.codigo_identificacion
                    HAVING COUNT(p.id) > 0
                    ORDER BY efectividad DESC, peleas_ganadas DESC
                    LIMIT :limite
                )
                SELECT json_agg(
                    json_build_object(
                        'ranking', ranking,
                        'id', id,
                        'nombre', nombre,
                        'raza_id', raza_id,
                        'codigo_identificacion', codigo_identificacion,
                        'total_peleas', total_peleas,
                        'peleas_ganadas', peleas_ganadas,
                        'efectividad', efectividad,
                        'ingresos_estimados', ingresos_estimados
                    )
                ) as ranking_data
                FROM ranking_calculado
            """)
            
        elif tipo == "padrillos":
            query = text(f"""
                WITH ranking_calculado AS (
                    SELECT 
                        ROW_NUMBER() OVER (ORDER BY ROUND(COALESCE(COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END)::numeric / NULLIF(COUNT(p.id), 0) * 100, 0), 1) DESC) as ranking,
                        padre.id,
                        padre.nombre,
                        padre.raza_id,
                        COUNT(DISTINCT h.id) as total_hijos,
                        COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END) as peleas_ganadas_hijos,
                        ROUND(COALESCE(COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END)::numeric / NULLIF(COUNT(p.id), 0) * 100, 0), 1) as efectividad
                    FROM gallos padre
                    LEFT JOIN gallos h ON h.padre_id = padre.id AND h.user_id = :user_id
                    LEFT JOIN peleas p ON h.id = p.gallo_id {filtro_fecha}
                    WHERE padre.user_id = :user_id AND padre.estado IN ('padre', 'activo')
                    GROUP BY padre.id, padre.nombre, padre.raza_id
                    HAVING COUNT(DISTINCT h.id) > 0 AND COUNT(p.id) > 0
                    ORDER BY efectividad DESC
                    LIMIT :limite
                )
                SELECT json_agg(
                    json_build_object(
                        'ranking', ranking,
                        'id', id,
                        'nombre', nombre,
                        'raza_id', raza_id,
                        'total_hijos', total_hijos,
                        'peleas_ganadas_hijos', peleas_ganadas_hijos,
                        'efectividad', efectividad
                    )
                ) as ranking_data
                FROM ranking_calculado
            """)
            
        elif tipo == "madres":
            query = text(f"""
                WITH ranking_calculado AS (
                    SELECT 
                        ROW_NUMBER() OVER (ORDER BY ROUND(COALESCE(COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END)::numeric / NULLIF(COUNT(p.id), 0) * 100, 0), 1) DESC) as ranking,
                        madre.id,
                        madre.nombre,
                        madre.raza_id,
                        COUNT(DISTINCT h.id) as total_hijos,
                        COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END) as peleas_ganadas_hijos,
                        ROUND(COALESCE(COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END)::numeric / NULLIF(COUNT(p.id), 0) * 100, 0), 1) as efectividad
                    FROM gallos madre
                    LEFT JOIN gallos h ON h.madre_id = madre.id AND h.user_id = :user_id
                    LEFT JOIN peleas p ON h.id = p.gallo_id {filtro_fecha}
                    WHERE madre.user_id = :user_id AND madre.estado IN ('madre', 'activo')
                    GROUP BY madre.id, madre.nombre, madre.raza_id
                    HAVING COUNT(DISTINCT h.id) > 0 AND COUNT(p.id) > 0
                    ORDER BY efectividad DESC
                    LIMIT :limite
                )
                SELECT json_agg(
                    json_build_object(
                        'ranking', ranking,
                        'id', id,
                        'nombre', nombre,
                        'raza_id', raza_id,
                        'total_hijos', total_hijos,
                        'peleas_ganadas_hijos', peleas_ganadas_hijos,
                        'efectividad', efectividad
                    )
                ) as ranking_data
                FROM ranking_calculado
            """)
        else:
            raise HTTPException(400, f"Tipo '{tipo}' no válido")
        
        result = db.execute(query, params).fetchone()
        
        # Procesar datos para compatibilidad con Flutter
        items_data = result.ranking_data if result and result.ranking_data else []
        
        # Mapear campos al formato esperado por Flutter
        items_flutter = []
        if items_data:
            for item in items_data:
                flutter_item = {
                    "id": item.get("id"),
                    "nombre": item.get("nombre"),
                    "raza": None,  # Se llenará desde raza_id si es necesario
                    "codigo": item.get("codigo_identificacion"),
                    "peleas_periodo": item.get("total_peleas", 0),
                    "ganadas_periodo": item.get("peleas_ganadas", item.get("peleas_ganadas_hijos", 0)),
                    "topes_periodo": 0,  # No incluido en ranking por ahora
                    "efectividad_periodo": item.get("efectividad", 0),
                    "posicion": item.get("ranking", 0)
                }
                items_flutter.append(flutter_item)
        
        return {
            "tipo": tipo,
            "timestamp": time.time(),
            "estadisticas": {
                "total_items": len(items_flutter),
                "total_peleas": sum(item["peleas_periodo"] for item in items_flutter),
                "total_ganadas": sum(item["ganadas_periodo"] for item in items_flutter),
                "efectividad_promedio": sum(item["efectividad_periodo"] for item in items_flutter) / len(items_flutter) if items_flutter else 0,
                "total_topes": 0
            },
            "items": items_flutter
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en rankings filtrado: {str(e)}")
        raise HTTPException(500, f"Error obteniendo rankings: {str(e)}")

# 📅 ENDPOINT PERÍODOS DISPONIBLES
@router.get("/periodos-disponibles")
async def get_periodos_disponibles(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📅 Obtener períodos con datos disponibles
    
    **Utilidad:**
    - Frontend puede mostrar solo años/meses que tengan datos
    - Evita filtros vacíos
    - Mejora UX del usuario
    """
    
    try:
        query = text("""
            WITH periodos_peleas AS (
                SELECT DISTINCT 
                    EXTRACT(YEAR FROM p.fecha_pelea) as año,
                    EXTRACT(MONTH FROM p.fecha_pelea) as mes,
                    TO_CHAR(p.fecha_pelea, 'Month YYYY') as nombre_periodo,
                    COUNT(*) as total_peleas
                FROM peleas p
                JOIN gallos g ON p.gallo_id = g.id
                WHERE g.user_id = :user_id
                GROUP BY EXTRACT(YEAR FROM p.fecha_pelea), EXTRACT(MONTH FROM p.fecha_pelea), TO_CHAR(p.fecha_pelea, 'Month YYYY')
                ORDER BY año DESC, mes DESC
            ),
            
            años_disponibles AS (
                SELECT DISTINCT año, COUNT(*) as meses_con_datos
                FROM periodos_peleas
                GROUP BY año
                ORDER BY año DESC
            )
            
            SELECT json_build_object(
                'años_disponibles', (
                    SELECT json_agg(
                        json_build_object(
                            'año', año,
                            'meses_con_datos', meses_con_datos
                        ) ORDER BY año DESC
                    ) FROM años_disponibles
                ),
                'periodos_detallados', (
                    SELECT json_agg(
                        json_build_object(
                            'año', año,
                            'mes', mes,
                            'nombre_periodo', nombre_periodo,
                            'total_peleas', total_peleas
                        ) ORDER BY año DESC, mes DESC
                    ) FROM periodos_peleas
                ),
                'periodo_actual', json_build_object(
                    'año', EXTRACT(YEAR FROM CURRENT_DATE),
                    'mes', EXTRACT(MONTH FROM CURRENT_DATE),
                    'nombre', TO_CHAR(CURRENT_DATE, 'Month YYYY')
                )
            ) as periodos_data
        """)
        
        result = db.execute(query, {"user_id": current_user_id}).fetchone()
        
        return result.periodos_data if result else {
            "años_disponibles": [],
            "periodos_detallados": [],
            "periodo_actual": {
                "año": datetime.now().year,
                "mes": datetime.now().month,
                "nombre": datetime.now().strftime("%B %Y")
            }
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo períodos: {str(e)}")
        raise HTTPException(500, f"Error obteniendo períodos: {str(e)}")

# 🧪 ENDPOINT TEST
@router.get("/test")
async def test_reportes():
    """🧪 Test del módulo de reportes con filtros"""
    return {
        "status": "ok",
        "modulo": "Reportes Épicos con Filtros",
        "version": "1.0-FILTRABLE",
        "timestamp": time.time(),
        "endpoints": [
            "GET /reportes/dashboard?año=2024&mes=12",
            "GET /reportes/rankings?tipo=gallos&año=2024", 
            "GET /reportes/periodos-disponibles"
        ]
    }