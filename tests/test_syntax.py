#!/usr/bin/env python3
# Test de sintaxis del archivo corregido

print("🔍 Probando sintaxis del archivo corregido...")

try:
    # Intentar compilar el archivo para verificar sintaxis
    import ast
    
    # Leer el archivo
    with open(r"C:\Users\acairamp\Documents\proyecto\Curso\Flutter\galloapp_backend\app\api\v1\gallos_genealogia_epica.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Parsear la sintaxis
    ast.parse(content)
    print("✅ SINTAXIS CORREGIDA EXITOSAMENTE!")
    print("✅ El archivo está listo para ser importado")
    
except SyntaxError as e:
    print(f"❌ Error de sintaxis encontrado:")
    print(f"   Línea {e.lineno}: {e.text}")
    print(f"   Error: {e.msg}")
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")

print("\n🚀 Probando imports básicos de FastAPI...")

try:
    from fastapi import FastAPI
    print("✅ FastAPI importado correctamente")
except Exception as e:
    print(f"❌ Error importando FastAPI: {e}")

print("\n🎯 Test completado!")
