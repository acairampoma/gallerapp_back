# 💼 Servicio de Inversiones
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime

from app.models.inversion import Inversion
from app.schemas.inversion import InversionCreate, InversionUpdate

class InversionService:
    
    @staticmethod
    def obtener_inversiones(
        db: Session, 
        user_id: int,
        año: Optional[int] = None,
        mes: Optional[int] = None,
        tipo_gasto: Optional[str] = None
    ) -> List[Inversion]:
        """Obtener inversiones con filtros opcionales"""
        query = db.query(Inversion).filter(Inversion.user_id == user_id)
        
        if año:
            query = query.filter(Inversion.año == año)
        if mes:
            query = query.filter(Inversion.mes == mes)
        if tipo_gasto:
            query = query.filter(Inversion.tipo_gasto == tipo_gasto)
        
        return query.order_by(Inversion.año.desc(), Inversion.mes.desc()).all()
    
    @staticmethod
    def inicializar_mes(db: Session, user_id: int, año: int, mes: int):
        """Inicializar los 4 tipos de gasto para un mes"""
        tipos = ['alimento', 'medicina', 'limpieza_galpon', 'entrenador']
        for tipo in tipos:
            inversion_existente = db.query(Inversion).filter(
                and_(
                    Inversion.user_id == user_id,
                    Inversion.año == año,
                    Inversion.mes == mes,
                    Inversion.tipo_gasto == tipo
                )
            ).first()
            
            if not inversion_existente:
                nueva_inversion = Inversion(
                    user_id=user_id,
                    año=año,
                    mes=mes,
                    tipo_gasto=tipo,
                    costo=0.00
                )
                db.add(nueva_inversion)
        
        db.commit()
    
    @staticmethod
    def crear_o_actualizar(
        db: Session,
        user_id: int,
        inversion_data: InversionCreate
    ) -> Inversion:
        """Crear o actualizar inversión (UPSERT)"""
        inversion = db.query(Inversion).filter(
            and_(
                Inversion.user_id == user_id,
                Inversion.año == inversion_data.año,
                Inversion.mes == inversion_data.mes,
                Inversion.tipo_gasto == inversion_data.tipo_gasto
            )
        ).first()
        
        if inversion:
            inversion.costo = inversion_data.costo
            inversion.fecha_registro = datetime.utcnow()
        else:
            inversion = Inversion(
                user_id=user_id,
                año=inversion_data.año,
                mes=inversion_data.mes,
                tipo_gasto=inversion_data.tipo_gasto,
                costo=inversion_data.costo
            )
            db.add(inversion)
        
        db.commit()
        db.refresh(inversion)
        return inversion
    
    @staticmethod
    def obtener_resumen_mensual(db: Session, user_id: int, año: int, mes: int) -> dict:
        """Obtener resumen de inversiones del mes"""
        # Inicializar mes si no existe
        InversionService.inicializar_mes(db, user_id, año, mes)
        
        inversiones = db.query(Inversion).filter(
            and_(
                Inversion.user_id == user_id,
                Inversion.año == año,
                Inversion.mes == mes
            )
        ).all()
        
        resumen = {
            "año": año,
            "mes": mes,
            "alimento": 0.00,
            "medicina": 0.00,
            "limpieza_galpon": 0.00,
            "entrenador": 0.00,
            "total": 0.00
        }
        
        for inv in inversiones:
            tipo = inv.tipo_gasto
            resumen[tipo] = float(inv.costo)
            resumen["total"] += float(inv.costo)
        
        return resumen
    
    @staticmethod
    def generar_reporte_anual(db: Session, user_id: int, año: int) -> dict:
        """Generar reporte anual de inversiones"""
        inversiones = db.query(
            Inversion.mes,
            Inversion.tipo_gasto,
            func.sum(Inversion.costo).label('total')
        ).filter(
            and_(
                Inversion.user_id == user_id,
                Inversion.año == año
            )
        ).group_by(Inversion.mes, Inversion.tipo_gasto).all()
        
        # Organizar por mes
        reporte_meses = {}
        for mes in range(1, 13):
            reporte_meses[mes] = {
                "mes": mes,
                "alimento": 0.00,
                "medicina": 0.00,
                "limpieza_galpon": 0.00,
                "entrenador": 0.00,
                "total": 0.00
            }
        
        # Llenar con datos reales
        for inv in inversiones:
            mes = inv.mes
            tipo = inv.tipo_gasto
            total = float(inv.total or 0)
            reporte_meses[mes][tipo] = total
            reporte_meses[mes]["total"] += total
        
        total_anual = sum(m["total"] for m in reporte_meses.values())
        
        return {
            "año": año,
            "meses": list(reporte_meses.values()),
            "total_anual": total_anual
        }