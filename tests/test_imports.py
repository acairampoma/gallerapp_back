"""Script para diagnosticar problemas de importación"""

print("=" * 50)
print("🔍 DIAGNÓSTICO DE IMPORTACIONES")
print("=" * 50)

# Test 1: Importar modelos
print("\n1. Probando importación de modelos...")
try:
    from app.models.user import User
    print("   ✅ User importado")
except Exception as e:
    print(f"   ❌ Error con User: {e}")

try:
    from app.models.gallo_simple import Gallo
    print("   ✅ Gallo importado")
except Exception as e:
    print(f"   ❌ Error con Gallo: {e}")

try:
    from app.models.vacuna import Vacuna
    print("   ✅ Vacuna importado")
except Exception as e:
    print(f"   ❌ Error con Vacuna: {e}")

# Test 2: Importar schemas
print("\n2. Probando importación de schemas...")
try:
    from app.schemas.vacuna import VacunaCreate, VacunaResponse
    print("   ✅ Schemas de vacuna importados")
except Exception as e:
    print(f"   ❌ Error con schemas de vacuna: {e}")

# Test 3: Importar routers
print("\n3. Probando importación de routers...")
try:
    from app.api.v1.gallos_con_pedigri import router as gallos_router
    print("   ✅ Router de gallos importado")
except Exception as e:
    print(f"   ❌ Error con router de gallos: {e}")

try:
    from app.api.v1.vacunas import router as vacunas_router
    print("   ✅ Router de vacunas importado")
except Exception as e:
    print(f"   ❌ Error con router de vacunas: {e}")

# Test 4: Probar app completa
print("\n4. Probando importación de app principal...")
try:
    from app.main import app
    print("   ✅ App principal importada")
    
    # Listar todas las rutas
    print("\n📋 RUTAS REGISTRADAS:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"   - {route.path}")
except Exception as e:
    print(f"   ❌ Error con app principal: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Diagnóstico completado")
print("=" * 50)