# app/api/v1/vacunas.py - VACUNAS ÉPICAS MONOLITO
from fastapi import APIRouter, Depends, HTTPException, Query, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from app.database import get_db
from app.core.security import get_current_user_id

router = APIRouter()

# 💉 MOCK DE TIPOS DE VACUNAS
TIPOS_VACUNAS = {
    'NEW01': {
        'codigo': 'NEW01',
        'nombre': 'Newcastle',
        'enfermedad': 'Enfermedad de Newcastle',
        'metodo': 'IM',
        'dosis': '0.5ml',
        'duracion_dias': 180,
        'color': '#2196f3'
    },
    'BRON01': {
        'codigo': 'BRON01', 
        'nombre': 'Bronquitis Infecciosa',
        'enfermedad': 'Bronquitis Infecciosa',
        'metodo': 'IM',
        'dosis': '0.5ml',
        'duracion_dias': 180,
        'color': '#e91e63'
    },
    'VIR01': {
        'codigo': 'VIR01',
        'nombre': 'Viruela Aviar', 
        'enfermedad': 'Viruela de las Aves',
        'metodo': 'puncion',
        'dosis': '1 punción',
        'duracion_dias': 730,
        'color': '#ff9800'
    },
    'GUM01': {
        'codigo': 'GUM01',
        'nombre': 'Gumboro',
        'enfermedad': 'Enfermedad de Gumboro', 
        'metodo': 'SC',
        'dosis': '0.5ml',
        'duracion_dias': 365,
        'color': '#f44336'
    },
    'COR01': {
        'codigo': 'COR01',
        'nombre': 'Coriza Infecciosa',
        'enfermedad': 'Coriza Infecciosa',
        'metodo': 'IM', 
        'dosis': '0.5ml',
        'duracion_dias': 180,
        'color': '#607d8b'
    },
    'SAL01': {
        'codigo': 'SAL01',
        'nombre': 'Salmonella',
        'enfermedad': 'Salmonelosis',
        'metodo': 'SC',
        'dosis': '0.5ml', 
        'duracion_dias': 365,
        'color': '#9c27b0'
    },
    'MAR01': {
        'codigo': 'MAR01',
        'nombre': 'Marek',
        'enfermedad': 'Enfermedad de Marek',
        'metodo': 'SC',
        'dosis': '0.2ml',
        'duracion_dias': 3650,
        'color': '#4caf50'
    },
    'LAR01': {
        'codigo': 'LAR01',
        'nombre': 'Laringotraqueitis',
        'enfermedad': 'Laringotraqueitis Infecciosa',
        'metodo': 'ocular',
        'dosis': '1 gota',
        'duracion_dias': 365,
        'color': '#ff5722'
    }
}

def enriquecer_vacuna_con_tipo(vacuna_data, tipo_codigo):
    """Enriquecer datos de vacuna con información del tipo"""
    tipo_info = TIPOS_VACUNAS.get(tipo_codigo, {})
    return {
        **vacuna_data,
        'tipo_info': tipo_info
    }

# 🏷️ ENDPOINT TIPOS DE VACUNAS
@router.get("/tipos", response_model=List[Dict[str, Any]])
async def get_tipos_vacunas():
    """🏷️ Obtener todos los tipos de vacunas disponibles"""
    return list(TIPOS_VACUNAS.values())

# 📊 ENDPOINT ESTADÍSTICAS 
@router.get("/stats", response_model=Dict[str, Any])
async def get_vaccination_stats(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📊 Obtener estadísticas generales de vacunación"""
    try:
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
        raise HTTPException(status_code=500, detail=f"Error estadísticas: {str(e)}")

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
                (v.proxima_dosis - CURRENT_DATE) as dias_restantes
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
        
        proximas = []
        for row in result:
            dias = row.dias_restantes
            estado = "urgente" if dias <= 2 else "proximo" if dias <= 7 else "normal"
            
            vacuna_data = {
                "gallo_id": row.gallo_id,
                "gallo_nombre": row.gallo_nombre,
                "tipo_vacuna": row.tipo_vacuna,
                "proxima_dosis": row.proxima_dosis.isoformat(),
                "dias_restantes": dias,
                "estado": estado
            }
            
            proximas.append(enriquecer_vacuna_con_tipo(vacuna_data, row.tipo_vacuna))
        
        return proximas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error próximas vacunas: {str(e)}")

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
        where_conditions = ["g.user_id = :user_id"]
        params = {"user_id": current_user_id, "offset": skip, "limit": limit}
        
        if gallo_id:
            where_conditions.append("v.gallo_id = :gallo_id")
            params["gallo_id"] = gallo_id
            
        if tipo_vacuna:
            where_conditions.append("v.tipo_vacuna = :tipo_vacuna")
            params["tipo_vacuna"] = tipo_vacuna
        
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
        
        vacunas = []
        for row in result:
            vacuna_data = {
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
            
            vacunas.append(enriquecer_vacuna_con_tipo(vacuna_data, row.tipo_vacuna))
        
        return vacunas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listar vacunas: {str(e)}")

# ➕ CREAR VACUNA
@router.post("", response_model=Dict[str, Any])
async def create_vacuna(
    gallo_id: int = Form(...),
    tipo_vacuna: str = Form(...),
    fecha_aplicacion: date = Form(...),
    laboratorio: Optional[str] = Form(None),
    proxima_dosis: Optional[date] = Form(None),
    veterinario_nombre: Optional[str] = Form(None),
    clinica: Optional[str] = Form(None),
    dosis: Optional[str] = Form(None),
    notas: Optional[str] = Form(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """➕ Crear nuevo registro de vacuna"""
    try:
        # Verificar tipo válido
        if tipo_vacuna not in TIPOS_VACUNAS:
            raise HTTPException(status_code=400, detail=f"Tipo de vacuna inválido: {tipo_vacuna}")
        
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
            raise HTTPException(status_code=404, detail="Gallo no encontrado")
        
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
            "id": vacuna_id,
            "tipo_info": TIPOS_VACUNAS[tipo_vacuna]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error crear vacuna: {str(e)}")

# ✏️ ACTUALIZAR VACUNA
@router.put("/{vacuna_id}", response_model=Dict[str, Any])
async def update_vacuna(
    vacuna_id: int,
    gallo_id: Optional[int] = Form(None),
    tipo_vacuna: Optional[str] = Form(None),
    fecha_aplicacion: Optional[date] = Form(None),
    laboratorio: Optional[str] = Form(None),
    proxima_dosis: Optional[date] = Form(None),
    veterinario_nombre: Optional[str] = Form(None),
    clinica: Optional[str] = Form(None),
    dosis: Optional[str] = Form(None),
    notas: Optional[str] = Form(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """✏️ Actualizar registro de vacuna existente"""
    try:
        # Verificar que la vacuna existe y pertenece al usuario
        verify_query = text("""
            SELECT v.id FROM vacunas v
            JOIN gallos g ON v.gallo_id = g.id
            WHERE v.id = :vacuna_id AND g.user_id = :user_id
        """)
        
        vacuna_check = db.execute(verify_query, {
            "vacuna_id": vacuna_id,
            "user_id": current_user_id
        }).fetchone()
        
        if not vacuna_check:
            raise HTTPException(status_code=404, detail="Vacuna no encontrada")
        
        # Construir campos a actualizar dinámicamente
        set_fields = []
        update_params = {"vacuna_id": vacuna_id}
        
        if gallo_id is not None:
            # Verificar que el nuevo gallo pertenece al usuario
            gallo_query = text("SELECT id FROM gallos WHERE id = :gallo_id AND user_id = :user_id")
            gallo_check = db.execute(gallo_query, {"gallo_id": gallo_id, "user_id": current_user_id}).fetchone()
            if not gallo_check:
                raise HTTPException(status_code=404, detail="Gallo no encontrado")
            set_fields.append("gallo_id = :gallo_id")
            update_params["gallo_id"] = gallo_id
            
        if tipo_vacuna is not None:
            if tipo_vacuna not in TIPOS_VACUNAS:
                raise HTTPException(status_code=400, detail=f"Tipo de vacuna inválido: {tipo_vacuna}")
            set_fields.append("tipo_vacuna = :tipo_vacuna")
            update_params["tipo_vacuna"] = tipo_vacuna
            
        if fecha_aplicacion is not None:
            set_fields.append("fecha_aplicacion = :fecha_aplicacion")
            update_params["fecha_aplicacion"] = fecha_aplicacion
            
        if laboratorio is not None:
            set_fields.append("laboratorio = :laboratorio")
            update_params["laboratorio"] = laboratorio
            
        if proxima_dosis is not None:
            set_fields.append("proxima_dosis = :proxima_dosis")
            update_params["proxima_dosis"] = proxima_dosis
            
        if veterinario_nombre is not None:
            set_fields.append("veterinario_nombre = :veterinario_nombre")
            update_params["veterinario_nombre"] = veterinario_nombre
            
        if clinica is not None:
            set_fields.append("clinica = :clinica")
            update_params["clinica"] = clinica
            
        if dosis is not None:
            set_fields.append("dosis = :dosis")
            update_params["dosis"] = dosis
            
        if notas is not None:
            set_fields.append("notas = :notas")
            update_params["notas"] = notas
        
        if not set_fields:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
        # Ejecutar actualización
        set_clause = ", ".join(set_fields)
        update_query = text(f"""
            UPDATE vacunas 
            SET {set_clause}
            WHERE id = :vacuna_id
            RETURNING tipo_vacuna
        """)
        
        result = db.execute(update_query, update_params)
        updated_tipo = result.fetchone()
        db.commit()
        
        return {
            "success": True,
            "message": "Vacuna actualizada exitosamente",
            "id": vacuna_id,
            "tipo_info": TIPOS_VACUNAS.get(updated_tipo.tipo_vacuna, {}) if updated_tipo else {}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error actualizar vacuna: {str(e)}")

# 🗑️ ELIMINAR VACUNA
@router.delete("/{vacuna_id}", response_model=Dict[str, Any])
async def delete_vacuna(
    vacuna_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🗑️ Eliminar registro de vacuna"""
    try:
        # Verificar que la vacuna existe y pertenece al usuario
        verify_query = text("""
            SELECT v.id FROM vacunas v
            JOIN gallos g ON v.gallo_id = g.id
            WHERE v.id = :vacuna_id AND g.user_id = :user_id
        """)
        
        vacuna_check = db.execute(verify_query, {
            "vacuna_id": vacuna_id,
            "user_id": current_user_id
        }).fetchone()
        
        if not vacuna_check:
            raise HTTPException(status_code=404, detail="Vacuna no encontrada")
        
        # Eliminar vacuna
        delete_query = text("DELETE FROM vacunas WHERE id = :vacuna_id")
        db.execute(delete_query, {"vacuna_id": vacuna_id})
        db.commit()
        
        return {
            "success": True,
            "message": "Vacuna eliminada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error eliminar vacuna: {str(e)}")

# ⚡ REGISTRO RÁPIDO
@router.post("/registro-rapido", response_model=Dict[str, Any])
async def registro_rapido_vacunas(
    gallo_ids: str = Form(..., description="IDs separados por comas"),
    tipo_vacunas: str = Form(..., description="Códigos separados por comas"),
    fecha_aplicacion: date = Form(...),
    veterinario_nombre: Optional[str] = Form(None),
    clinica: Optional[str] = Form(None),
    dosis: Optional[str] = Form(None),
    proxima_dosis: Optional[date] = Form(None),
    notas: Optional[str] = Form(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """⚡ Registro rápido de múltiples vacunas"""
    try:
        # Convertir strings a listas
        gallo_ids_list = [int(x.strip()) for x in gallo_ids.split(',')]
        tipo_vacunas_list = [x.strip() for x in tipo_vacunas.split(',')]
        
        # Verificar tipos válidos
        for tipo in tipo_vacunas_list:
            if tipo not in TIPOS_VACUNAS:
                raise HTTPException(status_code=400, detail=f"Tipo inválido: {tipo}")
        
        # Verificar gallos
        verify_query = text("""
            SELECT id FROM gallos 
            WHERE id = ANY(:gallo_ids) AND user_id = :user_id
        """)
        
        gallos_check = db.execute(verify_query, {
            "gallo_ids": gallo_ids_list,
            "user_id": current_user_id
        }).fetchall()
        
        if len(gallos_check) != len(gallo_ids_list):
            raise HTTPException(status_code=404, detail="Algunos gallos no pertenecen al usuario")
        
        registros_creados = 0
        
        # Crear registros para cada combinación
        for gallo_id in gallo_ids_list:
            for tipo_vacuna in tipo_vacunas_list:
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
            "message": f"Se crearon {registros_creados} registros",
            "registros_creados": registros_creados,
            "gallos": len(gallo_ids_list),
            "tipos_vacunas": len(tipo_vacunas_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error registro rápido: {str(e)}")

# 📊 HISTORIAL POR GALLO
@router.get("/gallo/{gallo_id}/historial", response_model=List[Dict[str, Any]])
async def get_historial_gallo(
    gallo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📊 Historial completo de vacunas de un gallo"""
    try:
        # Verificar gallo
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
        
        historial = []
        for row in result:
            vacuna_data = {
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
            
            historial.append(enriquecer_vacuna_con_tipo(vacuna_data, row.tipo_vacuna))
        
        return historial
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error historial: {str(e)}")