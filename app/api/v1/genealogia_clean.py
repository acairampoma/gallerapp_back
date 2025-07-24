# 🌳 app/api/v1/genealogia_clean.py - ÁRBOL GENEALÓGICO ÉPICO
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.gallo import Gallo

router = APIRouter()

# ========================================
# 🌳 ÁRBOL GENEALÓGICO (2 ENDPOINTS ÉPICOS)
# ========================================

def build_ancestor_tree(db: Session, gallo_id: int, depth: int = 3, current_depth: int = 0) -> Optional[Dict[str, Any]]:
    """🌳 Construir árbol de ancestros recursivamente"""
    
    if current_depth >= depth:
        return None
    
    # Obtener gallo actual
    gallo = db.query(Gallo).filter(Gallo.id == gallo_id).first()
    if not gallo:
        return None
    
    # Datos básicos del gallo
    gallo_data = {
        "id": gallo.id,
        "nombre": gallo.nombre,
        "codigo_identificacion": gallo.codigo_identificacion,
        "foto_principal_url": gallo.foto_principal_url,
        "fecha_nacimiento": gallo.fecha_nacimiento.isoformat() if gallo.fecha_nacimiento else None,
        "raza_nombre": gallo.raza.nombre if gallo.raza else None,
        "generacion": current_depth
    }
    
    # Construir recursivamente padres
    padre = None
    madre = None
    
    if gallo.padre_id:
        padre = build_ancestor_tree(db, gallo.padre_id, depth, current_depth + 1)
    
    if gallo.madre_id:
        madre = build_ancestor_tree(db, gallo.madre_id, depth, current_depth + 1)
    
    # Solo agregar padres si existen
    if padre or madre:
        gallo_data["padres"] = {}
        if padre:
            gallo_data["padres"]["padre"] = padre
        if madre:
            gallo_data["padres"]["madre"] = madre
    
    return gallo_data

def get_descendants(db: Session, gallo_id: int, user_id: int, depth: int = 3) -> List[Dict[str, Any]]:
    """👶 Obtener descendientes del gallo"""
    
    descendants = []
    
    def _get_descendants_recursive(parent_id: int, current_depth: int = 0):
        if current_depth >= depth:
            return
        
        # Buscar hijos directos
        hijos = db.query(Gallo).filter(
            ((Gallo.padre_id == parent_id) | (Gallo.madre_id == parent_id)),
            Gallo.user_id == user_id
        ).all()
        
        for hijo in hijos:
            hijo_data = {
                "id": hijo.id,
                "nombre": hijo.nombre,
                "codigo_identificacion": hijo.codigo_identificacion,
                "foto_principal_url": hijo.foto_principal_url,
                "fecha_nacimiento": hijo.fecha_nacimiento.isoformat() if hijo.fecha_nacimiento else None,
                "raza_nombre": hijo.raza.nombre if hijo.raza else None,
                "generacion": current_depth + 1,
                "relacion": "hijo" if hijo.padre_id == parent_id else "hija" if hijo.madre_id == parent_id else "descendiente"
            }
            descendants.append(hijo_data)
            
            # Recursión para nietos, bisnietos, etc.
            _get_descendants_recursive(hijo.id, current_depth + 1)
    
    _get_descendants_recursive(gallo_id)
    return descendants

@router.get("/{gallo_id}/genealogia", response_model=dict)
async def get_arbol_genealogico(
    gallo_id: int,
    depth: int = Query(3, ge=1, le=5, description="Profundidad del árbol (generaciones)"),
    include_descendants: bool = Query(True, description="Incluir descendientes"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """🌳 Obtener árbol genealógico completo"""
    
    try:
        # Verificar que el gallo existe y pertenece al usuario
        gallo_base = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo_base:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Construir árbol de ancestros
        arbol_ancestros = build_ancestor_tree(db, gallo_id, depth)
        
        # Obtener descendientes si se solicita
        descendientes = []
        if include_descendants:
            descendientes = get_descendants(db, gallo_id, current_user_id, depth)
        
        # Calcular estadísticas
        def count_nodes(tree):
            if not tree:
                return 0
            count = 1
            if "padres" in tree:
                if "padre" in tree["padres"]:
                    count += count_nodes(tree["padres"]["padre"])
                if "madre" in tree["padres"]:
                    count += count_nodes(tree["padres"]["madre"])
            return count
        
        total_ancestros = count_nodes(arbol_ancestros) - 1  # No contar el gallo base
        total_descendientes = len(descendientes)
        
        # Calcular generaciones
        def max_generation(tree):
            if not tree or "padres" not in tree:
                return tree["generacion"] if tree else 0
            
            max_padre = 0
            max_madre = 0
            
            if "padre" in tree["padres"]:
                max_padre = max_generation(tree["padres"]["padre"])
            if "madre" in tree["padres"]:
                max_madre = max_generation(tree["padres"]["madre"])
            
            return max(max_padre, max_madre)
        
        generaciones_hacia_arriba = max_generation(arbol_ancestros)
        generaciones_hacia_abajo = max([d["generacion"] for d in descendientes]) if descendientes else 0
        
        return {
            "success": True,
            "data": {
                "gallo_base": {
                    "id": gallo_base.id,
                    "nombre": gallo_base.nombre,
                    "codigo_identificacion": gallo_base.codigo_identificacion,
                    "foto_principal_url": gallo_base.foto_principal_url,
                    "raza_nombre": gallo_base.raza.nombre if gallo_base.raza else None
                },
                "arbol_genealogico": {
                    "ancestros": arbol_ancestros,
                    "descendientes": descendientes,
                    "estadisticas": {
                        "total_ancestros": total_ancestros,
                        "total_descendientes": total_descendientes,
                        "generaciones_hacia_arriba": generaciones_hacia_arriba,
                        "generaciones_hacia_abajo": generaciones_hacia_abajo,
                        "total_familiares": total_ancestros + total_descendientes
                    }
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error construyendo árbol genealógico: {str(e)}"
        )

@router.get("/{gallo_id}/descendants", response_model=dict)
async def get_descendants_only(
    gallo_id: int,
    depth: int = Query(3, ge=1, le=5, description="Profundidad de descendientes"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """👶 Obtener solo descendientes del gallo"""
    
    try:
        # Verificar que el gallo existe y pertenece al usuario
        gallo_base = db.query(Gallo).filter(
            Gallo.id == gallo_id,
            Gallo.user_id == current_user_id
        ).first()
        
        if not gallo_base:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallo no encontrado"
            )
        
        # Obtener descendientes
        descendientes = get_descendants(db, gallo_id, current_user_id, depth)
        
        # Organizar por generaciones
        descendientes_por_generacion = {}
        for desc in descendientes:
            gen = desc["generacion"]
            if gen not in descendientes_por_generacion:
                descendientes_por_generacion[gen] = []
            descendientes_por_generacion[gen].append(desc)
        
        return {
            "success": True,
            "data": {
                "gallo_base": {
                    "id": gallo_base.id,
                    "nombre": gallo_base.nombre,
                    "codigo_identificacion": gallo_base.codigo_identificacion
                },
                "descendientes": {
                    "lista_completa": descendientes,
                    "por_generacion": descendientes_por_generacion,
                    "estadisticas": {
                        "total_descendientes": len(descendientes),
                        "generaciones": len(descendientes_por_generacion),
                        "hijos_directos": len(descendientes_por_generacion.get(1, [])),
                        "nietos": len(descendientes_por_generacion.get(2, [])),
                        "bisnietos": len(descendientes_por_generacion.get(3, []))
                    }
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo descendientes: {str(e)}"
        )
