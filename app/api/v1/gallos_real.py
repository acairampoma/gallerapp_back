# 🐓 app/api/v1/gallos_real.py - ENDPOINTS REALES CON POSTGRESQL
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

from app.database import get_db
from app.core.security import get_current_user_id

router = APIRouter()

# ========================================
# 🐓 CRUD REAL DE GALLOS
# ========================================

@router.get("", response_model=dict)
async def list_gallos_real(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Listar TODOS los gallos REALES del usuario"""
    
    try:
        # Query SQL directo para obtener gallos del usuario
        query = text("""
            SELECT g.*, r.nombre as raza_nombre 
            FROM gallos g 
            LEFT JOIN razas r ON g.raza_id = r.id 
            WHERE g.user_id = :user_id 
            ORDER BY g.created_at DESC
        """)
        
        result = db.execute(query, {"user_id": current_user_id})
        gallos_raw = result.fetchall()
        
        # Convertir a dict
        gallos_data = []
        for row in gallos_raw:
            gallos_data.append({
                "id": row.id,
                "nombre": row.nombre,
                "codigo_identificacion": row.codigo_identificacion,
                "raza_id": row.raza_id,
                "raza_nombre": row.raza_nombre,
                "fecha_nacimiento": row.fecha_nacimiento.isoformat() if row.fecha_nacimiento else None,
                "peso": float(row.peso) if row.peso else None,
                "altura": row.altura,
                "color": row.color,
                "estado": row.estado,
                "procedencia": row.procedencia,
                "notas": row.notas,
                "padre_id": row.padre_id,
                "madre_id": row.madre_id,
                "foto_principal_url": row.foto_principal_url,
                "created_at": row.created_at.isoformat(),
                "updated_at": row.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "message": "Gallos obtenidos desde PostgreSQL",
            "data": {
                "gallos": gallos_data,
                "total": len(gallos_data),
                "user_id": current_user_id
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo gallos: {str(e)}"
        )

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_gallo_real(
    nombre: str = Form(...),
    codigo_identificacion: str = Form(...),
    raza_id: Optional[int] = Form(None),
    fecha_nacimiento: Optional[str] = Form(None),
    peso: Optional[float] = Form(None),
    altura: Optional[int] = Form(None),
    color: Optional[str] = Form(None),
    estado: str = Form("activo"),
    procedencia: Optional[str] = Form(None),
    notas: Optional[str] = Form(None),
    padre_id: Optional[int] = Form(None),
    madre_id: Optional[int] = Form(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🆕 Crear gallo REAL en PostgreSQL"""
    
    try:
        # Validar código único
        query_check = text("SELECT id FROM gallos WHERE codigo_identificacion = :codigo AND user_id = :user_id")
        existing = db.execute(query_check, {"codigo": codigo_identificacion.upper(), "user_id": current_user_id}).fetchone()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un gallo con el código '{codigo_identificacion}'"
            )
        
        # Procesar fecha
        fecha_nacimiento_parsed = None
        if fecha_nacimiento:
            try:
                fecha_nacimiento_parsed = datetime.fromisoformat(fecha_nacimiento).date()
            except:
                pass
        
        # Insertar gallo REAL en PostgreSQL
        insert_query = text("""
            INSERT INTO gallos (
                user_id, nombre, codigo_identificacion, raza_id, fecha_nacimiento,
                peso, altura, color, estado, procedencia, notas, padre_id, madre_id,
                created_at, updated_at
            ) VALUES (
                :user_id, :nombre, :codigo, :raza_id, :fecha_nacimiento,
                :peso, :altura, :color, :estado, :procedencia, :notas, :padre_id, :madre_id,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            ) RETURNING id, created_at
        """)
        
        result = db.execute(insert_query, {
            "user_id": current_user_id,
            "nombre": nombre,
            "codigo": codigo_identificacion.upper(),
            "raza_id": raza_id,
            "fecha_nacimiento": fecha_nacimiento_parsed,
            "peso": peso,
            "altura": altura,
            "color": color,
            "estado": estado,
            "procedencia": procedencia,
            "notas": notas,
            "padre_id": padre_id,
            "madre_id": madre_id
        })
        
        new_gallo = result.fetchone()
        db.commit()
        
        return {
            "success": True,
            "message": "✅ GALLO CREADO EN POSTGRESQL",
            "data": {
                "gallo": {
                    "id": new_gallo.id,
                    "nombre": nombre,
                    "codigo_identificacion": codigo_identificacion.upper(),
                    "raza_id": raza_id,
                    "user_id": current_user_id,
                    "created_at": new_gallo.created_at.isoformat()
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando gallo: {str(e)}"
        )

@router.get("/{gallo_id}", response_model=dict)
async def get_gallo_real(
    gallo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🔍 Obtener gallo REAL con genealogía"""
    
    try:
        # Query para obtener gallo con raza y padres
        query = text("""
            SELECT 
                g.*,
                r.nombre as raza_nombre,
                p.nombre as padre_nombre,
                p.codigo_identificacion as padre_codigo,
                p.foto_principal_url as padre_foto,
                m.nombre as madre_nombre, 
                m.codigo_identificacion as madre_codigo,
                m.foto_principal_url as madre_foto
            FROM gallos g
            LEFT JOIN razas r ON g.raza_id = r.id
            LEFT JOIN gallos p ON g.padre_id = p.id
            LEFT JOIN gallos m ON g.madre_id = m.id
            WHERE g.id = :gallo_id AND g.user_id = :user_id
        """)
        
        result = db.execute(query, {"gallo_id": gallo_id, "user_id": current_user_id})
        gallo_row = result.fetchone()
        
        if not gallo_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Construir respuesta con genealogía
        gallo_data = {
            "id": gallo_row.id,
            "nombre": gallo_row.nombre,
            "codigo_identificacion": gallo_row.codigo_identificacion,
            "raza_id": gallo_row.raza_id,
            "raza_nombre": gallo_row.raza_nombre,
            "fecha_nacimiento": gallo_row.fecha_nacimiento.isoformat() if gallo_row.fecha_nacimiento else None,
            "peso": float(gallo_row.peso) if gallo_row.peso else None,
            "altura": gallo_row.altura,
            "color": gallo_row.color,
            "estado": gallo_row.estado,
            "procedencia": gallo_row.procedencia,
            "notas": gallo_row.notas,
            "foto_principal_url": gallo_row.foto_principal_url,
            "padre_id": gallo_row.padre_id,
            "madre_id": gallo_row.madre_id,
            "created_at": gallo_row.created_at.isoformat(),
            "updated_at": gallo_row.updated_at.isoformat(),
            
            # Genealogía
            "padre": {
                "id": gallo_row.padre_id,
                "nombre": gallo_row.padre_nombre,
                "codigo_identificacion": gallo_row.padre_codigo,
                "foto_principal_url": gallo_row.padre_foto
            } if gallo_row.padre_id else None,
            
            "madre": {
                "id": gallo_row.madre_id,
                "nombre": gallo_row.madre_nombre,
                "codigo_identificacion": gallo_row.madre_codigo,
                "foto_principal_url": gallo_row.madre_foto
            } if gallo_row.madre_id else None
        }
        
        return {
            "success": True,
            "message": "✅ GALLO OBTENIDO DESDE POSTGRESQL",
            "data": {"gallo": gallo_data}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo gallo: {str(e)}"
        )

@router.put("/{gallo_id}", response_model=dict)
async def update_gallo_real(
    gallo_id: int,
    nombre: Optional[str] = Form(None),
    peso: Optional[float] = Form(None),
    altura: Optional[int] = Form(None),
    color: Optional[str] = Form(None),
    estado: Optional[str] = Form(None),
    procedencia: Optional[str] = Form(None),
    notas: Optional[str] = Form(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """✏️ Actualizar gallo REAL en PostgreSQL"""
    
    try:
        # Verificar que existe
        check_query = text("SELECT id FROM gallos WHERE id = :gallo_id AND user_id = :user_id")
        existing = db.execute(check_query, {"gallo_id": gallo_id, "user_id": current_user_id}).fetchone()
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Construir update dinámico
        updates = []
        params = {"gallo_id": gallo_id, "user_id": current_user_id}
        
        if nombre:
            updates.append("nombre = :nombre")
            params["nombre"] = nombre
        if peso is not None:
            updates.append("peso = :peso") 
            params["peso"] = peso
        if altura is not None:
            updates.append("altura = :altura")
            params["altura"] = altura
        if color:
            updates.append("color = :color")
            params["color"] = color
        if estado:
            updates.append("estado = :estado")
            params["estado"] = estado
        if procedencia:
            updates.append("procedencia = :procedencia")
            params["procedencia"] = procedencia
        if notas:
            updates.append("notas = :notas")
            params["notas"] = notas
        
        if not updates:
            return {
                "success": True,
                "message": "No hay cambios para aplicar",
                "data": {"gallo_id": gallo_id}
            }
        
        # Ejecutar update
        updates.append("updated_at = CURRENT_TIMESTAMP")
        update_query = text(f"""
            UPDATE gallos 
            SET {', '.join(updates)}
            WHERE id = :gallo_id AND user_id = :user_id
        """)
        
        db.execute(update_query, params)
        db.commit()
        
        return {
            "success": True,
            "message": "✅ GALLO ACTUALIZADO EN POSTGRESQL",
            "data": {
                "gallo_id": gallo_id,
                "cambios": list(params.keys())[2:]  # Excluir gallo_id y user_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando gallo: {str(e)}"
        )

@router.delete("/{gallo_id}", response_model=dict)
async def delete_gallo_real(
    gallo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🗑️ Eliminar gallo REAL de PostgreSQL"""
    
    try:
        # Verificar que existe
        check_query = text("SELECT nombre, codigo_identificacion FROM gallos WHERE id = :gallo_id AND user_id = :user_id")
        gallo = db.execute(check_query, {"gallo_id": gallo_id, "user_id": current_user_id}).fetchone()
        
        if not gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Verificar descendientes
        desc_query = text("SELECT COUNT(*) as count FROM gallos WHERE (padre_id = :gallo_id OR madre_id = :gallo_id)")
        descendientes = db.execute(desc_query, {"gallo_id": gallo_id}).fetchone()
        
        if descendientes.count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar. Este gallo es padre/madre de {descendientes.count} gallos"
            )
        
        # Eliminar
        delete_query = text("DELETE FROM gallos WHERE id = :gallo_id AND user_id = :user_id")
        db.execute(delete_query, {"gallo_id": gallo_id, "user_id": current_user_id})
        db.commit()
        
        return {
            "success": True,
            "message": "✅ GALLO ELIMINADO DE POSTGRESQL",
            "data": {
                "gallo_eliminado": {
                    "id": gallo_id,
                    "nombre": gallo.nombre,
                    "codigo_identificacion": gallo.codigo_identificacion
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando gallo: {str(e)}"
        )

# ========================================
# 🌳 GENEALOGÍA REAL (AGRUPADA CON GALLOS)
# ========================================

@router.get("/{gallo_id}/genealogia", response_model=dict)
async def get_genealogia_real(
    gallo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🌳 Árbol genealógico REAL desde PostgreSQL"""
    
    try:
        # Función recursiva para construir árbol
        def build_tree(current_id, depth=0, max_depth=3):
            if depth >= max_depth or not current_id:
                return None
            
            query = text("""
                SELECT g.*, r.nombre as raza_nombre
                FROM gallos g 
                LEFT JOIN razas r ON g.raza_id = r.id
                WHERE g.id = :id
            """)
            
            result = db.execute(query, {"id": current_id}).fetchone()
            if not result:
                return None
            
            node = {
                "id": result.id,
                "nombre": result.nombre,
                "codigo_identificacion": result.codigo_identificacion,
                "raza_nombre": result.raza_nombre,
                "foto_principal_url": result.foto_principal_url,
                "generacion": depth
            }
            
            # Recursión para padres
            if result.padre_id:
                node["padre"] = build_tree(result.padre_id, depth + 1, max_depth)
            if result.madre_id:
                node["madre"] = build_tree(result.madre_id, depth + 1, max_depth)
            
            return node
        
        # Verificar que el gallo base existe y pertenece al usuario
        base_query = text("SELECT id FROM gallos WHERE id = :gallo_id AND user_id = :user_id")
        base_gallo = db.execute(base_query, {"gallo_id": gallo_id, "user_id": current_user_id}).fetchone()
        
        if not base_gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Construir árbol
        arbol = build_tree(gallo_id)
        
        # Contar descendientes
        desc_query = text("""
            WITH RECURSIVE descendientes AS (
                SELECT id, nombre, codigo_identificacion, padre_id, madre_id, 1 as nivel
                FROM gallos 
                WHERE (padre_id = :gallo_id OR madre_id = :gallo_id)
                
                UNION ALL
                
                SELECT g.id, g.nombre, g.codigo_identificacion, g.padre_id, g.madre_id, d.nivel + 1
                FROM gallos g
                INNER JOIN descendientes d ON (g.padre_id = d.id OR g.madre_id = d.id)
                WHERE d.nivel < 3
            )
            SELECT * FROM descendientes ORDER BY nivel, nombre
        """)
        
        descendientes = db.execute(desc_query, {"gallo_id": gallo_id}).fetchall()
        
        descendientes_data = [
            {
                "id": desc.id,
                "nombre": desc.nombre,
                "codigo_identificacion": desc.codigo_identificacion,
                "generacion": desc.nivel,
                "relacion": "descendiente"
            }
            for desc in descendientes
        ]
        
        return {
            "success": True,
            "message": "🌳 ÁRBOL GENEALÓGICO DESDE POSTGRESQL",
            "data": {
                "gallo_base": {
                    "id": gallo_id,
                    "user_id": current_user_id
                },
                "arbol_genealogico": {
                    "ancestros": arbol,
                    "descendientes": descendientes_data,
                    "estadisticas": {
                        "total_ancestros": len([n for n in str(arbol) if '"id":' in str(n)]) - 1 if arbol else 0,
                        "total_descendientes": len(descendientes_data),
                        "generaciones_hacia_arriba": 3,
                        "generaciones_hacia_abajo": max([d["generacion"] for d in descendientes_data]) if descendientes_data else 0
                    }
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error construyendo genealogía: {str(e)}"
        )
