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
        # Usar timestamp + UUID para garantizar unicidad
        timestamp = int(datetime.now().timestamp())
        unique_suffix = str(uuid.uuid4().int)[:6]  # 6 dígitos del UUID
        return int(f"{timestamp}{unique_suffix}")
    
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
            # 1. 🎯 GENERAR ID GENEALÓGICO ÚNICO
            genealogy_id = GenealogyService.generate_genealogy_id()
            print(f"🧬 Generando familia genealógica ID: {genealogy_id}")
            
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
                
                # Crear registro del padre
                padre_creado = Gallo(
                    **padre_data,
                    id_gallo_genealogico=genealogy_id,
                    tipo_registro=\"padre_generado\",
                    estado=\"padre\",
                    codigo_identificacion=padre_data['codigo_identificacion'].upper()
                )
                
                db.add(padre_creado)
                db.flush()  # Para obtener el ID
                padre_final_id = padre_creado.id
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
                
                # Crear registro de la madre
                madre_creada = Gallo(
                    **madre_data,
                    id_gallo_genealogico=genealogy_id,
                    tipo_registro=\"madre_generada\",
                    estado=\"madre\",
                    codigo_identificacion=madre_data['codigo_identificacion'].upper()
                )
                
                db.add(madre_creada)
                db.flush()  # Para obtener el ID
                madre_final_id = madre_creada.id
                print(f"✅ Madre creada con ID: {madre_final_id}")
            
            # 5. 🔥 CREAR GALLO PRINCIPAL CON GENEALOGÍA
            print(f"🔨 Creando gallo principal: {gallo_data.get('nombre')}")
            
            # Validar código único del gallo principal
            existing_gallo = db.query(Gallo).filter(
                Gallo.codigo_identificacion == gallo_data['codigo_identificacion'].upper(),
                Gallo.user_id == gallo_data['user_id']
            ).first()
            
            if existing_gallo:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya existe un gallo con código '{gallo_data['codigo_identificacion']}' (Principal)"
                )
            
            # Validar ciclos genealógicos
            GenealogyService.validate_genealogy_cycle(
                db=db,
                gallo_id=None,  # Nuevo gallo
                padre_id=padre_final_id,
                madre_id=madre_final_id
            )
            
            # Crear gallo principal
            gallo_principal = Gallo(
                **gallo_data,
                id_gallo_genealogico=genealogy_id,
                tipo_registro=\"principal\",
                codigo_identificacion=gallo_data['codigo_identificacion'].upper(),
                padre_id=padre_final_id,
                madre_id=madre_final_id
            )
            
            db.add(gallo_principal)
            db.flush()  # Para obtener el ID
            print(f"✅ Gallo principal creado con ID: {gallo_principal.id}")
            
            # 6. 💾 COMMIT TRANSACCIÓN
            db.commit()
            
            # 7. 📊 GENERAR RESPUESTA ÉPICA
            total_registros = 1  # Gallo principal
            if padre_creado:
                total_registros += 1
            if madre_creada:
                total_registros += 1
            
            return {
                'success': True,
                'gallo_principal': gallo_principal,
                'padre_creado': padre_creado,
                'madre_creada': madre_creada,
                'total_registros_creados': total_registros,
                'genealogy_id': genealogy_id,
                'padre_final_id': padre_final_id,
                'madre_final_id': madre_final_id
            }
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error en técnica recursiva genealógica: {str(e)}"
            )
    
    @staticmethod
    def get_family_tree(
        db: Session, 
        gallo_id: int, 
        max_depth: int = 5,
        include_descendants: bool = False
    ) -> Dict[str, Any]:
        """🌳 Obtener árbol genealógico completo (ascendentes y descendientes)"""
        
        try:
            # Obtener gallo base
            gallo = db.query(Gallo).filter(Gallo.id == gallo_id).first()
            if not gallo:
                raise HTTPException(status_code=404, detail="Gallo no encontrado")
            
            # 🔼 ASCENDENTES (padres, abuelos, etc.)
            ancestros = gallo.get_ancestros(db, max_depth)
            
            # 🔽 DESCENDIENTES (hijos, nietos, etc.)
            descendientes = []
            if include_descendants:
                descendientes = gallo.get_descendientes(db)
            
            # 👨‍👩‍👧‍👦 FAMILIA COMPLETA (mismo id_gallo_genealogico)
            familia_completa = []
            if gallo.id_gallo_genealogico:
                familia_completa = gallo.get_familia_completa(db)
            
            # 📊 ESTADÍSTICAS
            estadisticas = {
                'total_ancestros': len(ancestros),
                'total_descendientes': len(descendientes),
                'total_familia_completa': len(familia_completa),
                'generaciones_hacia_arriba': max([a['nivel'] for a in ancestros]) if ancestros else 0,
                'generaciones_hacia_abajo': 1 if descendientes else 0,
                'tiene_padre': gallo.padre_id is not None,
                'tiene_madre': gallo.madre_id is not None,
                'genealogy_id': gallo.id_gallo_genealogico
            }
            
            return {
                'success': True,
                'gallo_base': {
                    'id': gallo.id,
                    'nombre': gallo.nombre,
                    'codigo_identificacion': gallo.codigo_identificacion,
                    'genealogy_id': gallo.id_gallo_genealogico
                },
                'ancestros': ancestros,
                'descendientes': descendientes,
                'familia_completa': [
                    {
                        'id': g.id,
                        'nombre': g.nombre,
                        'codigo_identificacion': g.codigo_identificacion,
                        'tipo_registro': g.tipo_registro,
                        'padre_id': g.padre_id,
                        'madre_id': g.madre_id
                    } for g in familia_completa
                ],
                'estadisticas': estadisticas
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error obteniendo árbol genealógico: {str(e)}"
            )
    
    @staticmethod
    def add_parents_to_existing(
        db: Session,
        gallo_id: int,
        padre_data: Optional[Dict[str, Any]] = None,
        madre_data: Optional[Dict[str, Any]] = None,
        padre_existente_id: Optional[int] = None,
        madre_existente_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """🔧 Agregar padres a un gallo existente (expandir genealogía)"""
        
        try:
            # Obtener gallo existente
            gallo = db.query(Gallo).filter(Gallo.id == gallo_id).first()
            if not gallo:
                raise HTTPException(status_code=404, detail="Gallo no encontrado")
            
            # Verificar si ya tiene padres
            if gallo.padre_id and padre_data:
                raise HTTPException(
                    status_code=400,
                    detail="El gallo ya tiene padre asignado. Use update para modificar."
                )
            
            if gallo.madre_id and madre_data:
                raise HTTPException(
                    status_code=400,
                    detail="El gallo ya tiene madre asignada. Use update para modificar."
                )
            
            # Usar mismo genealogy_id o crear uno nuevo
            genealogy_id = gallo.id_gallo_genealogico
            if not genealogy_id:
                genealogy_id = GenealogyService.generate_genealogy_id()
                gallo.id_gallo_genealogico = genealogy_id
            
            padre_creado = None
            madre_creada = None
            
            # Crear/asignar padre
            if padre_data and not padre_existente_id:
                # Validar código único
                existing = db.query(Gallo).filter(
                    Gallo.codigo_identificacion == padre_data['codigo_identificacion'].upper(),
                    Gallo.user_id == gallo.user_id
                ).first()
                
                if existing:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Ya existe un gallo con código '{padre_data['codigo_identificacion']}'"
                    )
                
                padre_creado = Gallo(
                    **padre_data,
                    user_id=gallo.user_id,
                    id_gallo_genealogico=genealogy_id,
                    tipo_registro="padre_generado",
                    estado="padre",
                    codigo_identificacion=padre_data['codigo_identificacion'].upper()
                )
                
                db.add(padre_creado)
                db.flush()
                gallo.padre_id = padre_creado.id
            
            elif padre_existente_id:
                # Validar ciclos
                GenealogyService.validate_genealogy_cycle(db, gallo_id, padre_existente_id, gallo.madre_id)
                gallo.padre_id = padre_existente_id
            
            # Crear/asignar madre
            if madre_data and not madre_existente_id:
                # Validar código único
                existing = db.query(Gallo).filter(
                    Gallo.codigo_identificacion == madre_data['codigo_identificacion'].upper(),
                    Gallo.user_id == gallo.user_id
                ).first()
                
                if existing:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Ya existe un gallo con código '{madre_data['codigo_identificacion']}'"
                    )
                
                madre_creada = Gallo(
                    **madre_data,
                    user_id=gallo.user_id,
                    id_gallo_genealogico=genealogy_id,
                    tipo_registro="madre_generada",
                    estado="madre",
                    codigo_identificacion=madre_data['codigo_identificacion'].upper()
                )
                
                db.add(madre_creada)
                db.flush()
                gallo.madre_id = madre_creada.id
            
            elif madre_existente_id:
                # Validar ciclos
                GenealogyService.validate_genealogy_cycle(db, gallo_id, gallo.padre_id, madre_existente_id)
                gallo.madre_id = madre_existente_id
            
            # Actualizar timestamp
            gallo.updated_at = func.current_timestamp()
            
            db.commit()
            
            return {
                'success': True,
                'gallo_actualizado': gallo,
                'padre_creado': padre_creado,
                'madre_creada': madre_creada,
                'genealogy_id': genealogy_id,
                'cambios_realizados': [
                    f"Padre {'creado' if padre_creado else 'asignado'}" if (padre_creado or padre_existente_id) else None,
                    f"Madre {'creada' if madre_creada else 'asignada'}" if (madre_creada or madre_existente_id) else None
                ]
            }
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error agregando padres: {str(e)}"
            )
    
    @staticmethod
    def search_by_genealogy(
        db: Session,
        genealogy_id: Optional[int] = None,
        ancestro_id: Optional[int] = None,
        descendiente_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """🔍 Búsqueda genealógica avanzada"""
        
        try:
            results = []
            
            if genealogy_id:
                # Buscar por familia completa
                gallos = db.query(Gallo).filter(
                    Gallo.id_gallo_genealogico == genealogy_id
                ).all()
                
                if user_id:
                    gallos = [g for g in gallos if g.user_id == user_id]
                
                results = gallos
            
            elif ancestro_id:
                # Buscar descendientes de un ancestro
                ancestro = db.query(Gallo).filter(Gallo.id == ancestro_id).first()
                if not ancestro:
                    raise HTTPException(status_code=404, detail="Ancestro no encontrado")
                
                # Búsqueda recursiva de descendientes
                def get_all_descendants(gallo_id: int, visited: set = None) -> List[Gallo]:
                    if visited is None:
                        visited = set()
                    
                    if gallo_id in visited:
                        return []
                    
                    visited.add(gallo_id)
                    descendants = []
                    
                    # Hijos directos
                    hijos = db.query(Gallo).filter(
                        (Gallo.padre_id == gallo_id) | (Gallo.madre_id == gallo_id)
                    ).all()
                    
                    for hijo in hijos:
                        descendants.append(hijo)
                        # Recursivo para nietos, bisnietos, etc.
                        descendants.extend(get_all_descendants(hijo.id, visited))
                    
                    return descendants
                
                results = get_all_descendants(ancestro_id)
                
                if user_id:
                    results = [g for g in results if g.user_id == user_id]
            
            elif descendiente_id:
                # Buscar ancestros de un descendiente
                descendiente = db.query(Gallo).filter(Gallo.id == descendiente_id).first()
                if not descendiente:
                    raise HTTPException(status_code=404, detail="Descendiente no encontrado")
                
                ancestros_data = descendiente.get_ancestros(db, max_depth=10)
                results = [a['gallo'] for a in ancestros_data]
                
                if user_id:
                    results = [g for g in results if g.user_id == user_id]
            
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
                },
                'user_id': user_id
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error obteniendo estadísticas: {str(e)}"
            )
