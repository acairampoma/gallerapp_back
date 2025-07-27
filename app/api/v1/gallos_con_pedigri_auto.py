# app/api/v1/gallos_con_pedigri_auto.py - VERSIÓN AUTOMÁTICA CORRECTA
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
import time

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
    
    # OPCIONES PARA CREAR FAMILIA (solo nombres, códigos se generan automáticamente)
    crear_padre: bool = Form(False),
    padre_nombre: Optional[str] = Form(None),
    padre_raza_id: Optional[int] = Form(None),
    padre_color: Optional[str] = Form(None),
    padre_peso: Optional[float] = Form(None),
    padre_procedencia: Optional[str] = Form(None),
    padre_notas: Optional[str] = Form(None),
    
    crear_madre: bool = Form(False),
    madre_nombre: Optional[str] = Form(None),
    madre_raza_id: Optional[int] = Form(None), 
    madre_color: Optional[str] = Form(None),
    madre_peso: Optional[float] = Form(None),
    madre_procedencia: Optional[str] = Form(None),
    madre_notas: Optional[str] = Form(None),
    
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🔥 TÉCNICA ÉPICA: Crear gallo con pedigrí completo
    - Solo se necesita el código del gallo principal
    - Los códigos del padre y madre se generan AUTOMÁTICAMENTE
    - 1 formulario → 3 registros vinculados
    """
    
    try:
        registros_creados = []
        padre_id = None
        madre_id = None
        
        # 🔥 GENERAR ID GENEALÓGICO ÚNICO PARA VINCULAR LA FAMILIA
        id_gallo_genealogico = int(time.time() * 1000) + current_user_id
        
        # 🎯 GENERAR CÓDIGOS AUTOMÁTICOS BASADOS EN EL CÓDIGO PRINCIPAL
        codigo_base = codigo_identificacion.upper()
        padre_codigo_auto = f"P-{codigo_base}"  # Ejemplo: P-CAMP001
        madre_codigo_auto = f"M-{codigo_base}"  # Ejemplo: M-CAMP001
        
        # PASO 1: CREAR PADRE SI SE SOLICITA
        if crear_padre:
            # Si no se dio nombre, generar uno automático
            if not padre_nombre:
                padre_nombre = f"Padre de {nombre}"
            
            # Validar que no exista el código autogenerado
            query_check = text("SELECT id FROM gallos WHERE codigo_identificacion = :codigo AND user_id = :user_id")
            existing = db.execute(query_check, {"codigo": padre_codigo_auto, "user_id": current_user_id}).fetchone()
            
            if existing:
                # Si ya existe, agregar un sufijo numérico
                for i in range(1, 100):
                    padre_codigo_auto = f"P{i}-{codigo_base}"
                    existing = db.execute(query_check, {"codigo": padre_codigo_auto, "user_id": current_user_id}).fetchone()
                    if not existing:
                        break
            
            # Insertar padre CON CÓDIGO AUTOGENERADO
            insert_padre = text("""
                INSERT INTO gallos (
                    user_id, nombre, codigo_identificacion, raza_id, peso, color, 
                    estado, procedencia, notas, 
                    id_gallo_genealogico, tipo_registro,
                    created_at, updated_at
                ) VALUES (
                    :user_id, :nombre, :codigo, :raza_id, :peso, :color,
                    'padre', :procedencia, :notas,
                    :id_gallo_genealogico, 'padre_generado',
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                ) RETURNING id, created_at
            """)
            
            result_padre = db.execute(insert_padre, {
                "user_id": current_user_id,
                "nombre": padre_nombre,
                "codigo": padre_codigo_auto,  # 🔥 CÓDIGO AUTOGENERADO
                "raza_id": padre_raza_id,
                "peso": padre_peso,
                "color": padre_color,
                "procedencia": padre_procedencia,
                "notas": padre_notas,
                "id_gallo_genealogico": id_gallo_genealogico
            })
            
            padre_row = result_padre.fetchone()
            padre_id = padre_row.id
            
            registros_creados.append({
                "tipo": "padre",
                "id": padre_id,
                "nombre": padre_nombre,
                "codigo": padre_codigo_auto,
                "codigo_autogenerado": True,  # 🔥 Indicar que fue autogenerado
                "id_gallo_genealogico": id_gallo_genealogico,
                "created_at": padre_row.created_at.isoformat()
            })
        
        # PASO 2: CREAR MADRE SI SE SOLICITA
        if crear_madre:
            # Si no se dio nombre, generar uno automático
            if not madre_nombre:
                madre_nombre = f"Madre de {nombre}"
            
            # Validar que no exista el código autogenerado
            query_check = text("SELECT id FROM gallos WHERE codigo_identificacion = :codigo AND user_id = :user_id")
            existing = db.execute(query_check, {"codigo": madre_codigo_auto, "user_id": current_user_id}).fetchone()
            
            if existing:
                # Si ya existe, agregar un sufijo numérico
                for i in range(1, 100):
                    madre_codigo_auto = f"M{i}-{codigo_base}"
                    existing = db.execute(query_check, {"codigo": madre_codigo_auto, "user_id": current_user_id}).fetchone()
                    if not existing:
                        break
            
            # Insertar madre CON CÓDIGO AUTOGENERADO
            insert_madre = text("""
                INSERT INTO gallos (
                    user_id, nombre, codigo_identificacion, raza_id, peso, color,
                    estado, procedencia, notas,
                    id_gallo_genealogico, tipo_registro,
                    created_at, updated_at
                ) VALUES (
                    :user_id, :nombre, :codigo, :raza_id, :peso, :color,
                    'madre', :procedencia, :notas,
                    :id_gallo_genealogico, 'madre_generada',
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                ) RETURNING id, created_at
            """)
            
            result_madre = db.execute(insert_madre, {
                "user_id": current_user_id,
                "nombre": madre_nombre,
                "codigo": madre_codigo_auto,  # 🔥 CÓDIGO AUTOGENERADO
                "raza_id": madre_raza_id,
                "peso": madre_peso,
                "color": madre_color,
                "procedencia": madre_procedencia,
                "notas": madre_notas,
                "id_gallo_genealogico": id_gallo_genealogico
            })
            
            madre_row = result_madre.fetchone()
            madre_id = madre_row.id
            
            registros_creados.append({
                "tipo": "madre",
                "id": madre_id,
                "nombre": madre_nombre,
                "codigo": madre_codigo_auto,
                "codigo_autogenerado": True,  # 🔥 Indicar que fue autogenerado
                "id_gallo_genealogico": id_gallo_genealogico,
                "created_at": madre_row.created_at.isoformat()
            })
        
        # PASO 3: CREAR GALLO PRINCIPAL
        # Validar código único del gallo principal
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
        
        # Insertar gallo principal
        insert_gallo = text("""
            INSERT INTO gallos (
                user_id, nombre, codigo_identificacion, raza_id, fecha_nacimiento,
                peso, altura, color, estado, procedencia, notas, 
                padre_id, madre_id, 
                id_gallo_genealogico, tipo_registro,
                created_at, updated_at
            ) VALUES (
                :user_id, :nombre, :codigo, :raza_id, :fecha_nacimiento,
                :peso, :altura, :color, :estado, :procedencia, :notas,
                :padre_id, :madre_id,
                :id_gallo_genealogico, 'principal',
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
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
            "padre_id": padre_id,
            "madre_id": madre_id,
            "id_gallo_genealogico": id_gallo_genealogico
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
            "id_gallo_genealogico": id_gallo_genealogico,
            "created_at": gallo_row.created_at.isoformat()
        })
        
        # Commit todo junto
        db.commit()
        
        # 🔥 MENSAJE ÉPICO MEJORADO
        mensaje = f"🔥 TÉCNICA ÉPICA COMPLETA - {len(registros_creados)} REGISTROS"
        if crear_padre or crear_madre:
            mensaje += "\n📝 CÓDIGOS AUTOGENERADOS:"
            if crear_padre:
                mensaje += f"\n   • Padre: {padre_codigo_auto}"
            if crear_madre:
                mensaje += f"\n   • Madre: {madre_codigo_auto}"
        
        return {
            "success": True,
            "message": mensaje,
            "data": {
                "gallo_principal": {
                    "id": gallo_principal_id,
                    "nombre": nombre,
                    "codigo_identificacion": codigo_identificacion.upper(),
                    "padre_id": padre_id,
                    "madre_id": madre_id,
                    "user_id": current_user_id,
                    "id_gallo_genealogico": id_gallo_genealogico
                },
                "registros_creados": registros_creados,
                "total_registros": len(registros_creados),
                "id_gallo_genealogico": id_gallo_genealogico,
                "tecnica_epica": {
                    "familia_vinculada": True,
                    "codigos_autogenerados": crear_padre or crear_madre,
                    "consulta_rapida": f"SELECT * FROM gallos WHERE id_gallo_genealogico = {id_gallo_genealogico}"
                },
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
