# 🧬 app/services/genealogy_service.py - Servicio ÉPICO de Genealogía Recursiva
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from fastapi import HTTPException
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import uuid

from app.models.gallo_simple import Gallo
from app.services.cloudinary_service import CloudinaryService

class GenealogyService:
    """🔥 Servicio épico para la técnica recursiva genealógica de Alan"""
    
    @staticmethod
    def generate_genealogy_id() -> int:
        """🎯 Generar nuevo ID genealógico único"""
        # Usar timestamp simplificado para PostgreSQL INT
        import time
        timestamp = int(time.time())  # Timestamp actual en segundos
        # Agregar número aleatorio pequeño para unicidad
        import random
        unique_suffix = random.randint(100, 999)
        genealogy_id = int(f"{timestamp}{unique_suffix}")
        
        # Asegurar que esté dentro del rango de PostgreSQL INTEGER (2^31 - 1)
        max_int = 2147483647
        if genealogy_id > max_int:
            # Si es muy grande, usar solo timestamp + suffix corto
            genealogy_id = timestamp + unique_suffix
        
        return genealogy_id
    
    @staticmethod
    def validate_genealogy_cycle(
        db: Session, 
        gallo_id: Optional[int], 
        padre_id: Optional[int], 
        madre_id: Optional[int]
    ) -> bool:
        """🔍 Validar que no se creen ciclos genealógicos"""
        
        if not gallo_id:
            return True  # Nuevo gallo, no hay ciclos posibles
        
        def check_ancestor(ancestor_id: int, target_id: int, max_depth: int = 10) -> bool:
            """Verificar si ancestor_id es descendiente de target_id"""
            if ancestor_id == target_id:
                return True
            
            if max_depth <= 0:
                return False
            
            ancestor = db.query(Gallo).filter(Gallo.id == ancestor_id).first()
            if not ancestor:
                return False
            
            # Verificar padres recursivamente
            if ancestor.padre_id and check_ancestor(ancestor.padre_id, target_id, max_depth - 1):
                return True
            if ancestor.madre_id and check_ancestor(ancestor.madre_id, target_id, max_depth - 1):
                return True
            
            return False
        
        # Verificar ciclos con padre
        if padre_id and check_ancestor(gallo_id, padre_id):
            raise HTTPException(
                status_code=400,
                detail=f"Ciclo genealógico detectado: El padre especificado es descendiente del gallo"
            )
        
        # Verificar ciclos con madre
        if madre_id and check_ancestor(gallo_id, madre_id):
            raise HTTPException(
                status_code=400,
                detail=f"Ciclo genealógico detectado: La madre especificada es descendiente del gallo"
            )
        
        return True
    
    @staticmethod
    def create_with_parents(
        db: Session,
        gallo_data: Dict[str, Any],
        padre_data: Optional[Dict[str, Any]] = None,
        madre_data: Optional[Dict[str, Any]] = None,
        padre_existente_id: Optional[int] = None,
        madre_existente_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """🔥 TÉCNICA RECURSIVA ÉPICA: Crear gallo con padres automáticamente"""
        
        try:
            # 1. 🎯 CREAR GALLO PRINCIPAL PRIMERO
            print(f"🧬 Creando gallo principal: {gallo_data.get('nombre')}")
            
            # Validar código único del gallo principal
            existing_gallo = db.query(Gallo).filter(
                Gallo.codigo_identificacion == gallo_data['codigo_identificacion'].upper(),
                Gallo.user_id == gallo_data['user_id']
            ).first()
            
            if existing_gallo:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya existe un gallo con código '{gallo_data['codigo_identificacion']}'"
                )
            
            # Preparar datos del gallo principal
            gallo_data_clean = gallo_data.copy()
            gallo_codigo_upper = gallo_data_clean['codigo_identificacion'].upper()
            gallo_data_clean['codigo_identificacion'] = gallo_codigo_upper
            
            # Crear gallo principal SIN genealogy_id todavía
            gallo_principal = Gallo(
                **gallo_data_clean,
                tipo_registro="principal",
                id_gallo_genealogico=0  # Temporal, se actualizará después
            )
            
            db.add(gallo_principal)
            db.flush()  # Para obtener el ID
            
            # 2. 🎯 USAR EL ID DEL GALLO COMO GENEALOGY_ID
            genealogy_id = gallo_principal.id
            gallo_principal.id_gallo_genealogico = genealogy_id
            
            print(f"✅ Gallo principal creado con ID: {gallo_principal.id}")
            print(f"🔥 Usando ID {genealogy_id} como genealogy_id para toda la familia")
            
            padre_creado = None
            madre_creada = None
            padre_final_id = padre_existente_id
            madre_final_id = madre_existente_id
            
            # 2. 🔍 VALIDAR PADRES EXISTENTES
            if padre_existente_id:
                padre_existente = db.query(Gallo).filter(Gallo.id == padre_existente_id).first()
                if not padre_existente:
                    raise HTTPException(status_code=404, detail=f"Padre con ID {padre_existente_id} no encontrado")
                print(f"👨 Usando padre existente: {padre_existente.nombre}")
            
            if madre_existente_id:
                madre_existente = db.query(Gallo).filter(Gallo.id == madre_existente_id).first()
                if not madre_existente:
                    raise HTTPException(status_code=404, detail=f"Madre con ID {madre_existente_id} no encontrado")
                print(f"👩 Usando madre existente: {madre_existente.nombre}")
            
            # 3. 🔥 CREAR PADRE SI SE ESPECIFICA
            if padre_data and not padre_existente_id:
                print(f"🔨 Creando padre: {padre_data.get('nombre')}")
                
                # Validar código único del padre
                existing_padre = db.query(Gallo).filter(
                    Gallo.codigo_identificacion == padre_data['codigo_identificacion'].upper(),
                    Gallo.user_id == gallo_data['user_id']
                ).first()
                
                if existing_padre:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Ya existe un gallo con código '{padre_data['codigo_identificacion']}' (Padre)"
                    )
                
                # Preparar datos del padre sin duplicar codigo_identificacion
                padre_data_clean = padre_data.copy()
                padre_codigo_upper = padre_data_clean['codigo_identificacion'].upper()
                padre_data_clean['codigo_identificacion'] = padre_codigo_upper
                
                # Crear registro del padre
                padre_creado = Gallo(
                    **padre_data_clean,
                    id_gallo_genealogico=genealogy_id,
                    tipo_registro="padre_generado",
                    estado="padre"
                )
                
                db.add(padre_creado)
                db.flush()  # Para obtener el ID
                padre_final_id = padre_creado.id
                
                # Actualizar el gallo principal con el padre
                gallo_principal.padre_id = padre_final_id
                
                print(f"✅ Padre creado con ID: {padre_final_id}")
            
            # 4. 🔥 CREAR MADRE SI SE ESPECIFICA
            if madre_data and not madre_existente_id:
                print(f"🔨 Creando madre: {madre_data.get('nombre')}")
                
                # Validar código único de la madre
                existing_madre = db.query(Gallo).filter(
                    Gallo.codigo_identificacion == madre_data['codigo_identificacion'].upper(),
                    Gallo.user_id == gallo_data['user_id']
                ).first()
                
                if existing_madre:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Ya existe un gallo con código '{madre_data['codigo_identificacion']}' (Madre)"
                    )
                
                # Preparar datos de la madre sin duplicar codigo_identificacion
                madre_data_clean = madre_data.copy()
                madre_codigo_upper = madre_data_clean['codigo_identificacion'].upper()
                madre_data_clean['codigo_identificacion'] = madre_codigo_upper
                
                # Crear registro de la madre
                madre_creada = Gallo(
                    **madre_data_clean,
                    id_gallo_genealogico=genealogy_id,
                    tipo_registro="madre_generada",
                    estado="madre"
                )
                
                db.add(madre_creada)
                db.flush()  # Para obtener el ID
                madre_final_id = madre_creada.id
                
                # Actualizar el gallo principal con la madre
                gallo_principal.madre_id = madre_final_id
                
                print(f"✅ Madre creada con ID: {madre_final_id}")
            
            # 5. 🎯 ACTUALIZAR REFERENCIAS DE PADRES EXISTENTES
            if padre_existente_id:
                gallo_principal.padre_id = padre_existente_id
            if madre_existente_id:
                gallo_principal.madre_id = madre_existente_id
            
            # 6. 🎯 COMMIT FINAL
            db.commit()
            
            # 7. 📊 CONTAR REGISTROS CREADOS
            total_registros = 1  # Gallo principal
            if padre_creado:
                total_registros += 1
            if madre_creada:
                total_registros += 1
            
            print(f"🏆 Técnica genealógica completada: {total_registros} registros con genealogy_id {genealogy_id}")
            
            return {
                'success': True,
                'gallo_principal': gallo_principal,
                'padre_creado': padre_creado,
                'madre_creada': madre_creada,
                'genealogy_id': genealogy_id,
                'total_registros_creados': total_registros,
                'mensaje_epico': f"🔥 Familia {gallo_principal.nombre} creada con {total_registros} registros"
            }
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error en técnica genealógica: {str(e)}"
            )
    
    @staticmethod
    def get_family_tree(
        db: Session,
        gallo_id: int,
        max_depth: int = 5,
        include_descendants: bool = False
    ) -> Dict[str, Any]:
        """🌳 Obtener árbol genealógico completo"""
        
        try:
            # Obtener gallo base
            gallo_base = db.query(Gallo).filter(Gallo.id == gallo_id).first()
            if not gallo_base:
                raise HTTPException(status_code=404, detail="Gallo no encontrado")
            
            def build_tree_recursive(gallo: Gallo, depth: int) -> Dict[str, Any]:
                """Construir árbol recursivamente"""
                if depth <= 0:
                    return None
                
                tree_node = {
                    'id': gallo.id,
                    'nombre': gallo.nombre,
                    'codigo_identificacion': gallo.codigo_identificacion,
                    'tipo_registro': gallo.tipo_registro,
                    'genealogy_id': gallo.id_gallo_genealogico,
                    'foto_principal_url': gallo.foto_principal_url,
                    'url_foto_cloudinary': gallo.url_foto_cloudinary,
                    'padre': None,
                    'madre': None
                }
                
                # Agregar padre recursivamente
                if gallo.padre_id:
                    padre = db.query(Gallo).filter(Gallo.id == gallo.padre_id).first()
                    if padre:
                        tree_node['padre'] = build_tree_recursive(padre, depth - 1)
                
                # Agregar madre recursivamente
                if gallo.madre_id:
                    madre = db.query(Gallo).filter(Gallo.id == gallo.madre_id).first()
                    if madre:
                        tree_node['madre'] = build_tree_recursive(madre, depth - 1)
                
                return tree_node
            
            # Construir árbol genealógico
            family_tree = build_tree_recursive(gallo_base, max_depth)
            
            # Estadísticas del árbol
            total_ancestros = 0
            generaciones = 0
            
            def count_ancestors(node, generation=0):
                nonlocal total_ancestros, generaciones
                if not node:
                    return
                
                generaciones = max(generaciones, generation)
                if generation > 0:  # No contar el gallo base
                    total_ancestros += 1
                
                count_ancestors(node.get('padre'), generation + 1)
                count_ancestors(node.get('madre'), generation + 1)
            
            count_ancestors(family_tree)
            
            return {
                'success': True,
                'gallo_base': {
                    'id': gallo_base.id,
                    'nombre': gallo_base.nombre,
                    'codigo_identificacion': gallo_base.codigo_identificacion
                },
                'arbol_genealogico': family_tree,
                'estadisticas': {
                    'total_ancestros': total_ancestros,
                    'generaciones_disponibles': generaciones,
                    'max_depth_used': max_depth,
                    'genealogy_id': gallo_base.id_gallo_genealogico
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error obteniendo árbol genealógico: {str(e)}"
            )
    
    @staticmethod
    def search_by_genealogy(
        db: Session,
        genealogy_id: Optional[int] = None,
        ancestro_id: Optional[int] = None,
        descendiente_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """🔍 Búsqueda avanzada por genealogía"""
        
        try:
            results = []
            
            if genealogy_id:
                # Buscar toda la familia
                query = db.query(Gallo).filter(Gallo.id_gallo_genealogico == genealogy_id)
                if user_id:
                    query = query.filter(Gallo.user_id == user_id)
                results = query.all()
            
            elif ancestro_id:
                # Buscar descendientes de un ancestro
                ancestro = db.query(Gallo).filter(Gallo.id == ancestro_id).first()
                if not ancestro:
                    raise HTTPException(status_code=404, detail="Ancestro no encontrado")
                
                # Buscar gallos que tengan este ancestro como padre o madre
                query = db.query(Gallo).filter(
                    (Gallo.padre_id == ancestro_id) | (Gallo.madre_id == ancestro_id)
                )
                if user_id:
                    query = query.filter(Gallo.user_id == user_id)
                results = query.all()
            
            elif descendiente_id:
                # Buscar ancestros de un descendiente
                descendiente = db.query(Gallo).filter(Gallo.id == descendiente_id).first()
                if not descendiente:
                    raise HTTPException(status_code=404, detail="Descendiente no encontrado")
                
                # Recopilar ancestros recursivamente
                ancestros_ids = set()
                
                def get_ancestors(gallo_id, depth=10):
                    if depth <= 0:
                        return
                    
                    gallo = db.query(Gallo).filter(Gallo.id == gallo_id).first()
                    if not gallo:
                        return
                    
                    if gallo.padre_id:
                        ancestros_ids.add(gallo.padre_id)
                        get_ancestors(gallo.padre_id, depth - 1)
                    
                    if gallo.madre_id:
                        ancestros_ids.add(gallo.madre_id)
                        get_ancestors(gallo.madre_id, depth - 1)
                
                get_ancestors(descendiente_id)
                
                if ancestros_ids:
                    query = db.query(Gallo).filter(Gallo.id.in_(ancestros_ids))
                    if user_id:
                        query = query.filter(Gallo.user_id == user_id)
                    results = query.all()
            
            return {
                'success': True,
                'total_encontrados': len(results),
                'gallos': [
                    {
                        'id': g.id,
                        'nombre': g.nombre,
                        'codigo_identificacion': g.codigo_identificacion,
                        'tipo_registro': g.tipo_registro,
                        'genealogy_id': g.id_gallo_genealogico,
                        'padre_id': g.padre_id,
                        'madre_id': g.madre_id,
                        'url_foto_cloudinary': g.url_foto_cloudinary
                    } for g in results
                ],
                'busqueda_params': {
                    'genealogy_id': genealogy_id,
                    'ancestro_id': ancestro_id,
                    'descendiente_id': descendiente_id,
                    'user_id': user_id
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error en búsqueda genealógica: {str(e)}"
            )
    
    @staticmethod
    def get_genealogy_stats(db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
        """📊 Estadísticas genealógicas del sistema"""
        
        try:
            query_base = db.query(Gallo)
            if user_id:
                query_base = query_base.filter(Gallo.user_id == user_id)
            
            # Estadísticas básicas
            total_gallos = query_base.count()
            gallos_con_padre = query_base.filter(Gallo.padre_id.isnot(None)).count()
            gallos_con_madre = query_base.filter(Gallo.madre_id.isnot(None)).count()
            gallos_principales = query_base.filter(Gallo.tipo_registro == "principal").count()
            gallos_padres_generados = query_base.filter(Gallo.tipo_registro == "padre_generado").count()
            gallos_madres_generadas = query_base.filter(Gallo.tipo_registro == "madre_generada").count()
            
            # Familias genealógicas
            familias_query = query_base.filter(Gallo.id_gallo_genealogico.isnot(None))
            familias_unicas = db.query(Gallo.id_gallo_genealogico).filter(
                Gallo.id_gallo_genealogico.isnot(None)
            ).distinct().count()
            
            if user_id:
                familias_unicas = db.query(Gallo.id_gallo_genealogico).filter(
                    Gallo.id_gallo_genealogico.isnot(None),
                    Gallo.user_id == user_id
                ).distinct().count()
            
            return {
                'success': True,
                'data': {
                    'estadisticas_generales': {
                        'total_gallos': total_gallos,
                        'gallos_con_padre': gallos_con_padre,
                        'gallos_con_madre': gallos_con_madre,
                        'gallos_con_ambos_padres': query_base.filter(
                            Gallo.padre_id.isnot(None),
                            Gallo.madre_id.isnot(None)
                        ).count(),
                        'gallos_huerfanos': query_base.filter(
                            Gallo.padre_id.is_(None),
                            Gallo.madre_id.is_(None)
                        ).count()
                    },
                    'distribucion_tipos': {
                        'principales': gallos_principales,
                        'padres_generados': gallos_padres_generados,
                        'madres_generadas': gallos_madres_generadas
                    },
                    'familias_genealogicas': {
                        'total_familias': familias_unicas,
                        'promedio_gallos_por_familia': total_gallos / familias_unicas if familias_unicas > 0 else 0
                    }
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error obteniendo estadísticas: {str(e)}"
            )
