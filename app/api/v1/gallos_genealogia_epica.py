# 🔥 app/api/v1/gallos_genealogia_epica.py - ENDPOINT ÉPICO con Técnica Recursiva
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.gallo_simple import Gallo
from app.services.cloudinary_service import CloudinaryService
from app.services.genealogy_service import GenealogyService
from app.services.validation_service import ValidationService
from app.schemas.gallo import (
    GenealogyCreateResponse, GallosListResponse, GalloDetailResponse,
    PhotoUploadResponse, GenealogySearchResponse, ErrorResponse,
    GalloSearchParams, GenealogySearchParams, DashboardStats,
    SuccessResponse, CodeValidationResponse
)

router = APIRouter()

# ========================
# 🔥 ENDPOINT ÉPICO PRINCIPAL - TÉCNICA RECURSIVA GENEALÓGICA
# ========================

@router.post("/with-genealogy", response_model=GenealogyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_gallo_with_genealogy(
    # 🐓 DATOS DEL GALLO PRINCIPAL
    nombre: str = Form(..., description="Nombre del gallo"),
    codigo_identificacion: str = Form(..., description="Código único de identificación"),
    raza_id: Optional[int] = Form(None, description="ID de la raza"),
    fecha_nacimiento: Optional[str] = Form(None, description="Fecha de nacimiento (YYYY-MM-DD)"),
    peso: Optional[float] = Form(None, description="Peso en kg"),
    altura: Optional[int] = Form(None, description="Altura en cm"),
    color: Optional[str] = Form(None, description="Color principal"),
    estado: str = Form("activo", description="Estado del gallo"),
    procedencia: Optional[str] = Form(None, description="Procedencia del gallo"),
    notas: Optional[str] = Form(None, description="Notas adicionales"),
    
    # 📋 CAMPOS ADICIONALES DETALLADOS
    color_plumaje: Optional[str] = Form(None, description="Color específico del plumaje"),
    color_placa: Optional[str] = Form(None, description="Color de la placa identificatoria"),
    ubicacion_placa: Optional[str] = Form(None, description="Ubicación de la placa"),
    color_patas: Optional[str] = Form(None, description="Color de las patas"),
    criador: Optional[str] = Form(None, description="Nombre del criador"),
    propietario_actual: Optional[str] = Form(None, description="Propietario actual"),
    observaciones: Optional[str] = Form(None, description="Observaciones adicionales"),
    numero_registro: Optional[str] = Form(None, description="Número de registro"),
    
    # 📸 FOTO PRINCIPAL
    foto_principal: Optional[UploadFile] = File(None, description="Foto principal del gallo"),
    
    # 🧬 CONTROL DE GENEALOGÍA
    crear_padre: bool = Form(False, description="Crear padre automáticamente"),
    crear_madre: bool = Form(False, description="Crear madre automáticamente"),
    padre_id: Optional[int] = Form(None, description="ID de padre existente"),
    madre_id: Optional[int] = Form(None, description="ID de madre existente"),
    
    # 👨 DATOS DEL PADRE (si crear_padre=True)
    padre_nombre: Optional[str] = Form(None, description="Nombre del padre"),
    padre_codigo: Optional[str] = Form(None, description="Código del padre"),
    padre_raza_id: Optional[int] = Form(None, description="Raza del padre"),
    padre_color: Optional[str] = Form(None, description="Color del padre"),
    padre_peso: Optional[float] = Form(None, description="Peso del padre"),
    padre_procedencia: Optional[str] = Form(None, description="Procedencia del padre"),
    padre_notas: Optional[str] = Form(None, description="Notas del padre"),
    padre_color_plumaje: Optional[str] = Form(None, description="Color plumaje del padre"),
    padre_color_patas: Optional[str] = Form(None, description="Color patas del padre"),
    padre_criador: Optional[str] = Form(None, description="Criador del padre"),
    
    # 👩 DATOS DE LA MADRE (si crear_madre=True)
    madre_nombre: Optional[str] = Form(None, description="Nombre de la madre"),
    madre_codigo: Optional[str] = Form(None, description="Código de la madre"),
    madre_raza_id: Optional[int] = Form(None, description="Raza de la madre"),
    madre_color: Optional[str] = Form(None, description="Color de la madre"),
    madre_peso: Optional[float] = Form(None, description="Peso de la madre"),
    madre_procedencia: Optional[str] = Form(None, description="Procedencia de la madre"),
    madre_notas: Optional[str] = Form(None, description="Notas de la madre"),
    madre_color_plumaje: Optional[str] = Form(None, description="Color plumaje de la madre"),
    madre_color_patas: Optional[str] = Form(None, description="Color patas de la madre"),
    madre_criador: Optional[str] = Form(None, description="Criador de la madre"),
    
    # 🔐 DEPENDENCIAS
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    🔥 ENDPOINT ÉPICO: Crear gallo con técnica recursiva genealógica
    
    **Funcionalidades épicas:**
    - ✅ Crea gallo principal con datos completos
    - ✅ Sube foto principal a Cloudinary automáticamente
    - ✅ Crea padres automáticamente si se especifica
    - ✅ Establece relaciones genealógicas con técnica recursiva
    - ✅ Valida códigos únicos y previene ciclos genealógicos
    - ✅ Retorna estructura completa para Flutter
    - ✅ Maneja errores robustamente con rollback automático
    
    **Casos de uso:**
    1. **Gallo solo:** Solo datos principales, sin padres
    2. **Gallo con padres existentes:** Usa padre_id y madre_id
    3. **Gallo con padre nuevo:** crear_padre=True + datos del padre
    4. **Gallo con madre nueva:** crear_madre=True + datos de la madre
    5. **Gallo completo:** Crear padre y madre nuevos automáticamente
    
    **Técnica recursiva:**
    - Genera `id_gallo_genealogico` único para vincular familia
    - Permite expansión genealógica infinita posteriormente
    - Optimizada para consultas rápidas con índices
    """
    
    try:
        print(f"🚀 Iniciando creación genealógica épica para usuario {current_user_id}")
        print(f"📋 Gallo: {nombre} ({codigo_identificacion})")
        print(f"🧬 Crear padre: {crear_padre}, Crear madre: {crear_madre}")
        
        # ========================
        # 🔍 PASO 1: VALIDACIONES INICIALES
        # ========================
        
        # Validar datos del gallo principal
        gallo_data = {
            'nombre': nombre,
            'codigo_identificacion': codigo_identificacion,
            'raza_id': raza_id,
            'fecha_nacimiento': fecha_nacimiento,
            'peso': peso,
            'altura': altura,
            'color': color,
            'estado': estado,
            'procedencia': procedencia,
            'notas': notas,
            'color_plumaje': color_plumaje,
            'color_placa': color_placa,
            'ubicacion_placa': ubicacion_placa,
            'color_patas': color_patas,
            'criador': criador,
            'propietario_actual': propietario_actual,
            'observaciones': observaciones,
            'numero_registro': numero_registro,
            'user_id': current_user_id
        }
        
        # Preparar datos de padres si se van a crear
        padre_data = None
        if crear_padre and padre_nombre and padre_codigo:
            padre_data = {
                'nombre': padre_nombre,
                'codigo_identificacion': padre_codigo,
                'raza_id': padre_raza_id,
                'color': padre_color,
                'peso': padre_peso,
                'procedencia': padre_procedencia,
                'notas': padre_notas,
                'color_plumaje': padre_color_plumaje,
                'color_patas': padre_color_patas,
                'criador': padre_criador,
                'user_id': current_user_id
            }
        
        madre_data = None
        if crear_madre and madre_nombre and madre_codigo:
            madre_data = {
                'nombre': madre_nombre,
                'codigo_identificacion': madre_codigo,
                'raza_id': madre_raza_id,
                'color': madre_color,
                'peso': madre_peso,
                'procedencia': madre_procedencia,
                'notas': madre_notas,
                'color_plumaje': madre_color_plumaje,
                'color_patas': madre_color_patas,
                'criador': madre_criador,
                'user_id': current_user_id
            }
        
        # Validar datos completos
        validated_data = ValidationService.validate_genealogy_data(
            gallo_data=gallo_data,
            padre_data=padre_data,
            madre_data=madre_data
        )
        
        print(f"✅ Validaciones completadas exitosamente")
        
        # Validar códigos únicos
        ValidationService.validate_codigo_unique(
            db=db,
            codigo=codigo_identificacion,
            user_id=current_user_id
        )
        
        if padre_data:
            ValidationService.validate_codigo_unique(
                db=db,
                codigo=padre_codigo,
                user_id=current_user_id
            )
        
        if madre_data:
            ValidationService.validate_codigo_unique(
                db=db,
                codigo=madre_codigo,
                user_id=current_user_id
            )
        
        print(f"✅ Códigos únicos validados")
        
        # ========================
        # 📸 PASO 2: SUBIR FOTO A CLOUDINARY (si existe)
        # ========================
        
        foto_principal_url = None
        cloudinary_url = None
        
        if foto_principal:
            print(f"📷 Subiendo foto principal para {codigo_identificacion}")
            
            # Validar archivo de foto
            ValidationService.validate_photo_file(foto_principal)
            
            # Subir a Cloudinary
            cloudinary_result = CloudinaryService.upload_gallo_photo(
                file=foto_principal,
                gallo_codigo=codigo_identificacion,
                photo_type="principal",
                user_id=current_user_id
            )
            
            foto_principal_url = cloudinary_result['secure_url']
            cloudinary_url = cloudinary_result['urls']['optimized']
            
            print(f"✅ Foto subida exitosamente: {cloudinary_url}")
            
            # Agregar URLs de fotos a los datos
            validated_data['gallo_data']['foto_principal_url'] = foto_principal_url
            validated_data['gallo_data']['url_foto_cloudinary'] = cloudinary_url
        
        # ========================
        # 🧬 PASO 3: APLICAR TÉCNICA RECURSIVA GENEALÓGICA ÉPICA
        # ========================
        
        print(f"🔥 Aplicando técnica recursiva genealógica...")
        
        genealogy_result = GenealogyService.create_with_parents(
            db=db,
            gallo_data=validated_data['gallo_data'],
            padre_data=validated_data['padre_data'],
            madre_data=validated_data['madre_data'],
            padre_existente_id=padre_id,
            madre_existente_id=madre_id
        )
        
        print(f"🎯 Técnica aplicada exitosamente:")
        print(f"   - Gallo principal ID: {genealogy_result['gallo_principal'].id}")
        print(f"   - Genealogy ID: {genealogy_result['genealogy_id']}")
        print(f"   - Total registros: {genealogy_result['total_registros_creados']}")
        
        # ========================
        # 📊 PASO 4: GENERAR RESPUESTA ÉPICA PARA FLUTTER
        # ========================
        
        # Obtener datos de raza si existe
        raza_data = None
        if genealogy_result['gallo_principal'].raza:
            raza_data = {
                'id': genealogy_result['gallo_principal'].raza.id,
                'nombre': genealogy_result['gallo_principal'].raza.nombre,
                'descripcion': getattr(genealogy_result['gallo_principal'].raza, 'descripcion', None),
                'origen': getattr(genealogy_result['gallo_principal'].raza, 'origen', None)
            }
        
        # Construir respuesta épica
        response_data = {
            "gallo_principal": {
                "id": genealogy_result['gallo_principal'].id,
                "nombre": genealogy_result['gallo_principal'].nombre,
                "codigo_identificacion": genealogy_result['gallo_principal'].codigo_identificacion,
                "raza": raza_data,
                "peso": float(genealogy_result['gallo_principal'].peso) if genealogy_result['gallo_principal'].peso else None,
                "altura": genealogy_result['gallo_principal'].altura,
                "color": genealogy_result['gallo_principal'].color,
                "estado": genealogy_result['gallo_principal'].estado,
                "foto_principal_url": genealogy_result['gallo_principal'].foto_principal_url,
                "url_foto_cloudinary": genealogy_result['gallo_principal'].url_foto_cloudinary,
                "padre_id": genealogy_result['gallo_principal'].padre_id,
                "madre_id": genealogy_result['gallo_principal'].madre_id,
                "id_gallo_genealogico": genealogy_result['gallo_principal'].id_gallo_genealogico,
                "tipo_registro": genealogy_result['gallo_principal'].tipo_registro,
                "created_at": genealogy_result['gallo_principal'].created_at.isoformat()
            },
            "padre_creado": None,
            "madre_creada": None,
            "total_registros_creados": genealogy_result['total_registros_creados'],
            "genealogy_summary": {
                "genealogy_id": genealogy_result['genealogy_id'],
                "generaciones_disponibles": 1 if (genealogy_result['padre_creado'] or genealogy_result['madre_creada']) else 0,
                "ancestros_totales": sum([1 for x in [genealogy_result['padre_creado'], genealogy_result['madre_creada']] if x]),
                "lineas_completas": 1 if (genealogy_result['padre_creado'] and genealogy_result['madre_creada']) else 0,
                "tiene_padre": genealogy_result['gallo_principal'].padre_id is not None,
                "tiene_madre": genealogy_result['gallo_principal'].madre_id is not None
            }
        }
        
        # Agregar datos del padre si fue creado
        if genealogy_result['padre_creado']:
            response_data["padre_creado"] = {
                "id": genealogy_result['padre_creado'].id,
                "nombre": genealogy_result['padre_creado'].nombre,
                "codigo_identificacion": genealogy_result['padre_creado'].codigo_identificacion,
                "estado": genealogy_result['padre_creado'].estado,
                "tipo_registro": genealogy_result['padre_creado'].tipo_registro,
                "id_gallo_genealogico": genealogy_result['padre_creado'].id_gallo_genealogico,
                "created_at": genealogy_result['padre_creado'].created_at.isoformat()
            }
        
        # Agregar datos de la madre si fue creada
        if genealogy_result['madre_creada']:
            response_data["madre_creada"] = {
                "id": genealogy_result['madre_creada'].id,
                "nombre": genealogy_result['madre_creada'].nombre,
                "codigo_identificacion": genealogy_result['madre_creada'].codigo_identificacion,
                "estado": genealogy_result['madre_creada'].estado,
                "tipo_registro": genealogy_result['madre_creada'].tipo_registro,
                "id_gallo_genealogico": genealogy_result['madre_creada'].id_gallo_genealogico,
                "created_at": genealogy_result['madre_creada'].created_at.isoformat()
            }
        
        print(f"🏆 ¡TÉCNICA RECURSIVA GENEALÓGICA APLICADA EXITOSAMENTE!")
        print(f"   - Usuario: {current_user_id}")
        print(f"   - Gallo: {genealogy_result['gallo_principal'].nombre}")
        print(f"   - Familia ID: {genealogy_result['genealogy_id']}")
        print(f"   - Registros totales: {genealogy_result['total_registros_creados']}")
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "message": f"🔥 TÉCNICA GENEALÓGICA ÉPICA APLICADA - {genealogy_result['total_registros_creados']} registros creados",
                "data": response_data
            }
        )
        
    except HTTPException as he:
        # Limpiar foto de Cloudinary si hubo error
        if foto_principal_url:
            try:
                CloudinaryService.delete_photo_by_url(foto_principal_url)
                print(f"🧹 Foto limpiada de Cloudinary por error HTTP")
            except:
                pass
        
        print(f"❌ Error HTTP: {he.detail}")
        raise he
        
    except Exception as e:
        # Limpiar foto de Cloudinary si hubo error
        if foto_principal_url:
            try:
                CloudinaryService.delete_photo_by_url(foto_principal_url)
                print(f"🧹 Foto limpiada de Cloudinary por error inesperado")
            except:
                pass
        
        print(f"💥 Error inesperado en técnica genealógica: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno aplicando técnica genealógica: {str(e)}"
        )

# ========================
# 📋 ENDPOINTS CRUD BÁSICOS
# ========================

@router.get("", response_model=GallosListResponse)
async def list_gallos(
    page: int = Query(1, ge=1, description="Página actual"),
    limit: int = Query(20, ge=1, le=100, description="Elementos por página"),
    search: Optional[str] = Query(None, min_length=2, description="Buscar por nombre o código"),
    raza_id: Optional[int] = Query(None, description="Filtrar por raza"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    tiene_foto: Optional[bool] = Query(None, description="Solo gallos con foto"),
    tiene_padres: Optional[bool] = Query(None, description="Solo gallos con genealogía"),
    sort_by: str = Query("created_at", description="Campo para ordenar"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Orden"),
    include_genealogy: bool = Query(False, description="Incluir datos genealógicos"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Listar gallos con filtros avanzados y paginación"""
    
    try:
        # Validar parámetros
        search_params = {
            'page': page,
            'limit': limit,
            'search': search,
            'raza_id': raza_id,
            'estado': estado,
            'tiene_foto': tiene_foto,
            'tiene_padres': tiene_padres,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'include_genealogy': include_genealogy
        }
        
        validated_params = ValidationService.validate_search_params(search_params)
        
        # Construir consulta base
        query = db.query(Gallo).filter(Gallo.user_id == current_user_id)
        
        # Aplicar filtros
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Gallo.nombre.ilike(search_term)) |
                (Gallo.codigo_identificacion.ilike(search_term))
            )
        
        if raza_id:
            query = query.filter(Gallo.raza_id == raza_id)
        
        if estado:
            query = query.filter(Gallo.estado == estado)
        
        if tiene_foto is not None:
            if tiene_foto:
                query = query.filter(
                    (Gallo.foto_principal_url.isnot(None)) |
                    (Gallo.url_foto_cloudinary.isnot(None))
                )
            else:
                query = query.filter(
                    (Gallo.foto_principal_url.is_(None)) &
                    (Gallo.url_foto_cloudinary.is_(None))
                )
        
        if tiene_padres is not None:
            if tiene_padres:
                query = query.filter(
                    (Gallo.padre_id.isnot(None)) |
                    (Gallo.madre_id.isnot(None))
                )
            else:
                query = query.filter(
                    (Gallo.padre_id.is_(None)) &
                    (Gallo.madre_id.is_(None))
                )
        
        # Ordenar
        if sort_by == "nombre":
            order_col = Gallo.nombre
        elif sort_by == "codigo_identificacion":
            order_col = Gallo.codigo_identificacion
        elif sort_by == "peso":
            order_col = Gallo.peso
        else:
            order_col = Gallo.created_at
        
        if sort_order == "desc":
            query = query.order_by(order_col.desc())
        else:
            query = query.order_by(order_col.asc())
        
        # Contar total
        total_count = query.count()
        
        # Aplicar paginación
        offset = (page - 1) * limit
        gallos = query.offset(offset).limit(limit).all()
        
        # Procesar resultados
        gallos_data = []
        for gallo in gallos:
            gallo_dict = {
                "id": gallo.id,
                "nombre": gallo.nombre,
                "codigo_identificacion": gallo.codigo_identificacion,
                "raza": {
                    "id": gallo.raza.id,
                    "nombre": gallo.raza.nombre
                } if gallo.raza else None,
                "peso": float(gallo.peso) if gallo.peso else None,
                "altura": gallo.altura,
                "color": gallo.color,
                "estado": gallo.estado,
                "foto_principal_url": gallo.foto_principal_url,
                "url_foto_cloudinary": gallo.url_foto_cloudinary,
                "tipo_registro": gallo.tipo_registro,
                "id_gallo_genealogico": gallo.id_gallo_genealogico,
                "padre_id": gallo.padre_id,
                "madre_id": gallo.madre_id,
                "created_at": gallo.created_at.isoformat()
            }
            
            # Incluir genealogía si se solicita
            if include_genealogy and (gallo.padre_id or gallo.madre_id):
                genealogia = {
                    "padre": None,
                    "madre": None,
                    "generaciones_disponibles": 0
                }
                
                if gallo.padre:
                    genealogia["padre"] = {
                        "id": gallo.padre.id,
                        "nombre": gallo.padre.nombre,
                        "codigo_identificacion": gallo.padre.codigo_identificacion,
                        "foto_principal_url": gallo.padre.foto_principal_url
                    }
                
                if gallo.madre:
                    genealogia["madre"] = {
                        "id": gallo.madre.id,
                        "nombre": gallo.madre.nombre,
                        "codigo_identificacion": gallo.madre.codigo_identificacion,
                        "foto_principal_url": gallo.madre.foto_principal_url
                    }
                
                genealogia["generaciones_disponibles"] = 1
                gallo_dict["genealogia"] = genealogia
            
            gallos_data.append(gallo_dict)
        
        # Calcular paginación
        total_pages = (total_count + limit - 1) // limit
        
        # Estadísticas rápidas
        stats = {
            "total_gallos": total_count,
            "gallos_con_foto": db.query(Gallo).filter(
                Gallo.user_id == current_user_id,
                (Gallo.foto_principal_url.isnot(None)) |
                (Gallo.url_foto_cloudinary.isnot(None))
            ).count(),
            "gallos_con_padres": db.query(Gallo).filter(
                Gallo.user_id == current_user_id,
                (Gallo.padre_id.isnot(None)) |
                (Gallo.madre_id.isnot(None))
            ).count()
        }
        
        return {
            "success": True,
            "data": {
                "gallos": gallos_data,
                "pagination": {
                    "current_page": page,
                    "per_page": limit,
                    "total_pages": total_pages,
                    "total_count": total_count,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                },
                "filters_applied": {
                    "search": search,
                    "raza_id": raza_id,
                    "estado": estado,
                    "tiene_foto": tiene_foto,
                    "tiene_padres": tiene_padres,
                    "include_genealogy": include_genealogy
                },
                "stats": stats
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listando gallos: {str(e)}"
        )

@router.get("/{gallo_id}", response_model=GalloDetailResponse)
async def get_gallo_detail(
    gallo_id: int,
    include_genealogy: bool = Query(True, description="Incluir árbol genealógico"),
    include_descendants: bool = Query(False, description="Incluir descendientes"),
    genealogy_depth: int = Query(3, ge=1, le=10, description="Profundidad genealógica"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📋 Obtener detalle completo de gallo con genealogía"""
    
    try:
        # Buscar gallo
        gallo = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Datos básicos del gallo
        gallo_data = {
            "id": gallo.id,
            "nombre": gallo.nombre,
            "codigo_identificacion": gallo.codigo_identificacion,
            "raza": {
                "id": gallo.raza.id,
                "nombre": gallo.raza.nombre,
                "descripcion": getattr(gallo.raza, 'descripcion', None),
                "origen": getattr(gallo.raza, 'origen', None)
            } if gallo.raza else None,
            "fecha_nacimiento": gallo.fecha_nacimiento.isoformat() if gallo.fecha_nacimiento else None,
            "peso": float(gallo.peso) if gallo.peso else None,
            "altura": gallo.altura,
            "color": gallo.color,
            "estado": gallo.estado,
            "procedencia": gallo.procedencia,
            "notas": gallo.notas,
            "color_plumaje": gallo.color_plumaje,
            "color_placa": gallo.color_placa,
            "ubicacion_placa": gallo.ubicacion_placa,
            "color_patas": gallo.color_patas,
            "criador": gallo.criador,
            "propietario_actual": gallo.propietario_actual,
            "observaciones": gallo.observaciones,
            "numero_registro": gallo.numero_registro,
            "foto_principal_url": gallo.foto_principal_url,
            "url_foto_cloudinary": gallo.url_foto_cloudinary,
            "fotos_adicionales": gallo.fotos_adicionales or [],
            "tipo_registro": gallo.tipo_registro,
            "id_gallo_genealogico": gallo.id_gallo_genealogico,
            "padre_id": gallo.padre_id,
            "madre_id": gallo.madre_id,
            "created_at": gallo.created_at.isoformat(),
            "updated_at": gallo.updated_at.isoformat()
        }
        
        response_data = {"gallo": gallo_data}
        
        # Incluir genealogía si se solicita
        if include_genealogy:
            genealogy_data = GenealogyService.get_family_tree(
                db=db,
                gallo_id=gallo_id,
                max_depth=genealogy_depth,
                include_descendants=include_descendants
            )
            response_data["genealogia"] = genealogy_data
        
        return {
            "success": True,
            "data": response_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo detalle de gallo: {str(e)}"
        )

# ========================
# 🌳 ENDPOINTS GENEALÓGICOS AVANZADOS
# ========================

@router.get("/{gallo_id}/genealogia", response_model=GenealogySearchResponse)
async def get_family_tree(
    gallo_id: int,
    max_depth: int = Query(5, ge=1, le=10, description="Profundidad máxima del árbol"),
    include_descendants: bool = Query(True, description="Incluir descendientes"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🌳 Obtener árbol genealógico completo de un gallo"""
    
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
        
        # Obtener árbol genealógico
        family_tree = GenealogyService.get_family_tree(
            db=db,
            gallo_id=gallo_id,
            max_depth=max_depth,
            include_descendants=include_descendants
        )
        
        return {
            "success": True,
            "data": family_tree
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo árbol genealógico: {str(e)}"
        )

@router.get("/search/genealogia", response_model=GenealogySearchResponse)
async def search_by_genealogy(
    genealogy_id: Optional[int] = Query(None, description="ID de familia genealógica"),
    ancestro_id: Optional[int] = Query(None, description="Buscar descendientes de este ancestro"),
    descendiente_id: Optional[int] = Query(None, description="Buscar ancestros de este descendiente"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🔍 Búsqueda avanzada por genealogía"""
    
    try:
        if not any([genealogy_id, ancestro_id, descendiente_id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe especificar al menos un parámetro de búsqueda"
            )
        
        # Realizar búsqueda genealógica
        search_results = GenealogyService.search_by_genealogy(
            db=db,
            genealogy_id=genealogy_id,
            ancestro_id=ancestro_id,
            descendiente_id=descendiente_id,
            user_id=current_user_id
        )
        
        return {
            "success": True,
            "data": search_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda genealógica: {str(e)}"
        )

# ========================
# 📊 ENDPOINTS DE ESTADÍSTICAS
# ========================

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """📊 Estadísticas del dashboard"""
    
    try:
        # Obtener estadísticas genealógicas
        genealogy_stats = GenealogyService.get_genealogy_stats(db=db, user_id=current_user_id)
        
        # Estadísticas adicionales
        total_gallos = db.query(Gallo).filter(Gallo.user_id == current_user_id).count()
        gallos_con_foto = db.query(Gallo).filter(
            Gallo.user_id == current_user_id,
            (Gallo.foto_principal_url.isnot(None)) |
            (Gallo.url_foto_cloudinary.isnot(None))
        ).count()
        
        return {
            "success": True,
            "data": {
                "resumen_general": genealogy_stats['data']['estadisticas_generales'],
                "distribucion_por_raza": [],  # Implementar si tienes tabla de razas
                "estadisticas_genealogicas": genealogy_stats['data']['familias_genealogicas'],
                "actividad_reciente": [],  # Implementar según necesidades
                "fotos_estadisticas": {
                    "total_fotos": gallos_con_foto,
                    "storage_usado_mb": 0,  # Implementar con Cloudinary stats
                    "promedio_fotos_por_gallo": gallos_con_foto / total_gallos if total_gallos > 0 else 0
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )

# ========================
# ✅ ENDPOINTS DE UTILIDADES
# ========================

@router.get("/validate-codigo/{codigo}", response_model=CodeValidationResponse)
async def validate_codigo_unique(
    codigo: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """✅ Validar que un código sea único"""
    
    try:
        # Limpiar código
        codigo_clean = codigo.strip().upper()
        
        # Buscar conflictos
        existing = db.query(Gallo).filter(
            Gallo.codigo_identificacion == codigo_clean,
            Gallo.user_id == current_user_id
        ).first()
        
        response_data = {
            "codigo": codigo_clean,
            "disponible": existing is None,
            "conflicto_con": None,
            "sugerencias": []
        }
        
        if existing:
            response_data["conflicto_con"] = {
                "id": existing.id,
                "nombre": existing.nombre,
                "tipo_registro": existing.tipo_registro
            }
            
            # Generar sugerencias
            base_codigo = codigo_clean[:15]  # Máximo 15 chars para dejar espacio
            sugerencias = []
            for i in range(1, 6):
                sugerencia = f"{base_codigo}{i:02d}"
                existing_sug = db.query(Gallo).filter(
                    Gallo.codigo_identificacion == sugerencia,
                    Gallo.user_id == current_user_id
                ).first()
                if not existing_sug:
                    sugerencias.append(sugerencia)
            
            response_data["sugerencias"] = sugerencias[:3]  # Max 3 sugerencias
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validando código: {str(e)}"
        )

print("🔥 Endpoints épicos de técnica recursiva genealógica cargados exitosamente!")
