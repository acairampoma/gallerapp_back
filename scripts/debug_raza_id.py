#!/usr/bin/env python3
# 🔍 Script para debuggear el problema de raza_id

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import get_db, DATABASE_URL
import asyncio

def debug_raza_id():
    """🔍 Debuggear problema de raza_id"""
    
    print("🔍 DEBUGGING RAZA_ID PROBLEM")
    print("=" * 50)
    
    # Crear conexión directa
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Verificar estructura de la tabla gallos
        print("\n1. 📋 ESTRUCTURA DE LA TABLA GALLOS:")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'gallos' 
            AND column_name LIKE '%raza%'
            ORDER BY ordinal_position;
        """))
        
        columns = result.fetchall()
        if columns:
            for col in columns:
                print(f"   - {col.column_name}: {col.data_type} (nullable: {col.is_nullable})")
        else:
            print("   ❌ NO SE ENCONTRÓ COLUMNA raza_id EN LA TABLA")
        
        # 2. Verificar si hay gallos con raza_id
        print("\n2. 🐓 GALLOS CON RAZA_ID:")
        result = db.execute(text("""
            SELECT id, nombre, raza_id, codigo_identificacion 
            FROM gallos 
            WHERE raza_id IS NOT NULL 
            LIMIT 5;
        """))
        
        gallos = result.fetchall()
        if gallos:
            for gallo in gallos:
                print(f"   - ID: {gallo.id}, Nombre: {gallo.nombre}, raza_id: '{gallo.raza_id}'")
        else:
            print("   ⚠️ NO HAY GALLOS CON raza_id GUARDADO")
        
        # 3. Verificar todos los gallos (últimos 5)
        print("\n3. 🔍 ÚLTIMOS 5 GALLOS CREADOS:")
        result = db.execute(text("""
            SELECT id, nombre, raza_id, codigo_identificacion, created_at 
            FROM gallos 
            ORDER BY created_at DESC 
            LIMIT 5;
        """))
        
        gallos = result.fetchall()
        for gallo in gallos:
            raza_status = f"'{gallo.raza_id}'" if gallo.raza_id else "NULL"
            print(f"   - ID: {gallo.id}, Nombre: {gallo.nombre}, raza_id: {raza_status}")
        
        # 4. Test de inserción directa
        print("\n4. 🧪 TEST DE INSERCIÓN DIRECTA:")
        try:
            test_result = db.execute(text("""
                INSERT INTO gallos (
                    user_id, nombre, codigo_identificacion, raza_id, estado, tipo_registro
                ) VALUES (
                    1, 'TEST_RAZA', 'TEST_001', 'RAZA_TEST_123', 'activo', 'test'
                ) RETURNING id, raza_id;
            """))
            
            test_row = test_result.fetchone()
            print(f"   ✅ INSERCIÓN EXITOSA - ID: {test_row.id}, raza_id: '{test_row.raza_id}'")
            
            # Limpiar test
            db.execute(text("DELETE FROM gallos WHERE codigo_identificacion = 'TEST_001'"))
            db.commit()
            
        except Exception as e:
            print(f"   ❌ ERROR EN INSERCIÓN: {e}")
            db.rollback()
        
        # 5. Verificar tipos de datos
        print("\n5. 📊 INFORMACIÓN DETALLADA DE LA COLUMNA raza_id:")
        result = db.execute(text("""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = 'gallos' 
            AND column_name = 'raza_id';
        """))
        
        col_info = result.fetchone()
        if col_info:
            print(f"   - Nombre: {col_info.column_name}")
            print(f"   - Tipo: {col_info.data_type}")
            print(f"   - Longitud máxima: {col_info.character_maximum_length}")
            print(f"   - Nullable: {col_info.is_nullable}")
            print(f"   - Default: {col_info.column_default}")
        else:
            print("   ❌ COLUMNA raza_id NO ENCONTRADA")
            
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")
        
    finally:
        db.close()
    
    print("\n" + "=" * 50)
    print("🔍 DEBUG COMPLETADO")

if __name__ == "__main__":
    debug_raza_id()
