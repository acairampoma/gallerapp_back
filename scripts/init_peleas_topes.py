#!/usr/bin/env python3
# 🚀 Script para crear tablas de Peleas y Topes en la BD

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models.pelea import Pelea
from app.models.tope import Tope

def create_tables():
    """Crear tablas de Peleas y Topes"""
    print("🔨 Creando tablas de Peleas y Topes...")
    
    try:
        # Crear solo las tablas nuevas
        Base.metadata.create_all(bind=engine, tables=[
            Pelea.__table__,
            Tope.__table__
        ])
        
        print("✅ Tablas creadas exitosamente:")
        print("   - peleas")
        print("   - topes")
        
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🥊 CREACIÓN DE TABLAS PELEAS Y TOPES")
    print("=" * 50)
    
    if create_tables():
        print("\n✅ ¡Proceso completado exitosamente!")
    else:
        print("\n❌ Hubo errores en el proceso")