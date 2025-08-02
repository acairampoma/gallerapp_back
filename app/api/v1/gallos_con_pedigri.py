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
    raza_id: Optional[str] = Form(None),  # Cambiado a varchar
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
    raza_id: Optional[str] = Form(None),  # Cambiado a varchar
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
        
        db.execute(update_gallo, {
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
        })
        
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
