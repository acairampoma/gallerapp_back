# app/api/v1/gallos_agregar_padres.py - EXPANDIR GENEALOGÍA
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from app.database import get_db
from app.core.security import get_current_user_id

router = APIRouter()

@router.post("/{gallo_id}/agregar-padres", response_model=dict)
async def agregar_padres_a_gallo(
    gallo_id: int,
    # DATOS DEL PADRE
    crear_padre: bool = Form(False),
    padre_nombre: Optional[str] = Form(None),
    padre_codigo: Optional[str] = Form(None),
    padre_raza_id: Optional[int] = Form(None),
    padre_color: Optional[str] = Form(None),
    padre_peso: Optional[float] = Form(None),
    
    # DATOS DE LA MADRE
    crear_madre: bool = Form(False),
    madre_nombre: Optional[str] = Form(None),
    madre_codigo: Optional[str] = Form(None),
    madre_raza_id: Optional[int] = Form(None),
    madre_color: Optional[str] = Form(None),
    madre_peso: Optional[float] = Form(None),
    
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🔥 EXPANDIR GENEALOGÍA: Agregar padres a un gallo existente
    - Los nuevos padres heredan el id_gallo_genealogico
    """
    
    try:
        # Verificar que el gallo existe y pertenece al usuario
        query_gallo = text("""
            SELECT id, nombre, codigo_identificacion, id_gallo_genealogico, padre_id, madre_id 
            FROM gallos 
            WHERE id = :id AND user_id = :user_id
        """)
        gallo = db.execute(query_gallo, {"id": gallo_id, "user_id": current_user_id}).fetchone()
        
        if not gallo:
            raise HTTPException(status_code=404, detail="Gallo no encontrado")
        
        if gallo.padre_id or gallo.madre_id:
            raise HTTPException(
                status_code=400, 
                detail=f"El gallo '{gallo.nombre}' ya tiene padres registrados"
            )
        
        # 🔥 USAR EL MISMO ID GENEALÓGICO
        id_gallo_genealogico = gallo.id_gallo_genealogico
        registros_creados = []
        padre_id = None
        madre_id = None
        
        # CREAR PADRE SI SE SOLICITA
        if crear_padre and padre_nombre and padre_codigo:
            # Validar código único
            query_check = text("SELECT id FROM gallos WHERE codigo_identificacion = :codigo AND user_id = :user_id")
            existing = db.execute(query_check, {"codigo": padre_codigo.upper(), "user_id": current_user_id}).fetchone()
            
            if existing:
                raise HTTPException(status_code=400, detail=f"Ya existe un gallo con código '{padre_codigo}'")
            
            # Insertar padre con el MISMO id_gallo_genealogico
            insert_padre = text("""
                INSERT INTO gallos (
                    user_id, nombre, codigo_identificacion, raza_id, peso, color,
                    estado, id_gallo_genealogico, tipo_registro,
                    created_at, updated_at
                ) VALUES (
                    :user_id, :nombre, :codigo, :raza_id, :peso, :color,
                    'padre', :id_gallo_genealogico, 'padre_generado',
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                ) RETURNING id
            """)
            
            result = db.execute(insert_padre, {
                "user_id": current_user_id,
                "nombre": padre_nombre,
                "codigo": padre_codigo.upper(),
                "raza_id": padre_raza_id,
                "peso": padre_peso,
                "color": padre_color,
                "id_gallo_genealogico": id_gallo_genealogico
            })
            
            padre_id = result.fetchone().id
            registros_creados.append({
                "tipo": "padre",
                "id": padre_id,
                "nombre": padre_nombre,
                "codigo": padre_codigo.upper(),
                "id_gallo_genealogico": id_gallo_genealogico
            })
        
        # CREAR MADRE SI SE SOLICITA
        if crear_madre and madre_nombre and madre_codigo:
            # Validar código único
            query_check = text("SELECT id FROM gallos WHERE codigo_identificacion = :codigo AND user_id = :user_id")
            existing = db.execute(query_check, {"codigo": madre_codigo.upper(), "user_id": current_user_id}).fetchone()
            
            if existing:
                raise HTTPException(status_code=400, detail=f"Ya existe un gallo con código '{madre_codigo}'")
            
            # Insertar madre con el MISMO id_gallo_genealogico
            insert_madre = text("""
                INSERT INTO gallos (
                    user_id, nombre, codigo_identificacion, raza_id, peso, color,
                    estado, id_gallo_genealogico, tipo_registro,
                    created_at, updated_at
                ) VALUES (
                    :user_id, :nombre, :codigo, :raza_id, :peso, :color,
                    'madre', :id_gallo_genealogico, 'madre_generada',
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                ) RETURNING id
            """)
            
            result = db.execute(insert_madre, {
                "user_id": current_user_id,
                "nombre": madre_nombre,
                "codigo": madre_codigo.upper(),
                "raza_id": madre_raza_id,
                "peso": madre_peso,
                "color": madre_color,
                "id_gallo_genealogico": id_gallo_genealogico
            })
            
            madre_id = result.fetchone().id
            registros_creados.append({
                "tipo": "madre",
                "id": madre_id,
                "nombre": madre_nombre,
                "codigo": madre_codigo.upper(),
                "id_gallo_genealogico": id_gallo_genealogico
            })
        
        # ACTUALIZAR EL GALLO CON SUS NUEVOS PADRES
        if padre_id or madre_id:
            update_gallo = text("""
                UPDATE gallos 
                SET padre_id = :padre_id, madre_id = :madre_id 
                WHERE id = :id
            """)
            db.execute(update_gallo, {
                "padre_id": padre_id,
                "madre_id": madre_id,
                "id": gallo_id
            })
        
        db.commit()
        
        return {
            "success": True,
            "message": f"🧬 GENEALOGÍA EXPANDIDA - {len(registros_creados)} nuevos registros",
            "data": {
                "gallo_actualizado": {
                    "id": gallo.id,
                    "nombre": gallo.nombre,
                    "codigo": gallo.codigo_identificacion,
                    "ahora_tiene_padre": padre_id is not None,
                    "ahora_tiene_madre": madre_id is not None
                },
                "registros_creados": registros_creados,
                "id_gallo_genealogico": id_gallo_genealogico,
                "familia_completa": f"SELECT * FROM gallos WHERE id_gallo_genealogico = {id_gallo_genealogico}"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
