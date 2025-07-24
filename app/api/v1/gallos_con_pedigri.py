# app/api/v1/gallos_con_pedigri.py - REGISTRO COMPLETO COMO EL HTML
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

from app.database import get_db
from app.core.security import get_current_user_id

router = APIRouter()

@router.post("/con-pedigri", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_gallo_con_pedigri(
    # DATOS DEL GALLO PRINCIPAL
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
    
    # DATOS DEL PADRE (OPCIONAL)
    crear_padre: bool = Form(False),
    padre_nombre: Optional[str] = Form(None),
    padre_codigo: Optional[str] = Form(None), 
    padre_raza_id: Optional[int] = Form(None),
    padre_color: Optional[str] = Form(None),
    padre_peso: Optional[float] = Form(None),
    padre_procedencia: Optional[str] = Form(None),
    padre_notas: Optional[str] = Form(None),
    
    # DATOS DE LA MADRE (OPCIONAL)
    crear_madre: bool = Form(False),
    madre_nombre: Optional[str] = Form(None),
    madre_codigo: Optional[str] = Form(None),
    madre_raza_id: Optional[int] = Form(None), 
    madre_color: Optional[str] = Form(None),
    madre_peso: Optional[float] = Form(None),
    madre_procedencia: Optional[str] = Form(None),
    madre_notas: Optional[str] = Form(None),
    
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Crear gallo con pedigri completo - hasta 3 registros"""
    
    try:
        registros_creados = []
        padre_id = None
        madre_id = None
        
        # PASO 1: CREAR PADRE SI SE SOLICITA
        if crear_padre and padre_nombre and padre_codigo:
            # Validar código único del padre
            query_check = text("SELECT id FROM gallos WHERE codigo_identificacion = :codigo AND user_id = :user_id")
            existing = db.execute(query_check, {"codigo": padre_codigo.upper(), "user_id": current_user_id}).fetchone()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un gallo con el código '{padre_codigo}' (Padre)"
                )
            
            # Insertar padre
            insert_padre = text("""
                INSERT INTO gallos (
                    user_id, nombre, codigo_identificacion, raza_id, peso, color, 
                    estado, procedencia, notas, created_at, updated_at
                ) VALUES (
                    :user_id, :nombre, :codigo, :raza_id, :peso, :color,
                    'padre', :procedencia, :notas, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                ) RETURNING id, created_at
            """)
            
            result_padre = db.execute(insert_padre, {
                "user_id": current_user_id,
                "nombre": padre_nombre,
                "codigo": padre_codigo.upper(),
                "raza_id": padre_raza_id,
                "peso": padre_peso,
                "color": padre_color,
                "procedencia": padre_procedencia,
                "notas": padre_notas
            })
            
            padre_row = result_padre.fetchone()
            padre_id = padre_row.id
            
            registros_creados.append({
                "tipo": "padre",
                "id": padre_id,
                "nombre": padre_nombre,
                "codigo": padre_codigo.upper(),
                "created_at": padre_row.created_at.isoformat()
            })
        
        # PASO 2: CREAR MADRE SI SE SOLICITA
        if crear_madre and madre_nombre and madre_codigo:
            # Validar código único de la madre
            query_check = text("SELECT id FROM gallos WHERE codigo_identificacion = :codigo AND user_id = :user_id")
            existing = db.execute(query_check, {"codigo": madre_codigo.upper(), "user_id": current_user_id}).fetchone()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un gallo con el código '{madre_codigo}' (Madre)"
                )
            
            # Insertar madre
            insert_madre = text("""
                INSERT INTO gallos (
                    user_id, nombre, codigo_identificacion, raza_id, peso, color,
                    estado, procedencia, notas, created_at, updated_at
                ) VALUES (
                    :user_id, :nombre, :codigo, :raza_id, :peso, :color,
                    'madre', :procedencia, :notas, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                ) RETURNING id, created_at
            """)
            
            result_madre = db.execute(insert_madre, {
                "user_id": current_user_id,
                "nombre": madre_nombre,
                "codigo": madre_codigo.upper(),
                "raza_id": madre_raza_id,
                "peso": madre_peso,
                "color": madre_color,
                "procedencia": madre_procedencia,
                "notas": madre_notas
            })
            
            madre_row = result_madre.fetchone()
            madre_id = madre_row.id
            
            registros_creados.append({
                "tipo": "madre",
                "id": madre_id,
                "nombre": madre_nombre,
                "codigo": madre_codigo.upper(),
                "created_at": madre_row.created_at.isoformat()
            })
        
        # PASO 3: CREAR GALLO PRINCIPAL CON PADRES
        # Validar código único del gallo principal
        query_check = text("SELECT id FROM gallos WHERE codigo_identificacion = :codigo AND user_id = :user_id")
        existing = db.execute(query_check, {"codigo": codigo_identificacion.upper(), "user_id": current_user_id}).fetchone()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un gallo con el código '{codigo_identificacion}' (Principal)"
            )
        
        # Procesar fecha
        fecha_nacimiento_parsed = None
        if fecha_nacimiento:
            try:
                fecha_nacimiento_parsed = datetime.fromisoformat(fecha_nacimiento).date()
            except:
                pass
        
        # Insertar gallo principal CON PADRES
        insert_gallo = text("""
            INSERT INTO gallos (
                user_id, nombre, codigo_identificacion, raza_id, fecha_nacimiento,
                peso, altura, color, estado, procedencia, notas, 
                padre_id, madre_id, created_at, updated_at
            ) VALUES (
                :user_id, :nombre, :codigo, :raza_id, :fecha_nacimiento,
                :peso, :altura, :color, :estado, :procedencia, :notas,
                :padre_id, :madre_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            ) RETURNING id, created_at
        """)
        
        result_gallo = db.execute(insert_gallo, {
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
            "padre_id": padre_id,  # CONECTADO AL PADRE
            "madre_id": madre_id   # CONECTADO A LA MADRE
        })
        
        gallo_row = result_gallo.fetchone()
        gallo_principal_id = gallo_row.id
        
        registros_creados.append({
            "tipo": "gallo_principal",
            "id": gallo_principal_id,
            "nombre": nombre,
            "codigo": codigo_identificacion.upper(),
            "padre_id": padre_id,
            "madre_id": madre_id,
            "created_at": gallo_row.created_at.isoformat()
        })
        
        # Commit todo junto
        db.commit()
        
        return {
            "success": True,
            "message": f"PEDIGRI COMPLETO CREADO - {len(registros_creados)} REGISTROS",
            "data": {
                "gallo_principal": {
                    "id": gallo_principal_id,
                    "nombre": nombre,
                    "codigo_identificacion": codigo_identificacion.upper(),
                    "padre_id": padre_id,
                    "madre_id": madre_id,
                    "user_id": current_user_id
                },
                "registros_creados": registros_creados,
                "total_registros": len(registros_creados),
                "pedigri_completo": {
                    "tiene_padre": padre_id is not None,
                    "tiene_madre": madre_id is not None,
                    "generaciones": 2 if (padre_id and madre_id) else 1
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando pedigri: {str(e)}"
        )
