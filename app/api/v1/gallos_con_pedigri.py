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

# 🐓 LISTAR TODOS LOS GALLOS DEL USUARIO - ENDPOINT QUE FALTABA
@router.get("/", response_model=dict)
async def get_gallos_usuario(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🔥 LISTAR TODOS LOS GALLOS DEL USUARIO AUTENTICADO
    Incluye fotos, pedigrí y datos completos
    """
    try:
        # Consulta SQL para obtener todos los gallos del usuario
        query = text("""
            SELECT 
                id, user_id, raza_id, nombre, codigo_identificacion, 
                fecha_nacimiento, peso, altura, color, estado,
                padre_id, madre_id, foto_principal_url, fotos_adicionales,
                procedencia, notas, created_at, updated_at,
                id_gallo_genealogico, url_foto_cloudinary,
                color_placa, ubicacion_placa, color_patas, color_plumaje,
                criador, propietario_actual, observaciones,
                numero_registro, tipo_registro
            FROM gallos 
            WHERE user_id = :user_id
            ORDER BY created_at DESC
        """)
        
        result = db.execute(query, {"user_id": current_user_id})
        gallos_raw = result.fetchall()
        
        # Convertir a lista de diccionarios
        gallos_list = []
        for gallo in gallos_raw:
            gallo_dict = {
                "id": gallo.id,
                "user_id": gallo.user_id,
                "raza_id": gallo.raza_id,
                "nombre": gallo.nombre,
                "codigo_identificacion": gallo.codigo_identificacion,
                "fecha_nacimiento": gallo.fecha_nacimiento.isoformat() if gallo.fecha_nacimiento else None,
                "peso": str(gallo.peso) if gallo.peso else None,
                "altura": gallo.altura,
                "color": gallo.color,
                "estado": gallo.estado,
                "padre_id": gallo.padre_id,
                "madre_id": gallo.madre_id,
                "foto_principal_url": gallo.foto_principal_url,
                "url_foto_cloudinary": gallo.url_foto_cloudinary,
                "fotos_adicionales": gallo.fotos_adicionales,
                "procedencia": gallo.procedencia,
                "notas": gallo.notas,
                "color_placa": gallo.color_placa,
                "ubicacion_placa": gallo.ubicacion_placa,
                "color_patas": gallo.color_patas,
                "color_plumaje": gallo.color_plumaje,
                "criador": gallo.criador,
                "propietario_actual": gallo.propietario_actual,
                "observaciones": gallo.observaciones,
                "numero_registro": gallo.numero_registro,
                "tipo_registro": gallo.tipo_registro,
                "id_gallo_genealogico": gallo.id_gallo_genealogico,
                "created_at": gallo.created_at.isoformat() if gallo.created_at else None,
                "updated_at": gallo.updated_at.isoformat() if gallo.updated_at else None
            }
            gallos_list.append(gallo_dict)
        
        return {
            "success": True,
            "data": {
                "gallos": gallos_list,
                "total": len(gallos_list),
                "user_id": current_user_id
            },
            "message": f"Se encontraron {len(gallos_list)} gallos"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo gallos: {str(e)}"
        )

@router.post("/con-pedigri", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_gallo_con_pedigri(
    # DATOS DEL GALLO PRINCIPAL
    nombre: str = Form(...),
    codigo_identificacion: str = Form(...),
    fecha_nacimiento: Optional[str] = Form(None),
    numero_registro: Optional[str] = Form(None),  # NUEVO CAMPO
    color_placa: Optional[str] = Form(None),      # NUEVO CAMPO
    ubicacion_placa: Optional[str] = Form(None),  # NUEVO CAMPO
    raza_id: Optional[str] = Form(None, description="ID o nombre de la raza del gallo"),
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
    padre_raza_id: Optional[str] = Form(None),  # Cambiado a varchar
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
    madre_raza_id: Optional[str] = Form(None),  # Cambiado a varchar 
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
        
        # 🔍 DEBUG: Verificar qué valor tiene raza_id
        print(f"🔍 DEBUG POST - raza_id recibido: '{raza_id}' (tipo: {type(raza_id)})")
        
        # 🛠️ NORMALIZAR raza_id: convertir string vacío a None
        if raza_id == "" or raza_id == "null" or raza_id == "undefined":
            raza_id = None
        print(f"🔍 DEBUG POST - raza_id normalizado: '{raza_id}'")
        
        # Insertar gallo principal PRIMERO (sin padres aún)
        # Usar numero_registro como codigo si está disponible, sino usar codigo_identificacion
        codigo_final = numero_registro or codigo_identificacion
        
        # 🔍 DEBUG: Mostrar exactamente qué se va a insertar
        params_to_insert = {
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
        }
        print(f"🔍 DEBUG POST - Parámetros a insertar: raza_id='{params_to_insert['raza_id']}'")
        
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
        
        try:
            result_gallo = db.execute(insert_gallo, params_to_insert)
            print(f"✅ DEBUG POST - INSERT ejecutado exitosamente")
        except Exception as insert_error:
            print(f"❌ DEBUG POST - ERROR EN INSERT: {insert_error}")
            raise
        
        gallo_row = result_gallo.fetchone()
        gallo_principal_id = gallo_row.id
        
        # 🔍 DEBUG: Verificar qué se guardó en la base de datos
        debug_query = text("SELECT id, nombre, raza_id FROM gallos WHERE id = :id")
        debug_result = db.execute(debug_query, {"id": gallo_principal_id})
        debug_gallo = debug_result.fetchone()
        print(f"🔍 DEBUG POST - Gallo guardado: ID={debug_gallo.id}, nombre='{debug_gallo.nombre}', raza_id='{debug_gallo.raza_id}'")
        
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

@router.put("/{gallo_id}", response_model=dict)
async def update_gallo_con_expansion(
    gallo_id: int,
    # DATOS DEL GALLO PRINCIPAL - TODOS LOS CAMPOS COMO EN POST
    nombre: str = Form(...),
    codigo_identificacion: str = Form(...),
    fecha_nacimiento: Optional[str] = Form(None),
    numero_registro: Optional[str] = Form(None),  # NUEVO CAMPO
    color_placa: Optional[str] = Form(None),      # NUEVO CAMPO
    ubicacion_placa: Optional[str] = Form(None),  # NUEVO CAMPO
    raza_id: Optional[str] = Form(None, description="ID o nombre de la raza del gallo"),
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
    
    # DATOS DEL PADRE (OPCIONAL) - TODOS LOS CAMPOS
    crear_padre: bool = Form(False),
    padre_nombre: Optional[str] = Form(None),
    padre_fecha_nacimiento: Optional[str] = Form(None),  # NUEVO CAMPO
    padre_numero_registro: Optional[str] = Form(None),   # NUEVO CAMPO
    padre_color_placa: Optional[str] = Form(None),       # NUEVO CAMPO
    padre_ubicacion_placa: Optional[str] = Form(None),   # NUEVO CAMPO
    padre_codigo: Optional[str] = Form(None), 
    padre_raza_id: Optional[str] = Form(None),  # Cambiado a varchar
    padre_color: Optional[str] = Form(None),
    padre_peso: Optional[float] = Form(None),
    padre_procedencia: Optional[str] = Form(None),
    padre_notas: Optional[str] = Form(None),
    
    # DATOS DE LA MADRE (OPCIONAL) - TODOS LOS CAMPOS
    crear_madre: bool = Form(False),
    madre_nombre: Optional[str] = Form(None),
    madre_fecha_nacimiento: Optional[str] = Form(None),  # NUEVO CAMPO
    madre_numero_registro: Optional[str] = Form(None),   # NUEVO CAMPO
    madre_color_placa: Optional[str] = Form(None),       # NUEVO CAMPO
    madre_ubicacion_placa: Optional[str] = Form(None),   # NUEVO CAMPO
    madre_codigo: Optional[str] = Form(None),
    madre_raza_id: Optional[str] = Form(None),  # Cambiado a varchar 
    madre_color: Optional[str] = Form(None),
    madre_peso: Optional[float] = Form(None),
    madre_procedencia: Optional[str] = Form(None),
    madre_notas: Optional[str] = Form(None),
    
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🔥 TÉCNICA ÉPICA: Actualizar gallo con pedigrí completo
    - Incluye TODOS los campos del POST
    - Maneja genealogía completa como en create
    - Actualiza o crea padres según necesidad
    """
    
    try:
        registros_actualizados = []
        padre_id = None
        madre_id = None
        
        # Verificar que el gallo existe y obtener datos actuales
        query_check = text("SELECT * FROM gallos WHERE id = :id AND user_id = :user_id")
        gallo_actual = db.execute(query_check, {"id": gallo_id, "user_id": current_user_id}).fetchone()
        
        if not gallo_actual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Validar código único (solo si cambió)
        if codigo_identificacion.upper() != gallo_actual.codigo_identificacion:
            query_check_codigo = text("SELECT id FROM gallos WHERE codigo_identificacion = :codigo AND user_id = :user_id AND id != :gallo_id")
            existing = db.execute(query_check_codigo, {
                "codigo": codigo_identificacion.upper(), 
                "user_id": current_user_id,
                "gallo_id": gallo_id
            }).fetchone()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otro gallo con el código '{codigo_identificacion}'"
                )
        
        # Procesar fecha
        fecha_nacimiento_parsed = None
        if fecha_nacimiento:
            try:
                fecha_nacimiento_parsed = datetime.fromisoformat(fecha_nacimiento).date()
            except:
                pass
        
        # 🔍 DEBUG: Verificar qué valor tiene raza_id en PUT
        print(f"🔍 DEBUG PUT - raza_id recibido: '{raza_id}' (tipo: {type(raza_id)})")
        
        # 🛠️ NORMALIZAR raza_id: convertir string vacío a None
        if raza_id == "" or raza_id == "null" or raza_id == "undefined":
            raza_id = None
        print(f"🔍 DEBUG PUT - raza_id normalizado: '{raza_id}'")
        
        # Usar numero_registro como codigo si está disponible, sino usar codigo_identificacion
        codigo_final = numero_registro or codigo_identificacion
        
        # 🔥 OBTENER ID GENEALÓGICO ACTUAL
        id_gallo_genealogico = gallo_actual.id_gallo_genealogico or gallo_id
        
        # MANEJAR CREACIÓN/ACTUALIZACIÓN DE PADRE
        if crear_padre and padre_nombre:
            # Usar numero_registro del padre si está disponible
            padre_codigo_final = padre_numero_registro or padre_codigo or f"P_{codigo_final}"
            
            # Procesar fecha del padre
            padre_fecha_parsed = None
            if padre_fecha_nacimiento:
                try:
                    padre_fecha_parsed = datetime.fromisoformat(padre_fecha_nacimiento).date()
                except:
                    pass
            
            # Verificar si ya existe un padre
            if gallo_actual.padre_id:
                # ACTUALIZAR PADRE EXISTENTE
                update_padre = text("""
                    UPDATE gallos SET 
                        nombre = :nombre,
                        codigo_identificacion = :codigo,
                        fecha_nacimiento = :fecha_nacimiento,
                        numero_registro = :numero_registro,
                        color_placa = :color_placa,
                        ubicacion_placa = :ubicacion_placa,
                        raza_id = :raza_id,
                        peso = :peso,
                        color = :color,
                        procedencia = :procedencia,
                        notas = :notas,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :padre_id AND user_id = :user_id
                """)
                
                db.execute(update_padre, {
                    "padre_id": gallo_actual.padre_id,
                    "user_id": current_user_id,
                    "nombre": padre_nombre,
                    "codigo": padre_codigo_final.upper(),
                    "fecha_nacimiento": padre_fecha_parsed,
                    "numero_registro": padre_numero_registro,
                    "color_placa": padre_color_placa,
                    "ubicacion_placa": padre_ubicacion_placa,
                    "raza_id": padre_raza_id,
                    "peso": padre_peso,
                    "color": padre_color,
                    "procedencia": padre_procedencia,
                    "notas": padre_notas
                })
                
                padre_id = gallo_actual.padre_id
                registros_actualizados.append({
                    "tipo": "padre_actualizado",
                    "id": padre_id,
                    "nombre": padre_nombre,
                    "codigo": padre_codigo_final.upper()
                })
            else:
                # CREAR NUEVO PADRE
                insert_padre = text("""
                    INSERT INTO gallos (
                        user_id, nombre, codigo_identificacion, fecha_nacimiento,
                        numero_registro, color_placa, ubicacion_placa, raza_id, peso, color,
                        estado, procedencia, notas, id_gallo_genealogico, tipo_registro,
                        created_at, updated_at
                    ) VALUES (
                        :user_id, :nombre, :codigo, :fecha_nacimiento,
                        :numero_registro, :color_placa, :ubicacion_placa, :raza_id, :peso, :color,
                        'padre', :procedencia, :notas, :id_gallo_genealogico, 'padre_generado',
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    ) RETURNING id, created_at
                """)
                
                result_padre = db.execute(insert_padre, {
                    "user_id": current_user_id,
                    "nombre": padre_nombre,
                    "codigo": padre_codigo_final.upper(),
                    "fecha_nacimiento": padre_fecha_parsed,
                    "numero_registro": padre_numero_registro,
                    "color_placa": padre_color_placa,
                    "ubicacion_placa": padre_ubicacion_placa,
                    "raza_id": padre_raza_id,
                    "peso": padre_peso,
                    "color": padre_color,
                    "procedencia": padre_procedencia,
                    "notas": padre_notas,
                    "id_gallo_genealogico": id_gallo_genealogico
                })
                
                padre_row = result_padre.fetchone()
                padre_id = padre_row.id
                
                registros_actualizados.append({
                    "tipo": "padre_creado",
                    "id": padre_id,
                    "nombre": padre_nombre,
                    "codigo": padre_codigo_final.upper(),
                    "id_gallo_genealogico": id_gallo_genealogico,
                    "created_at": padre_row.created_at.isoformat()
                })
        else:
            # Mantener padre actual si existe
            padre_id = gallo_actual.padre_id
        
        # MANEJAR CREACIÓN/ACTUALIZACIÓN DE MADRE
        if crear_madre and madre_nombre:
            # Usar numero_registro de la madre si está disponible
            madre_codigo_final = madre_numero_registro or madre_codigo or f"M_{codigo_final}"
            
            # Procesar fecha de la madre
            madre_fecha_parsed = None
            if madre_fecha_nacimiento:
                try:
                    madre_fecha_parsed = datetime.fromisoformat(madre_fecha_nacimiento).date()
                except:
                    pass
            
            # Verificar si ya existe una madre
            if gallo_actual.madre_id:
                # ACTUALIZAR MADRE EXISTENTE
                update_madre = text("""
                    UPDATE gallos SET 
                        nombre = :nombre,
                        codigo_identificacion = :codigo,
                        fecha_nacimiento = :fecha_nacimiento,
                        numero_registro = :numero_registro,
                        color_placa = :color_placa,
                        ubicacion_placa = :ubicacion_placa,
                        raza_id = :raza_id,
                        peso = :peso,
                        color = :color,
                        procedencia = :procedencia,
                        notas = :notas,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :madre_id AND user_id = :user_id
                """)
                
                db.execute(update_madre, {
                    "madre_id": gallo_actual.madre_id,
                    "user_id": current_user_id,
                    "nombre": madre_nombre,
                    "codigo": madre_codigo_final.upper(),
                    "fecha_nacimiento": madre_fecha_parsed,
                    "numero_registro": madre_numero_registro,
                    "color_placa": madre_color_placa,
                    "ubicacion_placa": madre_ubicacion_placa,
                    "raza_id": madre_raza_id,
                    "peso": madre_peso,
                    "color": madre_color,
                    "procedencia": madre_procedencia,
                    "notas": madre_notas
                })
                
                madre_id = gallo_actual.madre_id
                registros_actualizados.append({
                    "tipo": "madre_actualizada",
                    "id": madre_id,
                    "nombre": madre_nombre,
                    "codigo": madre_codigo_final.upper()
                })
            else:
                # CREAR NUEVA MADRE
                insert_madre = text("""
                    INSERT INTO gallos (
                        user_id, nombre, codigo_identificacion, fecha_nacimiento,
                        numero_registro, color_placa, ubicacion_placa, raza_id, peso, color,
                        estado, procedencia, notas, id_gallo_genealogico, tipo_registro,
                        created_at, updated_at
                    ) VALUES (
                        :user_id, :nombre, :codigo, :fecha_nacimiento,
                        :numero_registro, :color_placa, :ubicacion_placa, :raza_id, :peso, :color,
                        'madre', :procedencia, :notas, :id_gallo_genealogico, 'madre_generada',
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    ) RETURNING id, created_at
                """)
                
                result_madre = db.execute(insert_madre, {
                    "user_id": current_user_id,
                    "nombre": madre_nombre,
                    "codigo": madre_codigo_final.upper(),
                    "fecha_nacimiento": madre_fecha_parsed,
                    "numero_registro": madre_numero_registro,
                    "color_placa": madre_color_placa,
                    "ubicacion_placa": madre_ubicacion_placa,
                    "raza_id": madre_raza_id,
                    "peso": madre_peso,
                    "color": madre_color,
                    "procedencia": madre_procedencia,
                    "notas": madre_notas,
                    "id_gallo_genealogico": id_gallo_genealogico
                })
                
                madre_row = result_madre.fetchone()
                madre_id = madre_row.id
                
                registros_actualizados.append({
                    "tipo": "madre_creada",
                    "id": madre_id,
                    "nombre": madre_nombre,
                    "codigo": madre_codigo_final.upper(),
                    "id_gallo_genealogico": id_gallo_genealogico,
                    "created_at": madre_row.created_at.isoformat()
                })
        else:
            # Mantener madre actual si existe
            madre_id = gallo_actual.madre_id
        
        # 🔍 DEBUG: Mostrar exactamente qué se va a actualizar
        params_to_update = {
            "id": gallo_id,
            "user_id": current_user_id,
            "nombre": nombre,
            "codigo": codigo_final.upper(),
            "fecha_nacimiento": fecha_nacimiento_parsed,
            "numero_registro": numero_registro,
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
            "observaciones": observaciones,
            "padre_id": padre_id,
            "madre_id": madre_id,
            "id_gallo_genealogico": id_gallo_genealogico
        }
        print(f"🔍 DEBUG PUT - Parámetros a actualizar: raza_id='{params_to_update['raza_id']}'")
        
        # ACTUALIZAR GALLO PRINCIPAL CON TODOS LOS CAMPOS
        update_gallo = text("""
            UPDATE gallos SET 
                nombre = :nombre,
                codigo_identificacion = :codigo,
                fecha_nacimiento = :fecha_nacimiento,
                numero_registro = :numero_registro,
                color_placa = :color_placa,
                ubicacion_placa = :ubicacion_placa,
                raza_id = :raza_id,
                peso = :peso,
                altura = :altura,
                color = :color,
                estado = :estado,
                procedencia = :procedencia,
                notas = :notas,
                color_patas = :color_patas,
                color_plumaje = :color_plumaje,
                criador = :criador,
                propietario_actual = :propietario_actual,
                observaciones = :observaciones,
                padre_id = :padre_id,
                madre_id = :madre_id,
                id_gallo_genealogico = :id_gallo_genealogico,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :id AND user_id = :user_id
        """)
        
        try:
            result_update = db.execute(update_gallo, params_to_update)
            print(f"✅ DEBUG PUT - UPDATE ejecutado exitosamente")
            print(f"🔍 DEBUG PUT - Filas afectadas: {result_update.rowcount}")
        except Exception as update_error:
            print(f"❌ DEBUG PUT - ERROR EN UPDATE: {update_error}")
            raise
        
        # 🔍 DEBUG: Verificar qué se actualizó en la base de datos
        debug_query = text("SELECT id, nombre, raza_id FROM gallos WHERE id = :id")
        debug_result = db.execute(debug_query, {"id": gallo_id})
        debug_gallo = debug_result.fetchone()
        print(f"🔍 DEBUG PUT - Gallo actualizado: ID={debug_gallo.id}, nombre='{debug_gallo.nombre}', raza_id='{debug_gallo.raza_id}'")
        
        registros_actualizados.append({
            "tipo": "gallo_principal_actualizado",
            "id": gallo_id,
            "nombre": nombre,
            "codigo": codigo_final.upper()
        })
        
        # 🔥 SUBIR FOTO IGUAL QUE EL POST
        foto_url = gallo_actual.foto_principal_url  # Mantener foto actual por defecto
        cloudinary_url = gallo_actual.url_foto_cloudinary
        
        if foto_principal:
            try:
                print(f"📷 Subiendo nueva foto para gallo {gallo_id}")
                
                cloudinary_result = await CloudinaryService.upload_gallo_photo(
                    file=foto_principal,
                    gallo_codigo=codigo_final,
                    photo_type="principal",
                    user_id=current_user_id
                )
                
                foto_url = cloudinary_result['secure_url']
                cloudinary_url = cloudinary_result.get('urls', {}).get('optimized', foto_url)
                
                # ACTUALIZAR URLs DE FOTO
                update_foto = text("""
                    UPDATE gallos 
                    SET foto_principal_url = :foto_url, url_foto_cloudinary = :cloudinary_url
                    WHERE id = :id
                """)
                db.execute(update_foto, {
                    "foto_url": foto_url,
                    "cloudinary_url": cloudinary_url,
                    "id": gallo_id
                })
                
                print(f"✅ Foto actualizada exitosamente: {cloudinary_url}")
            except Exception as foto_error:
                print(f"❌ Error subiendo foto: {foto_error}")
                # No fallar el update por error de foto
        
        # Commit todo junto
        db.commit()
        
        return {
            "success": True,
            "message": f"🔥 TÉCNICA ÉPICA COMPLETA - Gallo actualizado con {len(registros_actualizados)} cambios",
            "data": {
                "gallo_principal": {
                    "id": gallo_id,
                    "nombre": nombre,
                    "codigo_identificacion": codigo_final.upper(),
                    "padre_id": padre_id,
                    "madre_id": madre_id,
                    "user_id": current_user_id,
                    "id_gallo_genealogico": id_gallo_genealogico,
                    "foto_principal_url": foto_url,
                    "url_foto_cloudinary": cloudinary_url,
                    "foto_actualizada": foto_principal is not None
                },
                "registros_actualizados": registros_actualizados,
                "total_cambios": len(registros_actualizados),
                "id_gallo_genealogico": id_gallo_genealogico,
                "tecnica_epica": {
                    "explicacion": f"Gallo '{nombre}' actualizado manteniendo id_gallo_genealogico = {id_gallo_genealogico}",
                    "consulta_familia": f"SELECT * FROM gallos WHERE id_gallo_genealogico = {id_gallo_genealogico}",
                    "funcionalidad": "PUT ahora tiene la misma funcionalidad completa que POST"
                },
                "pedigri_actualizado": {
                    "tiene_padre": padre_id is not None,
                    "tiene_madre": madre_id is not None,
                    "padres_creados_o_actualizados": crear_padre or crear_madre
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando pedigri: {str(e)}"
        )

# 📄🐓 EXPORTAR FICHA PDF DE GALLO
@router.post("/{gallo_id}/exportar-ficha")
async def exportar_ficha_gallo(
    gallo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🔥 EXPORTAR FICHA COMPLETA DE GALLO EN PDF
    
    Genera PDF épico con:
    - Foto del gallo
    - Estadísticas completas 
    - Genealogía con fotos
    - Historial de peleas
    - Gráficos de rendimiento
    """
    try:
        # 1. OBTENER DATOS COMPLETOS DEL GALLO
        query_gallo = text("""
            SELECT 
                g.id, g.nombre, g.codigo_identificacion, g.fecha_nacimiento,
                g.peso, g.altura, g.color, g.estado, g.procedencia, g.notas,
                g.foto_principal_url, g.url_foto_cloudinary,
                g.color_placa, g.ubicacion_placa, g.color_patas, g.color_plumaje,
                g.criador, g.propietario_actual, g.observaciones,
                g.numero_registro, g.tipo_registro,
                r.nombre as raza_nombre,
                -- Datos del padre
                p.id as padre_id, p.nombre as padre_nombre, p.codigo_identificacion as padre_codigo,
                p.foto_principal_url as padre_foto, pr.nombre as padre_raza,
                -- Datos de la madre
                m.id as madre_id, m.nombre as madre_nombre, m.codigo_identificacion as madre_codigo,
                m.foto_principal_url as madre_foto, mr.nombre as madre_raza
            FROM gallos g
            LEFT JOIN razas r ON g.raza_id::integer = r.id
            LEFT JOIN gallos p ON g.padre_id = p.id
            LEFT JOIN razas pr ON p.raza_id::integer = pr.id
            LEFT JOIN gallos m ON g.madre_id = m.id
            LEFT JOIN razas mr ON m.raza_id::integer = mr.id
            WHERE g.id = :gallo_id AND g.user_id = :user_id::integer
        """)
        
        gallo_result = db.execute(query_gallo, {
            "gallo_id": gallo_id,
            "user_id": current_user_id
        }).fetchone()
        
        if not gallo_result:
            raise HTTPException(
                status_code=404,
                detail="Gallo no encontrado"
            )
        
        # 2. OBTENER ESTADÍSTICAS DE PELEAS
        query_peleas = text("""
            SELECT 
                COUNT(*) as total_peleas,
                COUNT(CASE WHEN resultado = 'ganada' THEN 1 END) as peleas_ganadas,
                COUNT(CASE WHEN resultado = 'perdida' THEN 1 END) as peleas_perdidas,
                ROUND(
                    COALESCE(
                        COUNT(CASE WHEN resultado = 'ganada' THEN 1 END)::numeric / 
                        NULLIF(COUNT(*), 0) * 100, 
                        0
                    ), 1
                ) as efectividad,
                SUM(CASE WHEN resultado = 'ganada' THEN COALESCE(premio, 0) ELSE 0 END) as ingresos_totales
            FROM peleas 
            WHERE gallo_id = :gallo_id
        """)
        
        stats_result = db.execute(query_peleas, {"gallo_id": gallo_id}).fetchone()
        
        # 3. OBTENER HISTORIAL RECIENTE DE PELEAS (últimas 10)
        query_historial = text("""
            SELECT 
                fecha_pelea,
                lugar,
                contrincante,
                resultado,
                tiempo_pelea,
                premio
            FROM peleas 
            WHERE gallo_id = :gallo_id
            ORDER BY fecha_pelea DESC
            LIMIT 10
        """)
        
        historial_result = db.execute(query_historial, {"gallo_id": gallo_id}).fetchall()
        
        # 4. OBTENER DATOS DE TOPES (ENTRENAMIENTOS)
        query_topes = text("""
            SELECT COUNT(*) as total_topes
            FROM topes 
            WHERE gallo_id = :gallo_id
        """)
        
        topes_result = db.execute(query_topes, {"gallo_id": gallo_id}).fetchone()
        
        # 5. CONSTRUIR RESPUESTA COMPLETA PARA PDF
        ficha_data = {
            "gallo": {
                "id": gallo_result.id,
                "nombre": gallo_result.nombre,
                "codigo": gallo_result.codigo_identificacion,
                "fecha_nacimiento": gallo_result.fecha_nacimiento.isoformat() if gallo_result.fecha_nacimiento else None,
                "peso": str(gallo_result.peso) if gallo_result.peso else None,
                "altura": gallo_result.altura,
                "color": gallo_result.color,
                "estado": gallo_result.estado,
                "raza": gallo_result.raza_nombre,
                "foto_url": gallo_result.url_foto_cloudinary or gallo_result.foto_principal_url,
                "criador": gallo_result.criador,
                "propietario": gallo_result.propietario_actual,
                "numero_registro": gallo_result.numero_registro,
                "observaciones": gallo_result.observaciones
            },
            "genealogia": {
                "padre": {
                    "id": gallo_result.padre_id,
                    "nombre": gallo_result.padre_nombre,
                    "codigo": gallo_result.padre_codigo,
                    "raza": gallo_result.padre_raza,
                    "foto_url": gallo_result.padre_foto
                } if gallo_result.padre_id else None,
                "madre": {
                    "id": gallo_result.madre_id,
                    "nombre": gallo_result.madre_nombre,
                    "codigo": gallo_result.madre_codigo,
                    "raza": gallo_result.madre_raza,
                    "foto_url": gallo_result.madre_foto
                } if gallo_result.madre_id else None
            },
            "estadisticas": {
                "total_peleas": stats_result.total_peleas or 0,
                "peleas_ganadas": stats_result.peleas_ganadas or 0,
                "peleas_perdidas": stats_result.peleas_perdidas or 0,
                "efectividad": float(stats_result.efectividad or 0),
                "ingresos_totales": float(stats_result.ingresos_totales or 0),
                "total_topes": topes_result.total_topes or 0
            },
            "historial_peleas": [
                {
                    "fecha": pelea.fecha_pelea.isoformat() if pelea.fecha_pelea else None,
                    "lugar": pelea.lugar,
                    "contrincante": pelea.contrincante,
                    "resultado": pelea.resultado,
                    "tiempo": pelea.tiempo_pelea,
                    "premio": float(pelea.premio or 0)
                }
                for pelea in historial_result
            ],
            "metadata": {
                "fecha_generacion": datetime.now().isoformat(),
                "usuario_id": current_user_id,
                "tipo_reporte": "ficha_completa",
                "version": "v1.0"
            }
        }
        
        # 6. AQUÍ SE INTEGRARÁ LA GENERACIÓN DE PDF
        # Por ahora retornamos los datos para que Flutter los use
        return {
            "success": True,
            "message": f"Ficha de {gallo_result.nombre} generada exitosamente",
            "data": ficha_data,
            "pdf_url": None,  # Se agregará cuando implementemos PDF generator
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando ficha: {str(e)}"
        )
