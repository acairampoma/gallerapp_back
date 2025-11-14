#!/usr/bin/env python3
"""Script para debugear el error en POST /peleas"""

import asyncio
import sys
from datetime import datetime

# Simular la creación de una pelea sin validaciones complejas
def test_pelea_creation():
    print("🔍 DEBUGGING POST /peleas")
    print("=" * 40)
    
    # Datos de prueba
    test_data = {
        "gallo_id": 1,
        "titulo": "Test Pelea Debug",
        "fecha_pelea": datetime.now(),
        "descripcion": "Pelea de prueba para debug",
        "ubicacion": "Campo de Testing",
        "oponente_nombre": "Oponente Test",
        "oponente_gallo": "Gallo Rival",
        "resultado": "ganada",
        "notas_resultado": "Victoria por debug"
    }
    
    print("📋 Datos de prueba:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    print("\n🎯 Posibles causas del error:")
    print("1. ❌ ForeignKey constraint violation (gallo_id no existe)")
    print("2. ❌ User_id constraint violation (user no existe)")  
    print("3. ❌ Campo requerido faltante")
    print("4. ❌ Tipo de dato incorrecto")
    print("5. ❌ Problema de timezone en fecha")
    
    print("\n💡 Solución temporal aplicada:")
    print("   - Comentar validación de gallo_id")
    print("   - Permitir user_id y gallo_id nullable")
    
    print("\n🚀 Probar endpoint simplificado:")
    print("""
    curl -X POST "http://localhost:8000/api/v1/peleas/" \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -F "gallo_id=1" \\
      -F "titulo=Debug Test" \\
      -F "fecha_pelea=2024-12-25T15:30:00"
    """)

if __name__ == "__main__":
    test_pelea_creation()