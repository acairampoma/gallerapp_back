# app/api/v1/gallos_con_pedigri.py - TÉCNICA ÉPICA CORRECTA
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
import os

from app.database import get_db
from app.core.security import get_current_user_id
from app.services.cloudinary_service import CloudinaryService

router = APIRouter()

@router.post("/con-pedigri", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_gallo_con_pedigri(
    # DATOS DEL GALLO PRINCIPAL
    nombre: str = Form(...),
    codigo_identificacion: str = Form(...),
    fecha_nacimiento: Optional[str] = Form(None),
    numero_registro: Optional[str] = Form(None),  # NUEVO CAMPO
    color_placa: Optional[str] = Form(None),      # NUEVO CAMPO
    ubicacion_placa: Optional[str] = Form(None),  # NUEVO CAMPO
    raza_id: Optional[int] = Form(None),
    peso: Optional[float] = Form(None),
    altura: Optional[int] = Form(None),
    color: Optional[str] = Form(None),
    estado: str = Form("activo"),
    procedencia: Optional[str] = Form(None),
    notas: Optional[str] = Form(None),
    # CAMPOS ADICIONALES DEL PLAN ÉPICO
    color_patas: Optional[str] = Form(None),
    color_plumaje: Optional[str] = Form(None),
    criador: Optional[str] = Form(None),
    propietario_actual: Optional[str] = Form(None),
    observaciones: Optional[str] = Form(None),
    
    # 📸 FOTO PRINCIPAL (OPCIONAL)
    foto_principal: Optional[UploadFile] = File(None, description="Foto principal del gallo"),
    
    # DATOS DEL PADRE (OPCIONAL)
    crear_padre: bool = Form(False),
    padre_nombre: Optional[str] = Form(None),
    padre_fecha_nacimiento: Optional[str] = Form(None),  # NUEVO CAMPO
    padre_numero_registro: Optional[str] = Form(None),   # NUEVO CAMPO
    padre_color_placa: Optional[str] = Form(None),       # NUEVO CAMPO
    padre_ubicacion_placa: Optional[str] = Form(None),   # NUEVO CAMPO
    padre_codigo: Optional[str] = Form(None), 
    padre_raza_id: Optional[int] = Form(None),
    padre_color: Optional[str] = Form(None),
    padre_peso: Optional[float] = Form(None),
    padre_procedencia: Optional[str] = Form(None),
    padre_notas: Optional[str] = Form(None),
    
    # DATOS DE LA MADRE (OPCIONAL)
    crear_madre: bool = Form(False),
    madre_nombre: Optional[str] = Form(None),
    madre_fecha_nacimiento: Optional[str] = Form(None),  # NUEVO CAMPO
    madre_numero_registro: Optional[str] = Form(None),   # NUEVO CAMPO
    madre_color_placa: Optional[str] = Form(None),       # NUEVO CAMPO
    madre_ubicacion_placa: Optional[str] = Form(None),   # NUEVO CAMPO
    madre_codigo: Optional[str] = Form(None),
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
    - El id_gallo_genealogico será el ID del gallo principal
    - Todos los familiares compartirán este mismo ID
    """
    
    try:
        registros_creados = []
        padre_id = None
        madre_id = None
        
        # PRIMERO: Crear el gallo principal para obtener su ID
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
        
        # Insertar gallo principal PRIMERO (sin padres aún)
        # Usar numero_registro como codigo si está disponible, sino usar codigo_identificacion
        codigo_final = numero_registro or codigo_identificacion
        
        insert_gallo = text("""
            INSERT INTO gallos (
                user_id, nombre, codigo_identificacion, fecha_nacimiento, 
                color_placa, ubicacion_placa, raza_id, peso, altura, color, 
                estado, procedencia, notas, color_patas, color_plumaje, 
                criador, propietario_actual, observaciones,
                tipo_registro, created_at, updated_at
            ) VALUES (
                :user_id, :nombre, :codigo, :fecha_nacimiento,
                :color_placa, :ubicacion_placa, :raza_id, :peso, :altura, :color,
                :estado, :procedencia, :notas, :color_patas, :color_plumaje,
                :criador, :propietario_actual, :observaciones,
                'principal', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            ) RETURNING id, created_at
        """)
        
        result_gallo = db.execute(insert_gallo, {
            "user_id": current_user_id,
            "nombre": nombre,
            "codigo": codigo_final.upper(),
            "fecha_nacimiento": fecha_nacimiento_parsed,
            "color_placa": color_placa,
            "ubicacion_placa": ubicacion_placa,
            "raza_id": raza_id,
            "peso": peso,
            "altura": altura,
            "color": color,
            "estado": estado,
            "procedencia": procedencia,
            "notas": notas,
            "color_patas": color_patas,
            "color_plumaje": color_plumaje,
            "criador": criador,
            "propietario_actual": propietario_actual,
            "observaciones": observaciones
        })
        
        gallo_row = result_gallo.fetchone()
        gallo_principal_id = gallo_row.id
        
        # 🔥 EL ID GENEALÓGICO ES EL ID DEL GALLO PRINCIPAL
        id_gallo_genealogico = gallo_principal_id
        
        # Actualizar el gallo principal con su propio ID genealógico
        update_gallo = text("""
            UPDATE gallos 
            SET id_gallo_genealogico = :id_genealogico 
            WHERE id = :id
        """)
        db.execute(update_gallo, {
            "id_genealogico": id_gallo_genealogico,
            "id": gallo_principal_id
        })
        
        registros_creados.append({
            "tipo": "gallo_principal",
            "id": gallo_principal_id,
            "nombre": nombre,
            "codigo": codigo_identificacion.upper(),
            "id_gallo_genealogico": id_gallo_genealogico,
            "created_at": gallo_row.created_at.isoformat()
        })
        
        # CREAR PADRE SI SE SOLICITA
        if crear_padre and padre_nombre:
            # Usar padre_numero_registro si está disponible, sino usar padre_codigo
            padre_codigo_final = padre_numero_registro or padre_codigo
            
            if padre_codigo_final:
                # Validar código único del padre
                existing = db.execute(query_check, {"codigo": padre_codigo_final.upper(), "user_id": current_user_id}).fetchone()
                
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ya existe un gallo con el código '{padre_codigo_final}' (Padre)"
                    )
                
                # Procesar fecha del padre
                padre_fecha_parsed = None
                if padre_fecha_nacimiento:
                    try:
                        padre_fecha_parsed = datetime.fromisoformat(padre_fecha_nacimiento).date()
                    except:
                        pass
                
                # Insertar padre con el MISMO id_gallo_genealogico
                insert_padre = text("""
                    INSERT INTO gallos (
                        user_id, nombre, codigo_identificacion, fecha_nacimiento,
                        color_placa, ubicacion_placa, raza_id, peso, color, 
                        estado, procedencia, notas, id_gallo_genealogico, tipo_registro,
                        created_at, updated_at
                    ) VALUES (
                        :user_id, :nombre, :codigo, :fecha_nacimiento,
                        :color_placa, :ubicacion_placa, :raza_id, :peso, :color,
                        'padre', :procedencia, :notas, :id_gallo_genealogico, 'padre_generado',
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    ) RETURNING id, created_at
                """)
                
                result_padre = db.execute(insert_padre, {
                    "user_id": current_user_id,
                    "nombre": padre_nombre,
                    "codigo": padre_codigo_final.upper(),
                    "fecha_nacimiento": padre_fecha_parsed,
                    "color_placa": padre_color_placa,
                    "ubicacion_placa": padre_ubicacion_placa,
                    "raza_id": padre_raza_id,
                    "peso": padre_peso,
                    "color": padre_color,
                    "procedencia": padre_procedencia,
                    "notas": padre_notas,
                    "id_gallo_genealogico": id_gallo_genealogico  # 🔥 MISMO ID QUE EL HIJO
                })
                
                padre_row = result_padre.fetchone()
                padre_id = padre_row.id
                
                registros_creados.append({
                    "tipo": "padre",
                    "id": padre_id,
                    "nombre": padre_nombre,
                    "codigo": padre_codigo_final.upper(),
                    "id_gallo_genealogico": id_gallo_genealogico,
                    "created_at": padre_row.created_at.isoformat()
                })
        
        # CREAR MADRE SI SE SOLICITA
        if crear_madre and madre_nombre:
            # Usar madre_numero_registro si está disponible, sino usar madre_codigo
            madre_codigo_final = madre_numero_registro or madre_codigo
            
            if madre_codigo_final:
                # Validar código único de la madre
                existing = db.execute(query_check, {"codigo": madre_codigo_final.upper(), "user_id": current_user_id}).fetchone()
                
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ya existe un gallo con el código '{madre_codigo_final}' (Madre)"
                    )
                
                # Procesar fecha de la madre
                madre_fecha_parsed = None
                if madre_fecha_nacimiento:
                    try:
                        madre_fecha_parsed = datetime.fromisoformat(madre_fecha_nacimiento).date()
                    except:
                        pass
                
                # Insertar madre con el MISMO id_gallo_genealogico
                insert_madre = text("""
                    INSERT INTO gallos (
                        user_id, nombre, codigo_identificacion, fecha_nacimiento,
                        color_placa, ubicacion_placa, raza_id, peso, color,
                        estado, procedencia, notas, id_gallo_genealogico, tipo_registro,
                        created_at, updated_at
                    ) VALUES (
                        :user_id, :nombre, :codigo, :fecha_nacimiento,
                        :color_placa, :ubicacion_placa, :raza_id, :peso, :color,
                        'madre', :procedencia, :notas, :id_gallo_genealogico, 'madre_generada',
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    ) RETURNING id, created_at
                """)
                
                result_madre = db.execute(insert_madre, {
                    "user_id": current_user_id,
                    "nombre": madre_nombre,
                    "codigo": madre_codigo_final.upper(),
                    "fecha_nacimiento": madre_fecha_parsed,
                    "color_placa": madre_color_placa,
                    "ubicacion_placa": madre_ubicacion_placa,
                    "raza_id": madre_raza_id,
                    "peso": madre_peso,
                    "color": madre_color,
                    "procedencia": madre_procedencia,
                    "notas": madre_notas,
                    "id_gallo_genealogico": id_gallo_genealogico  # 🔥 MISMO ID QUE EL HIJO
                })
                
                madre_row = result_madre.fetchone()
                madre_id = madre_row.id
                
                registros_creados.append({
                    "tipo": "madre",
                    "id": madre_id,
                    "nombre": madre_nombre,
                    "codigo": madre_codigo_final.upper(),
                    "id_gallo_genealogico": id_gallo_genealogico,
                    "created_at": madre_row.created_at.isoformat()
                })
        
        # AHORA ACTUALIZAR EL GALLO PRINCIPAL CON LOS IDs DE PADRES
        if padre_id or madre_id:
            update_padres = text("""
                UPDATE gallos 
                SET padre_id = :padre_id, madre_id = :madre_id
                WHERE id = :id
            """)
            db.execute(update_padres, {
                "padre_id": padre_id,
                "madre_id": madre_id,
                "id": gallo_principal_id
            })
        
        # Commit todo junto
        db.commit()
        
        # 🔥 SUBIR FOTO DEL PARÁMETRO DESPUÉS DE CREAR GALLOS
        foto_url = None
        cloudinary_url = None
        try:
            # Usar foto_principal del parámetro Form (NO ruta estática)
            if foto_principal:
                print(f"📷 Subiendo foto del parámetro para gallo {gallo_principal_id}")
                
                # Usar CloudinaryService con el UploadFile del parámetro
                cloudinary_result = await CloudinaryService.upload_gallo_photo(
                    file=foto_principal,  # ← PARÁMETRO DEL FORM
                    gallo_codigo=codigo_final,
                    photo_type="principal",
                    user_id=current_user_id
                )
                
                foto_url = cloudinary_result['secure_url']
                cloudinary_url = cloudinary_result.get('urls', {}).get('optimized', foto_url)
                
                # Actualizar gallo principal con URL de foto
                update_foto = text("""
                    UPDATE gallos 
                    SET foto_principal_url = :foto_url, url_foto_cloudinary = :cloudinary_url
                    WHERE id = :id
                """)
                db.execute(update_foto, {
                    "foto_url": foto_url,
                    "cloudinary_url": cloudinary_url,
                    "id": gallo_principal_id
                })
                db.commit()
                
                print(f"✅ Foto subida exitosamente: {cloudinary_url}")
            else:
                print(f"⚠️ No se proporcionó foto_principal en el parámetro")
                
        except Exception as foto_error:
            print(f"❌ Error subiendo foto automática: {foto_error}")
            # No fallar el endpoint por error de foto
        
        return {
            "success": True,
            "message": f"🔥 TÉCNICA ÉPICA COMPLETA - {len(registros_creados)} REGISTROS VINCULADOS",
            "data": {
                "gallo_principal": {
                    "id": gallo_principal_id,
                    "nombre": nombre,
                    "codigo_identificacion": codigo_final.upper(),
                    "padre_id": padre_id,
                    "madre_id": madre_id,
                    "user_id": current_user_id,
                    "id_gallo_genealogico": id_gallo_genealogico,  # 🔥 ES SU PROPIO ID
                    "foto_principal_url": foto_url,
                    "url_foto_cloudinary": cloudinary_url,
                    "foto_subida_automaticamente": foto_url is not None
                },
                "registros_creados": registros_creados,
                "total_registros": len(registros_creados),
                "id_gallo_genealogico": id_gallo_genealogico,
                "tecnica_epica": {
                    "explicacion": f"Todos los familiares de '{nombre}' compartirán id_gallo_genealogico = {id_gallo_genealogico}",
                    "consulta_familia": f"SELECT * FROM gallos WHERE id_gallo_genealogico = {id_gallo_genealogico}",
                    "expandible": "Si después se agregan abuelos, bisabuelos, etc., todos tendrán el mismo id_gallo_genealogico"
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
