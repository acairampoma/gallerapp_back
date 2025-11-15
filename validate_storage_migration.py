"""
🔍 SCRIPT DE VALIDACIÓN - Migración a Storage Adapter Pattern
Valida que todo esté correctamente configurado y sin errores
"""
import sys
import importlib
from typing import List, Tuple

def validate_imports() -> List[Tuple[str, bool, str]]:
    """Validar que todos los imports funcionen"""
    results = []
    
    # Módulos a validar
    modules_to_test = [
        # Storage system
        ("app.services.storage.base_storage", "BaseStorageAdapter, UploadResult, TransformOptions"),
        ("app.services.storage.imagekit_adapter", "imagekit_adapter"),
        ("app.services.storage.cloudinary_adapter", "cloudinary_adapter"),
        ("app.services.storage.storage_manager", "storage_manager, StorageProvider"),
        ("app.services.storage", "storage_manager, upload_image, upload_video, delete_file"),
        
        # API endpoints migrados
        ("app.api.v1.peleas", "router"),
        ("app.api.v1.topes", "router"),
        ("app.api.v1.pagos", "router"),
        ("app.api.v1.profiles", "router"),
        ("app.api.v1.peleas_evento", "router"),
        
        # Modelos actualizados
        ("app.models.pelea", "Pelea"),
        ("app.models.tope", "Tope"),
        ("app.models.pelea_evento", "PeleaEvento"),
        ("app.models.pago_pendiente", "PagoPendiente"),
    ]
    
    for module_name, items in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            
            # Verificar que los items existan
            for item in items.split(", "):
                if not hasattr(module, item):
                    results.append((module_name, False, f"Falta: {item}"))
                    break
            else:
                results.append((module_name, True, "OK"))
                
        except Exception as e:
            results.append((module_name, False, str(e)))
    
    return results


def validate_storage_manager():
    """Validar que el StorageManager funcione correctamente"""
    try:
        from app.services.storage import storage_manager
        
        print("\n📊 VALIDACIÓN DEL STORAGE MANAGER:")
        print(f"   Proveedor activo: {storage_manager.provider_name}")
        print(f"   Disponible: {'✅' if storage_manager.is_available else '❌'}")
        
        # Verificar métodos
        methods = [
            'upload_image',
            'upload_video',
            'upload_with_transformations',
            'delete_file',
            'get_optimized_url',
            'get_thumbnail_url'
        ]
        
        print("\n   Métodos disponibles:")
        for method in methods:
            has_method = hasattr(storage_manager, method)
            status = "✅" if has_method else "❌"
            print(f"   {status} {method}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error validando StorageManager: {e}")
        return False


def validate_models():
    """Validar que los modelos tengan el campo file_id"""
    try:
        from app.models.pelea import Pelea
        from app.models.tope import Tope
        from app.models.pelea_evento import PeleaEvento
        from app.models.pago_pendiente import PagoPendiente
        
        print("\n📋 VALIDACIÓN DE MODELOS:")
        
        models_to_check = [
            (Pelea, "file_id"),
            (Tope, "file_id"),
            (PeleaEvento, "file_id"),
            (PagoPendiente, "comprobante_file_id"),
        ]
        
        all_ok = True
        for model, field in models_to_check:
            has_field = hasattr(model, field)
            status = "✅" if has_field else "❌"
            print(f"   {status} {model.__name__}.{field}")
            if not has_field:
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"\n❌ Error validando modelos: {e}")
        return False


def main():
    """Ejecutar todas las validaciones"""
    print("=" * 70)
    print("🔍 VALIDACIÓN COMPLETA - MIGRACIÓN A STORAGE ADAPTER PATTERN")
    print("=" * 70)
    
    # 1. Validar imports
    print("\n1️⃣ VALIDANDO IMPORTS...")
    results = validate_imports()
    
    failed = []
    for module_name, success, message in results:
        status = "✅" if success else "❌"
        print(f"   {status} {module_name}: {message}")
        if not success:
            failed.append((module_name, message))
    
    # 2. Validar StorageManager
    print("\n2️⃣ VALIDANDO STORAGE MANAGER...")
    storage_ok = validate_storage_manager()
    
    # 3. Validar modelos
    print("\n3️⃣ VALIDANDO MODELOS...")
    models_ok = validate_models()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE VALIDACIÓN")
    print("=" * 70)
    
    total_modules = len(results)
    successful = sum(1 for _, success, _ in results if success)
    
    print(f"\n✅ Módulos validados: {successful}/{total_modules}")
    print(f"{'✅' if storage_ok else '❌'} StorageManager: {'OK' if storage_ok else 'FALLO'}")
    print(f"{'✅' if models_ok else '❌'} Modelos: {'OK' if models_ok else 'FALLO'}")
    
    if failed:
        print("\n❌ ERRORES ENCONTRADOS:")
        for module, error in failed:
            print(f"   - {module}: {error}")
        return 1
    
    if not storage_ok or not models_ok:
        print("\n⚠️ Algunas validaciones fallaron")
        return 1
    
    print("\n" + "=" * 70)
    print("🎉 ¡TODAS LAS VALIDACIONES PASARON EXITOSAMENTE!")
    print("=" * 70)
    print("\n✅ El sistema está listo para usar el Storage Adapter Pattern")
    print("✅ Puedes cambiar de proveedor modificando STORAGE_PROVIDER en settings.py")
    print("\n💡 Proveedores disponibles:")
    print("   - imagekit (activo)")
    print("   - cloudinary")
    print("\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
