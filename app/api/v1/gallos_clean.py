# 🐓 app/api/v1/gallos_clean.py - ENDPOINTS LIMPIOS Y ESENCIALES
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.gallo import Gallo
from app.models.raza import Raza
from app.models.foto import FotoGallo
from app.services.cloudinary_service import CloudinaryService
from app.services.validation_service import ValidationService

router = APIRouter()

# ========================================
# 🐓 CRUD BÁSICO DE GALLOS (5 ENDPOINTS)
# ========================================

@router.get("", response_model=dict)
async def list_gallos(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Listar TODOS los gallos del usuario (Flutter filtra localmente)"""
    
    try:
        # Query simple: todos los gallos del usuario con raza
        gallos = db.query(Gallo).filter(
            Gallo.user_id == current_user_id
        ).join(Raza, Gallo.raza_id == Raza.id, isouter=True).all()
        
        # Serializar datos básicos para Flutter
        gallos_data = []
        for gallo in gallos:
            gallos_data.append({
                "id": gallo.id,
                "nombre": gallo.nombre,
                "codigo_identificacion": gallo.codigo_identificacion,
                "raza_id": gallo.raza_id,
                "raza_nombre": gallo.raza.nombre if gallo.raza else None,
                "fecha_nacimiento": gallo.fecha_nacimiento.isoformat() if gallo.fecha_nacimiento else None,
                "peso": float(gallo.peso) if gallo.peso else None,
                "altura": gallo.altura,
                "color": gallo.color,
                "estado": gallo.estado,
                "procedencia": gallo.procedencia,
                "foto_principal_url": gallo.foto_principal_url,
                "padre_id": gallo.padre_id,
                "madre_id": gallo.madre_id,
                "created_at": gallo.created_at.isoformat(),
                "updated_at": gallo.updated_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "gallos": gallos_data,
                "total": len(gallos_data)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo gallos: {str(e)}"
        )

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_gallo(
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
    foto: Optional[UploadFile] = File(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🆕 Crear nuevo gallo (con foto opcional)"""
    
    try:
        # Validar código único
        existing_gallo = db.query(Gallo).filter(
            Gallo.codigo_identificacion == codigo_identificacion,
            Gallo.user_id == current_user_id
        ).first()
        
        if existing_gallo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un gallo con el código '{codigo_identificacion}'"
            )
        
        # Procesar fecha
        fecha_nacimiento_date = None
        if fecha_nacimiento:
            try:
                fecha_nacimiento_date = datetime.fromisoformat(fecha_nacimiento).date()
            except:
                pass
        
        # Crear gallo
        nuevo_gallo = Gallo(
            user_id=current_user_id,
            nombre=nombre,
            codigo_identificacion=codigo_identificacion.upper(),
            raza_id=raza_id,
            fecha_nacimiento=fecha_nacimiento_date,
            peso=peso,
            altura=altura,
            color=color,
            estado=estado,
            procedencia=procedencia,
            notas=notas,
            padre_id=padre_id,
            madre_id=madre_id
        )
        
        db.add(nuevo_gallo)
        db.commit()
        db.refresh(nuevo_gallo)
        
        # Subir foto si se proporcionó
        foto_url = None
        if foto:
            try:
                ValidationService.validate_photo_file(foto)
                cloudinary_result = CloudinaryService.upload_gallo_photo(
                    file=foto,
                    gallo_codigo=nuevo_gallo.codigo_identificacion,
                    photo_type="principal"
                )
                
                # Actualizar URL en el gallo
                nuevo_gallo.foto_principal_url = cloudinary_result["secure_url"]
                
                # Crear registro de foto
                nueva_foto = FotoGallo(
                    gallo_id=nuevo_gallo.id,
                    cloudinary_public_id=cloudinary_result["public_id"],
                    foto_url=cloudinary_result["secure_url"],
                    tipo="principal",
                    descripcion="Foto principal",
                    foto_metadata=cloudinary_result["metadata"]
                )
                db.add(nueva_foto)
                db.commit()
                
                foto_url = cloudinary_result["secure_url"]
                
            except Exception as e:
                print(f"Error subiendo foto: {e}")
        
        return {
            "success": True,
            "message": "Gallo creado exitosamente",
            "data": {
                "gallo": {
                    "id": nuevo_gallo.id,
                    "nombre": nuevo_gallo.nombre,
                    "codigo_identificacion": nuevo_gallo.codigo_identificacion,
                    "foto_principal_url": foto_url,
                    "created_at": nuevo_gallo.created_at.isoformat()
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
async def get_gallo(
    gallo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🔍 Obtener gallo específico con detalles completos"""
    
    try:
        # Obtener gallo con raza
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Obtener fotos
        fotos = db.query(FotoGallo).filter(
            FotoGallo.gallo_id == gallo_id
        ).order_by(FotoGallo.tipo.desc(), FotoGallo.orden).all()
        
        fotos_data = [
            {
                "id": foto.id,
                "url": foto.foto_url,
                "tipo": foto.tipo,
                "descripcion": foto.descripcion,
                "orden": foto.orden
            }
            for foto in fotos
        ]
        
        # Obtener padres si existen
        padre = None
        madre = None
        
        if gallo.padre_id:
            padre_obj = db.query(Gallo).filter(Gallo.id == gallo.padre_id).first()
            if padre_obj:
                padre = {
                    "id": padre_obj.id,
                    "nombre": padre_obj.nombre,
                    "codigo_identificacion": padre_obj.codigo_identificacion,
                    "foto_principal_url": padre_obj.foto_principal_url
                }
        
        if gallo.madre_id:
            madre_obj = db.query(Gallo).filter(Gallo.id == gallo.madre_id).first()
            if madre_obj:
                madre = {
                    "id": madre_obj.id,
                    "nombre": madre_obj.nombre,
                    "codigo_identificacion": madre_obj.codigo_identificacion,
                    "foto_principal_url": madre_obj.foto_principal_url
                }
        
        return {
            "success": True,
            "data": {
                "gallo": {
                    "id": gallo.id,
                    "nombre": gallo.nombre,
                    "codigo_identificacion": gallo.codigo_identificacion,
                    "raza_id": gallo.raza_id,
                    "raza_nombre": gallo.raza.nombre if gallo.raza else None,
                    "fecha_nacimiento": gallo.fecha_nacimiento.isoformat() if gallo.fecha_nacimiento else None,
                    "peso": float(gallo.peso) if gallo.peso else None,
                    "altura": gallo.altura,
                    "color": gallo.color,
                    "estado": gallo.estado,
                    "procedencia": gallo.procedencia,
                    "notas": gallo.notas,
                    "foto_principal_url": gallo.foto_principal_url,
                    "padre_id": gallo.padre_id,
                    "madre_id": gallo.madre_id,
                    "created_at": gallo.created_at.isoformat(),
                    "updated_at": gallo.updated_at.isoformat(),
                    
                    # Datos adicionales
                    "fotos": fotos_data,
                    "padre": padre,
                    "madre": madre
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo gallo: {str(e)}"
        )

@router.put("/{gallo_id}", response_model=dict)
async def update_gallo(
    gallo_id: int,
    nombre: Optional[str] = Form(None),
    peso: Optional[float] = Form(None),
    altura: Optional[int] = Form(None),
    color: Optional[str] = Form(None),
    estado: Optional[str] = Form(None),
    procedencia: Optional[str] = Form(None),
    notas: Optional[str] = Form(None),
    padre_id: Optional[int] = Form(None),
    madre_id: Optional[int] = Form(None),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """✏️ Editar gallo existente"""
    
    try:
        # Obtener gallo
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Actualizar campos
        cambios = []
        if nombre and nombre != gallo.nombre:
            gallo.nombre = nombre
            cambios.append("nombre")
        
        if peso is not None and peso != gallo.peso:
            gallo.peso = peso
            cambios.append("peso")
            
        if altura is not None and altura != gallo.altura:
            gallo.altura = altura
            cambios.append("altura")
            
        if color and color != gallo.color:
            gallo.color = color
            cambios.append("color")
            
        if estado and estado != gallo.estado:
            gallo.estado = estado
            cambios.append("estado")
            
        if procedencia != gallo.procedencia:
            gallo.procedencia = procedencia
            cambios.append("procedencia")
            
        if notas != gallo.notas:
            gallo.notas = notas
            cambios.append("notas")
            
        if padre_id != gallo.padre_id:
            gallo.padre_id = padre_id
            cambios.append("padre")
            
        if madre_id != gallo.madre_id:
            gallo.madre_id = madre_id
            cambios.append("madre")
        
        if not cambios:
            return {
                "success": True,
                "message": "No hay cambios para aplicar",
                "data": {"gallo_id": gallo_id}
            }
        
        gallo.updated_at = datetime.now()
        db.commit()
        
        return {
            "success": True,
            "message": "Gallo actualizado exitosamente",
            "data": {
                "gallo_id": gallo_id,
                "cambios": cambios,
                "updated_at": gallo.updated_at.isoformat()
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
async def delete_gallo(
    gallo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🗑️ Eliminar gallo"""
    
    try:
        # Obtener gallo
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Verificar si es padre o madre de otros gallos
        descendientes = db.query(Gallo).filter(
            (Gallo.padre_id == gallo_id) | (Gallo.madre_id == gallo_id)
        ).count()
        
        if descendientes > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar. Este gallo es padre/madre de {descendientes} gallos"
            )
        
        # Eliminar fotos de Cloudinary
        fotos = db.query(FotoGallo).filter(FotoGallo.gallo_id == gallo_id).all()
        for foto in fotos:
            try:
                CloudinaryService.delete_photo(foto.cloudinary_public_id)
            except:
                pass
        
        # Eliminar registros
        db.query(FotoGallo).filter(FotoGallo.gallo_id == gallo_id).delete()
        db.delete(gallo)
        db.commit()
        
        return {
            "success": True,
            "message": "Gallo eliminado exitosamente",
            "data": {
                "gallo_eliminado": {
                    "id": gallo_id,
                    "nombre": gallo.nombre,
                    "codigo_identificacion": gallo.codigo_identificacion
                },
                "fotos_eliminadas": len(fotos)
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
