#!/usr/bin/env python3
# Diagnóstico de imports épicos

import sys
import os

# Añadir el directorio del proyecto
sys.path.insert(0, r'C:\Users\acairamp\Documents\proyecto\Curso\Flutter\galloapp_backend')

def test_individual_imports():
    """Probar cada import individualmente para encontrar el problema exacto"""
    
    print("=== DIAGNÓSTICO DE IMPORTS ÉPICOS ===")
    
    # Test 1: Imports básicos
    try:
        from fastapi import APIRouter
        print("✅ FastAPI - OK")
    except Exception as e:
        print(f"❌ FastAPI - {e}")
        return
    
    # Test 2: Database
    try:
        from app.database import get_db
        print("✅ Database - OK")
    except Exception as e:
        print(f"❌ Database - {e}")
        return
    
    # Test 3: Security
    try:
        from app.core.security import get_current_user_id
        print("✅ Security - OK")
    except Exception as e:
        print(f"❌ Security - {e}")
        return
    
    # Test 4: Modelo
    try:
        from app.models.gallo_simple import Gallo
        print("✅ Modelo Gallo - OK")
    except Exception as e:
        print(f"❌ Modelo Gallo - {e}")
        return
    
    # Test 5: Servicios específicos
    services = [
        ('cloudinary_service', 'CloudinaryService'),
        ('genealogy_service', 'GenealogyService'),
        ('validation_service', 'ValidationService')
    ]
    
    for service_module, service_class in services:
        try:
            module = __import__(f'app.services.{service_module}', fromlist=[service_class])
            service = getattr(module, service_class)
            print(f"✅ {service_class} - OK")
        except Exception as e:
            print(f"❌ {service_class} - {e}")
            print(f"   Detalle: {type(e).__name__}")
            return service_module, e
    
    # Test 6: Schemas
    try:
        from app.schemas.gallo import GenealogyCreateResponse
        print("✅ Schemas - OK")
    except Exception as e:
        print(f"❌ Schemas - {e}")
        return
    
    # Test 7: Import final del endpoint épico
    try:
        from app.api.v1.gallos_genealogia_epica import router
        print("✅ ¡ENDPOINT ÉPICO IMPORTADO EXITOSAMENTE!")
        print(f"📋 Router tiene {len(router.routes)} rutas")
        return True
    except Exception as e:
        print(f"❌ Endpoint épico - {e}")
        print(f"   Tipo: {type(e).__name__}")
        return False

if __name__ == "__main__":
    result = test_individual_imports()
    if result is True:
        print("\n🔥 ¡TODOS LOS IMPORTS FUNCIONAN!")
        print("   El problema debe estar en el server reload")
    else:
        print(f"\n💥 Problema encontrado: {result}")
