# 📸 app/api/v1/fotos_gallos_epica.py - Endpoints ÉPICOS de Fotos con Cloudinary
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.gallo_simple import Gallo
from app.services.cloudinary_service import CloudinaryService
from app.services.validation_service import ValidationService
from app.schemas.gallo import PhotoUploadResponse, SuccessResponse, ErrorResponse

router = APIRouter()

# ========================
# 📸 FOTO PRINCIPAL
# ========================

@router.post("/{gallo_id}/foto-principal", response_model=PhotoUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_foto_principal(
    gallo_id: int,
    foto: UploadFile = File(..., description="Archivo de imagen para foto principal"),
    descripcion: Optional[str] = Form(None, description="Descripción de la foto"),
    reemplazar_existente: bool = Form(True, description="Reemplazar foto existente si existe"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📸 Subir o actualizar foto principal de gallo"""
    
    try:
        # Verificar que el gallo existe y pertenece al usuario
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        print(f"📷 Subiendo foto principal para gallo: {gallo.nombre} ({gallo.codigo_identificacion})")
        
        # Validar archivo
        ValidationService.validate_photo_file(foto)
        
        # Eliminar foto anterior si existe y se va a reemplazar
        foto_anterior_eliminada = None
        if reemplazar_existente and gallo.url_foto_cloudinary:
            try:
                delete_result = CloudinaryService.delete_photo_by_url(gallo.url_foto_cloudinary)
                if delete_result['success']:
                    foto_anterior_eliminada = gallo.url_foto_cloudinary
                    print(f"🗑️ Foto anterior eliminada: {foto_anterior_eliminada}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar foto anterior: {str(e)}")
        
        # Subir nueva foto
        upload_result = CloudinaryService.upload_gallo_photo(
            file=foto,
            gallo_codigo=gallo.codigo_identificacion,
            photo_type="principal",
            user_id=current_user_id
        )
        
        # Actualizar URLs en la base de datos
        gallo.foto_principal_url = upload_result['secure_url']
        gallo.url_foto_cloudinary = upload_result['urls']['optimized']
        
        db.commit()
        
        print(f"✅ Foto principal subida exitosamente: {upload_result['urls']['optimized']}")
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "message": "Foto principal subida exitosamente",
                "data": {
                    "foto_url": upload_result['secure_url'],
                    "foto_optimizada_url": upload_result['urls']['optimized'],
                    "cloudinary_public_id": upload_result['public_id'],
                    "urls_disponibles": upload_result['urls'],
                    "metadata": upload_result['metadata'],
                    "foto_anterior_eliminada": foto_anterior_eliminada,
                    "gallo": {
                        "id": gallo.id,
                        "nombre": gallo.nombre,
                        "codigo_identificacion": gallo.codigo_identificacion
                    }
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error subiendo foto principal: {str(e)}"
        )

@router.delete("/{gallo_id}/foto-principal", response_model=SuccessResponse)
async def delete_foto_principal(
    gallo_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🗑️ Eliminar foto principal de gallo"""
    
    try:
        # Verificar gallo
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        if not gallo.url_foto_cloudinary and not gallo.foto_principal_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El gallo no tiene foto principal"
            )
        
        # Eliminar de Cloudinary
        cloudinary_eliminada = False
        if gallo.url_foto_cloudinary:
            try:
                delete_result = CloudinaryService.delete_photo_by_url(gallo.url_foto_cloudinary)
                cloudinary_eliminada = delete_result['success']
            except Exception as e:
                print(f"⚠️ Error eliminando de Cloudinary: {str(e)}")
        
        # Limpiar URLs en base de datos
        foto_eliminada_url = gallo.url_foto_cloudinary or gallo.foto_principal_url
        gallo.foto_principal_url = None
        gallo.url_foto_cloudinary = None
        
        db.commit()
        
        return {
            "success": True,
            "message": "Foto principal eliminada exitosamente",
            "data": {
                "foto_eliminada_url": foto_eliminada_url,
                "cloudinary_eliminada": cloudinary_eliminada,
                "gallo": {
                    "id": gallo.id,
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
            detail=f"Error eliminando foto principal: {str(e)}"
        )

# ========================
# 📸 FOTOS ADICIONALES
# ========================

@router.post("/{gallo_id}/fotos-adicionales", response_model=PhotoUploadResponse)
async def upload_fotos_adicionales(
    gallo_id: int,
    fotos: List[UploadFile] = File(..., description="Archivos de imágenes adicionales"),
    descripciones: Optional[str] = Form(None, description="Descripciones separadas por comas"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📸 Subir múltiples fotos adicionales"""
    
    try:
        # Verificar gallo
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Validar límite de fotos
        current_additional_photos = len(gallo.fotos_adicionales or [])
        max_additional_photos = 8  # Límite total de fotos adicionales
        
        if current_additional_photos + len(fotos) > max_additional_photos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Límite excedido. Máximo {max_additional_photos} fotos adicionales. Actuales: {current_additional_photos}"
            )
        
        print(f"📷 Subiendo {len(fotos)} fotos adicionales para: {gallo.nombre}")
        
        # Procesar descripciones
        lista_descripciones = []
        if descripciones:
            lista_descripciones = [desc.strip() for desc in descripciones.split(",")]
        
        # Subir fotos a Cloudinary
        upload_results = CloudinaryService.upload_multiple_photos(
            files=fotos,
            gallo_codigo=gallo.codigo_identificacion,
            user_id=current_user_id
        )
        
        if not upload_results['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error subiendo fotos: {upload_results['errors']}"
            )
        
        # Actualizar fotos adicionales en base de datos
        fotos_adicionales_actuales = gallo.fotos_adicionales or []
        
        for i, result in enumerate(upload_results['results']):
            descripcion = lista_descripciones[i] if i < len(lista_descripciones) else f"Foto adicional {len(fotos_adicionales_actuales) + i + 1}"
            
            foto_data = {
                "url": result['secure_url'],
                "url_optimizada": result['urls']['optimized'],
                "public_id": result['public_id'],
                "descripcion": descripcion,
                "metadata": result['metadata'],
                "uploaded_at": datetime.now().isoformat()
            }
            
            fotos_adicionales_actuales.append(foto_data)
        
        gallo.fotos_adicionales = fotos_adicionales_actuales
        db.commit()
        
        print(f"✅ {upload_results['uploaded_count']} fotos adicionales subidas exitosamente")
        
        return {
            "success": True,
            "message": f"{upload_results['uploaded_count']} fotos adicionales subidas exitosamente",
            "data": {
                "fotos_subidas": upload_results['results'],
                "total_fotos_adicionales": len(fotos_adicionales_actuales),
                "limite_fotos": max_additional_photos,
                "fotos_restantes": max_additional_photos - len(fotos_adicionales_actuales),
                "errores": upload_results['errors'],
                "gallo": {
                    "id": gallo.id,
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
            detail=f"Error subiendo fotos adicionales: {str(e)}"
        )

@router.get("/{gallo_id}/fotos", response_model=SuccessResponse)
async def list_fotos_gallo(
    gallo_id: int,
    include_cloudinary_info: bool = False,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Listar todas las fotos de un gallo"""
    
    try:
        # Verificar gallo
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        fotos_data = {
            "foto_principal": None,
            "fotos_adicionales": [],
            "total_fotos": 0
        }
        
        # Foto principal
        if gallo.url_foto_cloudinary or gallo.foto_principal_url:
            fotos_data["foto_principal"] = {
                "url": gallo.foto_principal_url,
                "url_optimizada": gallo.url_foto_cloudinary,
                "tipo": "principal"
            }
            fotos_data["total_fotos"] += 1
        
        # Fotos adicionales
        if gallo.fotos_adicionales:
            fotos_data["fotos_adicionales"] = gallo.fotos_adicionales
            fotos_data["total_fotos"] += len(gallo.fotos_adicionales)
        
        # Información adicional de Cloudinary si se solicita
        cloudinary_info = None
        if include_cloudinary_info:
            try:
                cloudinary_info = CloudinaryService.list_gallo_photos(
                    gallo_codigo=gallo.codigo_identificacion,
                    user_id=current_user_id
                )
            except Exception as e:
                print(f"⚠️ Error obteniendo info de Cloudinary: {str(e)}")
        
        return {
            "success": True,
            "message": f"Fotos de {gallo.nombre} obtenidas exitosamente",
            "data": {
                "gallo": {
                    "id": gallo.id,
                    "nombre": gallo.nombre,
                    "codigo_identificacion": gallo.codigo_identificacion
                },
                "fotos": fotos_data,
                "cloudinary_info": cloudinary_info
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listando fotos: {str(e)}"
        )

@router.delete("/{gallo_id}/fotos/{foto_index}", response_model=SuccessResponse)
async def delete_foto_adicional(
    gallo_id: int,
    foto_index: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🗑️ Eliminar foto adicional específica"""
    
    try:
        # Verificar gallo
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        if not gallo.fotos_adicionales or foto_index >= len(gallo.fotos_adicionales):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Foto no encontrada"
            )
        
        # Obtener foto a eliminar
        foto_a_eliminar = gallo.fotos_adicionales[foto_index]
        
        # Eliminar de Cloudinary
        cloudinary_eliminada = False
        if 'public_id' in foto_a_eliminar:
            try:
                delete_result = CloudinaryService.delete_photo(foto_a_eliminar['public_id'])
                cloudinary_eliminada = delete_result['success']
            except Exception as e:
                print(f"⚠️ Error eliminando de Cloudinary: {str(e)}")
        
        # Eliminar de la lista
        fotos_adicionales_actualizadas = gallo.fotos_adicionales.copy()
        fotos_adicionales_actualizadas.pop(foto_index)
        
        gallo.fotos_adicionales = fotos_adicionales_actualizadas
        db.commit()
        
        return {
            "success": True,
            "message": "Foto adicional eliminada exitosamente",
            "data": {
                "foto_eliminada": foto_a_eliminar,
                "cloudinary_eliminada": cloudinary_eliminada,
                "fotos_restantes": len(fotos_adicionales_actualizadas),
                "gallo": {
                    "id": gallo.id,
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
            detail=f"Error eliminando foto adicional: {str(e)}"
        )

# ========================
# 🧹 UTILIDADES DE FOTOS
# ========================

@router.delete("/{gallo_id}/fotos/all", response_model=SuccessResponse)
async def delete_all_fotos(
    gallo_id: int,
    incluir_principal: bool = False,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🧹 Eliminar todas las fotos de un gallo"""
    
    try:
        # Verificar gallo
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        eliminaciones = {
            "foto_principal": False,
            "fotos_adicionales": 0,
            "cloudinary_eliminadas": 0,
            "errores": []
        }
        
        # Eliminar fotos adicionales
        if gallo.fotos_adicionales:
            for foto in gallo.fotos_adicionales:
                try:
                    if 'public_id' in foto:
                        delete_result = CloudinaryService.delete_photo(foto['public_id'])
                        if delete_result['success']:
                            eliminaciones["cloudinary_eliminadas"] += 1
                except Exception as e:
                    eliminaciones["errores"].append(f"Error eliminando {foto.get('public_id', 'unknown')}: {str(e)}")
            
            eliminaciones["fotos_adicionales"] = len(gallo.fotos_adicionales)
            gallo.fotos_adicionales = []
        
        # Eliminar foto principal si se solicita
        if incluir_principal and (gallo.url_foto_cloudinary or gallo.foto_principal_url):
            try:
                if gallo.url_foto_cloudinary:
                    delete_result = CloudinaryService.delete_photo_by_url(gallo.url_foto_cloudinary)
                    if delete_result['success']:
                        eliminaciones["cloudinary_eliminadas"] += 1
                
                gallo.foto_principal_url = None
                gallo.url_foto_cloudinary = None
                eliminaciones["foto_principal"] = True
                
            except Exception as e:
                eliminaciones["errores"].append(f"Error eliminando foto principal: {str(e)}")
        
        db.commit()
        
        total_eliminadas = eliminaciones["fotos_adicionales"] + (1 if eliminaciones["foto_principal"] else 0)
        
        return {
            "success": True,
            "message": f"{total_eliminadas} fotos eliminadas exitosamente",
            "data": {
                "eliminaciones": eliminaciones,
                "total_fotos_eliminadas": total_eliminadas,
                "gallo": {
                    "id": gallo.id,
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
            detail=f"Error eliminando fotos: {str(e)}"
        )

@router.get("/storage/stats", response_model=SuccessResponse)
async def get_storage_stats(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📊 Estadísticas de almacenamiento de fotos"""
    
    try:
        # Estadísticas de base de datos
        total_gallos = db.query(Gallo).filter(Gallo.user_id == current_user_id).count()
        gallos_con_foto_principal = db.query(Gallo).filter(
            Gallo.user_id == current_user_id,
            (Gallo.foto_principal_url.isnot(None)) |
            (Gallo.url_foto_cloudinary.isnot(None))
        ).count()
        
        # Contar fotos adicionales
        gallos_con_adicionales = db.query(Gallo).filter(
            Gallo.user_id == current_user_id,
            Gallo.fotos_adicionales.isnot(None)
        ).all()
        
        total_fotos_adicionales = sum([
            len(gallo.fotos_adicionales) for gallo in gallos_con_adicionales 
            if gallo.fotos_adicionales
        ])
        
        # Estadísticas de Cloudinary (si están disponibles)
        cloudinary_stats = None
        try:
            cloudinary_stats = CloudinaryService.get_storage_stats()
        except Exception as e:
            print(f"⚠️ Error obteniendo stats de Cloudinary: {str(e)}")
        
        return {
            "success": True,
            "message": "Estadísticas de almacenamiento obtenidas",
            "data": {
                "database_stats": {
                    "total_gallos": total_gallos,
                    "gallos_con_foto_principal": gallos_con_foto_principal,
                    "gallos_con_fotos_adicionales": len(gallos_con_adicionales),
                    "total_fotos_adicionales": total_fotos_adicionales,
                    "total_fotos": gallos_con_foto_principal + total_fotos_adicionales,
                    "promedio_fotos_por_gallo": (gallos_con_foto_principal + total_fotos_adicionales) / total_gallos if total_gallos > 0 else 0
                },
                "cloudinary_stats": cloudinary_stats,
                "user_id": current_user_id
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )

# Importar datetime que faltaba
from datetime import datetime

print("📸 Endpoints épicos de fotos con Cloudinary cargados exitosamente!")
