# ✅ app/services/validation_service.py - Servicio ÉPICO de Validaciones
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from typing import Optional, Dict, List, Any
import re
from datetime import datetime, date
from decimal import Decimal
import magic

from app.models.gallo_simple import Gallo

class ValidationService:
    """🔍 Servicio épico para validaciones robustas del sistema"""
    
    # 📋 CONFIGURACIONES DE VALIDACIÓN
    CODIGO_PATTERN = r'^[A-Z0-9]{3,20}$'  # Solo letras mayúsculas y números, 3-20 caracteres
    NOMBRE_MIN_LENGTH = 2
    NOMBRE_MAX_LENGTH = 255
    PESO_MIN = 0.5  # kg
    PESO_MAX = 10.0  # kg
    ALTURA_MIN = 20  # cm
    ALTURA_MAX = 100  # cm
    ESTADOS_VALIDOS = ['activo', 'inactivo', 'padre', 'madre', 'campeon', 'retirado', 'vendido']
    TIPOS_REGISTRO_VALIDOS = ['principal', 'padre_generado', 'madre_generada']
    
    @staticmethod
    def validate_codigo_identificacion(codigo: str, exclude_id: Optional[int] = None) -> bool:
        """🔍 Validar código de identificación único"""
        
        if not codigo:
            raise HTTPException(
                status_code=400,
                detail="El código de identificación es obligatorio"
            )
        
        # Limpiar y convertir a mayúsculas
        codigo_clean = codigo.strip().upper()
        
        # Validar formato
        if not re.match(ValidationService.CODIGO_PATTERN, codigo_clean):
            raise HTTPException(
                status_code=400,
                detail=f"Código inválido. Use solo letras y números (3-20 caracteres): {codigo_clean}"
            )
        
        return True
    
    @staticmethod
    def validate_codigo_unique(
        db: Session, 
        codigo: str, 
        user_id: int, 
        exclude_id: Optional[int] = None
    ) -> bool:
        """🔍 Validar que el código sea único para el usuario"""
        
        # Primero validar formato
        ValidationService.validate_codigo_identificacion(codigo, exclude_id)
        
        codigo_clean = codigo.strip().upper()
        
        # Verificar unicidad en la base de datos
        query = db.query(Gallo).filter(
            Gallo.codigo_identificacion == codigo_clean,
            Gallo.user_id == user_id
        )
        
        if exclude_id:
            query = query.filter(Gallo.id != exclude_id)
        
        existing = query.first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un gallo con el código '{codigo_clean}' en tu colección"
            )
        
        return True
    
    @staticmethod
    def validate_nombre(nombre: str) -> bool:
        """🔍 Validar nombre del gallo"""
        
        if not nombre:
            raise HTTPException(
                status_code=400,
                detail="El nombre es obligatorio"
            )
        
        nombre_clean = nombre.strip()
        
        if len(nombre_clean) < ValidationService.NOMBRE_MIN_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"El nombre debe tener al menos {ValidationService.NOMBRE_MIN_LENGTH} caracteres"
            )
        
        if len(nombre_clean) > ValidationService.NOMBRE_MAX_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"El nombre no puede exceder {ValidationService.NOMBRE_MAX_LENGTH} caracteres"
            )
        
        # Validar caracteres especiales peligrosos
        forbidden_chars = ['<', '>', '"', "'", '&', '|', ';']
        if any(char in nombre_clean for char in forbidden_chars):
            raise HTTPException(
                status_code=400,
                detail="El nombre contiene caracteres no permitidos"
            )
        
        return True
    
    @staticmethod
    def validate_peso(peso: Optional[float]) -> bool:
        """🔍 Validar peso del gallo"""
        
        if peso is None:
            return True  # Peso es opcional
        
        if not isinstance(peso, (int, float, Decimal)):
            raise HTTPException(
                status_code=400,
                detail="El peso debe ser un número válido"
            )
        
        peso_float = float(peso)
        
        if peso_float < ValidationService.PESO_MIN:
            raise HTTPException(
                status_code=400,
                detail=f"El peso mínimo es {ValidationService.PESO_MIN} kg"
            )
        
        if peso_float > ValidationService.PESO_MAX:
            raise HTTPException(
                status_code=400,
                detail=f"El peso máximo es {ValidationService.PESO_MAX} kg"
            )
        
        return True
    
    @staticmethod
    def validate_altura(altura: Optional[int]) -> bool:
        """🔍 Validar altura del gallo"""
        
        if altura is None:
            return True  # Altura es opcional
        
        if not isinstance(altura, int) or altura <= 0:
            raise HTTPException(
                status_code=400,
                detail="La altura debe ser un número entero positivo"
            )
        
        if altura < ValidationService.ALTURA_MIN:
            raise HTTPException(
                status_code=400,
                detail=f"La altura mínima es {ValidationService.ALTURA_MIN} cm"
            )
        
        if altura > ValidationService.ALTURA_MAX:
            raise HTTPException(
                status_code=400,
                detail=f"La altura máxima es {ValidationService.ALTURA_MAX} cm"
            )
        
        return True
    
    @staticmethod
    def validate_estado(estado: str) -> bool:
        """🔍 Validar estado del gallo"""
        
        if not estado:
            raise HTTPException(
                status_code=400,
                detail="El estado es obligatorio"
            )
        
        estado_clean = estado.strip().lower()
        
        if estado_clean not in ValidationService.ESTADOS_VALIDOS:
            raise HTTPException(
                status_code=400,
                detail=f"Estado inválido. Estados válidos: {', '.join(ValidationService.ESTADOS_VALIDOS)}"
            )
        
        return True
    
    @staticmethod
    def validate_tipo_registro(tipo_registro: str) -> bool:
        """🔍 Validar tipo de registro"""
        
        if not tipo_registro:
            tipo_registro = "principal"  # Valor por defecto
        
        if tipo_registro not in ValidationService.TIPOS_REGISTRO_VALIDOS:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de registro inválido. Tipos válidos: {', '.join(ValidationService.TIPOS_REGISTRO_VALIDOS)}"
            )
        
        return True
    
    @staticmethod
    def validate_fecha_nacimiento(fecha_nacimiento: Optional[str]) -> Optional[date]:
        """🔍 Validar y convertir fecha de nacimiento"""
        
        if not fecha_nacimiento:
            return None
        
        try:
            # Intentar diferentes formatos
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
            
            for fmt in formats:
                try:
                    fecha_obj = datetime.strptime(fecha_nacimiento, fmt).date()
                    
                    # Validar que la fecha no sea futura
                    if fecha_obj > date.today():
                        raise HTTPException(
                            status_code=400,
                            detail="La fecha de nacimiento no puede ser futura"
                        )
                    
                    # Validar que la fecha no sea muy antigua (100 años)
                    if fecha_obj < date(1920, 1, 1):
                        raise HTTPException(
                            status_code=400,
                            detail="La fecha de nacimiento es muy antigua"
                        )
                    
                    return fecha_obj
                except ValueError:
                    continue
            
            raise ValueError("Formato de fecha inválido")
            
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Formato de fecha inválido. Use: YYYY-MM-DD, DD/MM/YYYY o DD-MM-YYYY"
            )
    
    @staticmethod
    def validate_photo_file(file: UploadFile) -> bool:
        """📸 Validar archivo de foto"""
        
        if not file:
            return True  # Foto es opcional
        
        # Validar nombre de archivo
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="El archivo debe tener un nombre válido"
            )
        
        # Validar extensión
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        file_extension = file.filename.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Formato de archivo no permitido. Use: {', '.join(allowed_extensions)}"
            )
        
        # Validar tamaño (será validado más a fondo en CloudinaryService)
        max_size = 5 * 1024 * 1024  # 5MB
        if hasattr(file, 'size') and file.size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"El archivo es muy grande. Máximo: {max_size // (1024*1024)}MB"
            )
        
        return True
    
    @staticmethod
    def validate_parent_data(parent_data: Dict[str, Any], parent_type: str = "padre") -> Dict[str, Any]:
        """👨‍👩‍👧‍👦 Validar datos de padres para creación automática"""
        
        if not parent_data:
            return {}
        
        validated_data = {}
        
        # Nombre obligatorio para padres
        if 'nombre' in parent_data:
            ValidationService.validate_nombre(parent_data['nombre'])
            validated_data['nombre'] = parent_data['nombre'].strip()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"El nombre del {parent_type} es obligatorio"
            )
        
        # Código obligatorio para padres
        if 'codigo_identificacion' in parent_data:
            ValidationService.validate_codigo_identificacion(parent_data['codigo_identificacion'])
            validated_data['codigo_identificacion'] = parent_data['codigo_identificacion'].strip().upper()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"El código del {parent_type} es obligatorio"
            )
        
        # Campos opcionales
        optional_fields = ['raza_id', 'peso', 'color', 'procedencia', 'notas', 'color_plumaje', 'color_patas']
        
        for field in optional_fields:
            if field in parent_data and parent_data[field] is not None:
                if field == 'peso':
                    ValidationService.validate_peso(parent_data[field])
                validated_data[field] = parent_data[field]
        
        return validated_data
    
    @staticmethod
    def validate_genealogy_data(
        gallo_data: Dict[str, Any],
        padre_data: Optional[Dict[str, Any]] = None,
        madre_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """🧬 Validar datos completos para creación genealógica"""
        
        validated = {
            'gallo_data': {},
            'padre_data': None,
            'madre_data': None
        }
        
        # 1. Validar datos del gallo principal
        if 'nombre' in gallo_data:
            ValidationService.validate_nombre(gallo_data['nombre'])
            validated['gallo_data']['nombre'] = gallo_data['nombre'].strip()
        
        if 'codigo_identificacion' in gallo_data:
            ValidationService.validate_codigo_identificacion(gallo_data['codigo_identificacion'])
            validated['gallo_data']['codigo_identificacion'] = gallo_data['codigo_identificacion'].strip().upper()
        
        if 'peso' in gallo_data:
            ValidationService.validate_peso(gallo_data['peso'])
            validated['gallo_data']['peso'] = gallo_data['peso']
        
        if 'altura' in gallo_data:
            ValidationService.validate_altura(gallo_data['altura'])
            validated['gallo_data']['altura'] = gallo_data['altura']
        
        if 'estado' in gallo_data:
            ValidationService.validate_estado(gallo_data['estado'])
            validated['gallo_data']['estado'] = gallo_data['estado'].strip().lower()
        
        if 'fecha_nacimiento' in gallo_data:
            fecha_validada = ValidationService.validate_fecha_nacimiento(gallo_data['fecha_nacimiento'])
            if fecha_validada:
                validated['gallo_data']['fecha_nacimiento'] = fecha_validada
        
        # Copiar otros campos válidos
        other_fields = ['raza_id', 'color', 'procedencia', 'notas', 'color_plumaje', 'color_patas', 
                       'criador', 'propietario_actual', 'observaciones', 'numero_registro',
                       'color_placa', 'ubicacion_placa', 'user_id']
        
        for field in other_fields:
            if field in gallo_data and gallo_data[field] is not None:
                validated['gallo_data'][field] = gallo_data[field]
        
        # 2. Validar datos del padre
        if padre_data:
            validated['padre_data'] = ValidationService.validate_parent_data(padre_data, "padre")
        
        # 3. Validar datos de la madre
        if madre_data:
            validated['madre_data'] = ValidationService.validate_parent_data(madre_data, "madre")
        
        return validated
    
    @staticmethod
    def validate_update_data(update_data: Dict[str, Any]) -> Dict[str, Any]:
        """✏️ Validar datos para actualización de gallo"""
        
        validated = {}
        
        # Validar cada campo individualmente
        if 'nombre' in update_data:
            ValidationService.validate_nombre(update_data['nombre'])
            validated['nombre'] = update_data['nombre'].strip()
        
        if 'peso' in update_data:
            ValidationService.validate_peso(update_data['peso'])
            validated['peso'] = update_data['peso']
        
        if 'altura' in update_data:
            ValidationService.validate_altura(update_data['altura'])
            validated['altura'] = update_data['altura']
        
        if 'estado' in update_data:
            ValidationService.validate_estado(update_data['estado'])
            validated['estado'] = update_data['estado'].strip().lower()
        
        if 'fecha_nacimiento' in update_data:
            fecha_validada = ValidationService.validate_fecha_nacimiento(update_data['fecha_nacimiento'])
            if fecha_validada:
                validated['fecha_nacimiento'] = fecha_validada
        
        # Copiar otros campos válidos sin validación especial
        simple_fields = ['color', 'procedencia', 'notas', 'color_plumaje', 'color_patas', 
                        'criador', 'propietario_actual', 'observaciones', 'numero_registro',
                        'color_placa', 'ubicacion_placa', 'raza_id']
        
        for field in simple_fields:
            if field in update_data and update_data[field] is not None:
                validated[field] = update_data[field]
        
        return validated
    
    @staticmethod
    def validate_search_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """🔍 Validar parámetros de búsqueda"""
        
        validated = {}
        
        # Parámetros de paginación
        if 'page' in params:
            try:
                page = int(params['page'])
                if page < 1:
                    raise ValueError()
                validated['page'] = page
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=400,
                    detail="El parámetro 'page' debe ser un número entero positivo"
                )
        
        if 'limit' in params:
            try:
                limit = int(params['limit'])
                if limit < 1 or limit > 100:
                    raise ValueError()
                validated['limit'] = limit
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=400,
                    detail="El parámetro 'limit' debe ser un número entre 1 y 100"
                )
        
        # Parámetros de filtro
        if 'search' in params and params['search']:
            search_term = params['search'].strip()
            if len(search_term) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="El término de búsqueda debe tener al menos 2 caracteres"
                )
            validated['search'] = search_term
        
        # Otros parámetros válidos
        simple_params = ['raza_id', 'estado', 'tiene_foto', 'tiene_padres', 
                        'created_after', 'sort_by', 'sort_order']
        
        for param in simple_params:
            if param in params and params[param] is not None:
                validated[param] = params[param]
        
        return validated
    
    @staticmethod
    def get_validation_summary() -> Dict[str, Any]:
        """📊 Obtener resumen de reglas de validación"""
        
        return {
            'codigo_identificacion': {
                'pattern': ValidationService.CODIGO_PATTERN,
                'descripcion': 'Solo letras mayúsculas y números, 3-20 caracteres',
                'obligatorio': True,
                'unico': True
            },
            'nombre': {
                'min_length': ValidationService.NOMBRE_MIN_LENGTH,
                'max_length': ValidationService.NOMBRE_MAX_LENGTH,
                'obligatorio': True,
                'caracteres_prohibidos': ['<', '>', '"', "'", '&', '|', ';']
            },
            'peso': {
                'min': ValidationService.PESO_MIN,
                'max': ValidationService.PESO_MAX,
                'unidad': 'kg',
                'obligatorio': False
            },
            'altura': {
                'min': ValidationService.ALTURA_MIN,
                'max': ValidationService.ALTURA_MAX,
                'unidad': 'cm',
                'obligatorio': False
            },
            'estado': {
                'valores_validos': ValidationService.ESTADOS_VALIDOS,
                'obligatorio': True,
                'default': 'activo'
            },
            'tipo_registro': {
                'valores_validos': ValidationService.TIPOS_REGISTRO_VALIDOS,
                'obligatorio': False,
                'default': 'principal'
            },
            'fecha_nacimiento': {
                'formatos_validos': ['YYYY-MM-DD', 'DD/MM/YYYY', 'DD-MM-YYYY'],
                'no_futura': True,
                'min_year': 1920,
                'obligatorio': False
            },
            'foto': {
                'formatos_validos': ['.jpg', '.jpeg', '.png', '.webp'],
                'tamaño_max': '5MB',
                'obligatorio': False
            }
        }
