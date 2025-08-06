# app/api/v1/vacunas_simple.py - SIGUIENDO PATRÓN EXISTENTE
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta
from app.database import get_db
from app.core.security import get_current_user_id

router = APIRouter()

# 📊 ESTADÍSTICAS DE VACUNAS
@router.get("/stats", response_model=Dict[str, Any])
async def get_vaccination_stats(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📊 Obtener estadísticas generales de vacunación"""
    try:
        # Consulta SQL directa como en gallos_con_pedigri
        query = text("""
            SELECT 
                COUNT(*) as total_vacunas,
                COUNT(CASE WHEN DATE_TRUNC('month', fecha_aplicacion) = DATE_TRUNC('month', CURRENT_DATE) THEN 1 END) as vacunas_este_mes,
                COUNT(CASE WHEN proxima_dosis BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days' THEN 1 END) as proximas_vacunas,
                COUNT(CASE WHEN proxima_dosis < CURRENT_DATE THEN 1 END) as vacunas_vencidas
            FROM vacunas v
            JOIN gallos g ON v.gallo_id = g.id 
            WHERE g.user_id = :user_id
        """)
        
        result = db.execute(query, {"user_id": current_user_id}).fetchone()
        
        return {
            "total_vacunas": result.total_vacunas or 0,
            "vacunas_este_mes": result.vacunas_este_mes or 0,
            "proximas_vacunas": result.proximas_vacunas or 0,
            "vacunas_vencidas": result.vacunas_vencidas or 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

# 🔜 PRÓXIMAS VACUNAS
@router.get("/proximas", response_model=List[Dict[str, Any]])
async def get_proximas_vacunas(
    dias_adelante: int = Query(30, description="Días hacia adelante"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🔜 Obtener próximas vacunas pendientes"""
    try:
        query = text("""
            SELECT 
                v.gallo_id,
                g.nombre as gallo_nombre,
                v.tipo_vacuna,
                v.proxima_dosis,
                (v.proxima_dosis - CURRENT_DATE) as dias_restantes,
                CASE 
                    WHEN (v.proxima_dosis - CURRENT_DATE) <= 2 THEN 'urgente'
                    WHEN (v.proxima_dosis - CURRENT_DATE) <= 7 THEN 'proximo'
                    ELSE 'normal'
                END as estado
            FROM vacunas v
            JOIN gallos g ON v.gallo_id = g.id
            WHERE g.user_id = :user_id 
                AND v.proxima_dosis BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL ':dias days'
            ORDER BY v.proxima_dosis ASC
        """)
        
        result = db.execute(query, {
            "user_id": current_user_id,
            "dias": dias_adelante
        }).fetchall()
        
        return [
            {
                "gallo_id": row.gallo_id,
                "gallo_nombre": row.gallo_nombre,
                "tipo_vacuna": row.tipo_vacuna,
                "proxima_dosis": row.proxima_dosis.isoformat(),
                "dias_restantes": row.dias_restantes,
                "estado": row.estado
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener próximas vacunas: {str(e)}")

# 📋 LISTAR VACUNAS
@router.get("", response_model=List[Dict[str, Any]])
async def get_vacunas(
    skip: int = Query(0),
    limit: int = Query(100),
    gallo_id: Optional[int] = Query(None),
    tipo_vacuna: Optional[str] = Query(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Obtener lista de vacunas del usuario"""
    try:
        # Construir WHERE dinámico
        where_conditions = ["g.user_id = :user_id"]
        params = {"user_id": current_user_id, "offset": skip, "limit": limit}
        
        if gallo_id:
            where_conditions.append("v.gallo_id = :gallo_id")
            params["gallo_id"] = gallo_id
            
        if tipo_vacuna:
            where_conditions.append("v.tipo_vacuna ILIKE :tipo_vacuna")
            params["tipo_vacuna"] = f"%{tipo_vacuna}%"
        
        where_clause = " AND ".join(where_conditions)
        
        query = text(f"""
            SELECT 
                v.id,
                v.gallo_id,
                g.nombre as gallo_nombre,
                g.codigo_identificacion as gallo_codigo,
                v.tipo_vacuna,
                v.laboratorio,
                v.fecha_aplicacion,
                v.proxima_dosis,
                v.veterinario_nombre,
                v.clinica,
                v.dosis,
                v.notas,
                v.created_at
            FROM vacunas v
            JOIN gallos g ON v.gallo_id = g.id
            WHERE {where_clause}
            ORDER BY v.fecha_aplicacion DESC
            OFFSET :offset LIMIT :limit
        """)
        
        result = db.execute(query, params).fetchall()
        
        return [
            {
                "id": row.id,
                "gallo_id": row.gallo_id,
                "gallo_nombre": row.gallo_nombre,
                "gallo_codigo": row.gallo_codigo,
                "tipo_vacuna": row.tipo_vacuna,
                "laboratorio": row.laboratorio,
                "fecha_aplicacion": row.fecha_aplicacion.isoformat() if row.fecha_aplicacion else None,
                "proxima_dosis": row.proxima_dosis.isoformat() if row.proxima_dosis else None,
                "veterinario_nombre": row.veterinario_nombre,
                "clinica": row.clinica,
                "dosis": row.dosis,
                "notas": row.notas,
                "created_at": row.created_at.isoformat() if row.created_at else None
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener vacunas: {str(e)}")

# ➕ CREAR VACUNA
@router.post("", response_model=Dict[str, Any])
async def create_vacuna(
    gallo_id: int,
    tipo_vacuna: str,
    fecha_aplicacion: date,
    laboratorio: Optional[str] = None,
    proxima_dosis: Optional[date] = None,
    veterinario_nombre: Optional[str] = None,
    clinica: Optional[str] = None,
    dosis: Optional[str] = None,
    notas: Optional[str] = None,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """➕ Crear nuevo registro de vacuna"""
    try:
        # Verificar que el gallo pertenece al usuario
        verify_query = text("""
            SELECT id FROM gallos 
            WHERE id = :gallo_id AND user_id = :user_id
        """)
        
        gallo_check = db.execute(verify_query, {
            "gallo_id": gallo_id,
            "user_id": current_user_id
        }).fetchone()
        
        if not gallo_check:
            raise HTTPException(status_code=404, detail="Gallo no encontrado o no pertenece al usuario")
        
        # Insertar vacuna
        insert_query = text("""
            INSERT INTO vacunas (
                gallo_id, tipo_vacuna, laboratorio, fecha_aplicacion, 
                proxima_dosis, veterinario_nombre, clinica, dosis, notas
            ) VALUES (
                :gallo_id, :tipo_vacuna, :laboratorio, :fecha_aplicacion,
                :proxima_dosis, :veterinario_nombre, :clinica, :dosis, :notas
            ) RETURNING id
        """)
        
        result = db.execute(insert_query, {
            "gallo_id": gallo_id,
            "tipo_vacuna": tipo_vacuna,
            "laboratorio": laboratorio,
            "fecha_aplicacion": fecha_aplicacion,
            "proxima_dosis": proxima_dosis,
            "veterinario_nombre": veterinario_nombre,
            "clinica": clinica,
            "dosis": dosis,
            "notas": notas
        })
        
        vacuna_id = result.fetchone().id
        db.commit()
        
        return {
            "success": True,
            "message": "Vacuna creada exitosamente",
            "id": vacuna_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear vacuna: {str(e)}")

# ⚡ REGISTRO RÁPIDO
@router.post("/registro-rapido", response_model=Dict[str, Any])
async def registro_rapido_vacunas(
    gallo_ids: List[int],
    tipo_vacunas: List[str],
    fecha_aplicacion: date,
    veterinario_nombre: Optional[str] = None,
    clinica: Optional[str] = None,
    dosis: Optional[str] = None,
    proxima_dosis: Optional[date] = None,
    notas: Optional[str] = None,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """⚡ Registro rápido de múltiples vacunas"""
    try:
        # Verificar que todos los gallos pertenecen al usuario
        verify_query = text("""
            SELECT id FROM gallos 
            WHERE id = ANY(:gallo_ids) AND user_id = :user_id
        """)
        
        gallos_check = db.execute(verify_query, {
            "gallo_ids": gallo_ids,
            "user_id": current_user_id
        }).fetchall()
        
        if len(gallos_check) != len(gallo_ids):
            raise HTTPException(status_code=404, detail="Algunos gallos no pertenecen al usuario")
        
        registros_creados = 0
        
        # Crear registros para cada combinación gallo-vacuna
        for gallo_id in gallo_ids:
            for tipo_vacuna in tipo_vacunas:
                insert_query = text("""
                    INSERT INTO vacunas (
                        gallo_id, tipo_vacuna, fecha_aplicacion, 
                        veterinario_nombre, clinica, dosis, proxima_dosis, notas
                    ) VALUES (
                        :gallo_id, :tipo_vacuna, :fecha_aplicacion,
                        :veterinario_nombre, :clinica, :dosis, :proxima_dosis, :notas
                    )
                """)
                
                db.execute(insert_query, {
                    "gallo_id": gallo_id,
                    "tipo_vacuna": tipo_vacuna,
                    "fecha_aplicacion": fecha_aplicacion,
                    "veterinario_nombre": veterinario_nombre,
                    "clinica": clinica,
                    "dosis": dosis,
                    "proxima_dosis": proxima_dosis,
                    "notas": notas
                })
                registros_creados += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Se crearon {registros_creados} registros de vacunación",
            "registros_creados": registros_creados,
            "gallos": len(gallo_ids),
            "vacunas": len(tipo_vacunas)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en registro rápido: {str(e)}")

# 📊 HISTORIAL POR GALLO
@router.get("/gallo/{gallo_id}/historial", response_model=List[Dict[str, Any]])
async def get_historial_gallo(
    gallo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📊 Obtener historial completo de vacunas de un gallo"""
    try:
        # Verificar que el gallo pertenece al usuario
        verify_query = text("""
            SELECT nombre FROM gallos 
            WHERE id = :gallo_id AND user_id = :user_id
        """)
        
        gallo_check = db.execute(verify_query, {
            "gallo_id": gallo_id,
            "user_id": current_user_id
        }).fetchone()
        
        if not gallo_check:
            raise HTTPException(status_code=404, detail="Gallo no encontrado")
        
        # Obtener historial
        query = text("""
            SELECT 
                id, tipo_vacuna, laboratorio, fecha_aplicacion,
                proxima_dosis, veterinario_nombre, clinica, dosis, notas, created_at
            FROM vacunas 
            WHERE gallo_id = :gallo_id
            ORDER BY fecha_aplicacion DESC
        """)
        
        result = db.execute(query, {"gallo_id": gallo_id}).fetchall()
        
        return [
            {
                "id": row.id,
                "tipo_vacuna": row.tipo_vacuna,
                "laboratorio": row.laboratorio,
                "fecha_aplicacion": row.fecha_aplicacion.isoformat() if row.fecha_aplicacion else None,
                "proxima_dosis": row.proxima_dosis.isoformat() if row.proxima_dosis else None,
                "veterinario_nombre": row.veterinario_nombre,
                "clinica": row.clinica,
                "dosis": row.dosis,
                "notas": row.notas,
                "created_at": row.created_at.isoformat() if row.created_at else None
            }
            for row in result
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")