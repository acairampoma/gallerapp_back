"""
Script de prueba para los endpoints de vacunas
Asegúrate de tener el servidor FastAPI corriendo antes de ejecutar este script
"""

import requests
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any

# Configuración
BASE_URL = "http://localhost:8000"  # Cambia esto según tu configuración
USERNAME = "admin"  # Cambia con tus credenciales
PASSWORD = "admin123"

def get_token() -> str:
    """Obtener token de autenticación"""
    print("🔐 Obteniendo token de autenticación...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Token obtenido exitosamente")
        return token
    else:
        print(f"❌ Error al obtener token: {response.status_code}")
        print(response.text)
        exit(1)

def test_estadisticas(headers: Dict[str, str]):
    """Probar endpoint de estadísticas"""
    print("\n📊 Probando estadísticas de vacunas...")
    response = requests.get(f"{BASE_URL}/api/v1/vacunas/stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Estadísticas obtenidas:")
        print(f"   - Total vacunas: {stats['total_vacunas']}")
        print(f"   - Vacunas este mes: {stats['vacunas_este_mes']}")
        print(f"   - Próximas vacunas: {stats['proximas_vacunas']}")
        print(f"   - Vacunas vencidas: {stats['vacunas_vencidas']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_proximas_vacunas(headers: Dict[str, str]):
    """Probar endpoint de próximas vacunas"""
    print("\n🔜 Probando próximas vacunas...")
    response = requests.get(
        f"{BASE_URL}/api/v1/vacunas/proximas?dias_adelante=30", 
        headers=headers
    )
    
    if response.status_code == 200:
        vacunas = response.json()
        print(f"✅ Se encontraron {len(vacunas)} próximas vacunas")
        for v in vacunas[:3]:  # Mostrar solo las primeras 3
            print(f"   - Gallo: {v.get('gallo_nombre', 'N/A')}")
            print(f"     Vacuna: {v['tipo_vacuna']}")
            print(f"     Fecha: {v['proxima_dosis']}")
            print(f"     Días restantes: {v['dias_restantes']}")
            print(f"     Estado: {v['estado']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_crear_vacuna(headers: Dict[str, str]) -> int:
    """Probar creación de vacuna"""
    print("\n➕ Probando crear vacuna...")
    
    nueva_vacuna = {
        "gallo_id": 1,  # Asumiendo que existe un gallo con ID 1
        "tipo_vacuna": "Newcastle",
        "laboratorio": "Lab Test",
        "fecha_aplicacion": date.today().isoformat(),
        "proxima_dosis": (date.today() + timedelta(days=180)).isoformat(),
        "veterinario_nombre": "Dr. Test",
        "clinica": "Clínica Test",
        "dosis": "0.5ml",
        "notas": "Vacuna de prueba desde API"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/vacunas",
        headers=headers,
        json=nueva_vacuna
    )
    
    if response.status_code in [200, 201]:
        vacuna = response.json()
        print(f"✅ Vacuna creada con ID: {vacuna['id']}")
        return vacuna['id']
    else:
        print(f"❌ Error al crear vacuna: {response.status_code}")
        print(response.text)
        return None

def test_listar_vacunas(headers: Dict[str, str]):
    """Probar listado de vacunas"""
    print("\n📋 Probando listar vacunas...")
    response = requests.get(
        f"{BASE_URL}/api/v1/vacunas?limit=5",
        headers=headers
    )
    
    if response.status_code == 200:
        vacunas = response.json()
        print(f"✅ Se encontraron {len(vacunas)} vacunas")
        for v in vacunas[:3]:  # Mostrar solo las primeras 3
            print(f"   - ID: {v['id']}")
            print(f"     Tipo: {v['tipo_vacuna']}")
            print(f"     Gallo: {v.get('gallo_nombre', 'N/A')}")
            print(f"     Fecha: {v['fecha_aplicacion']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_registro_rapido(headers: Dict[str, str]):
    """Probar registro rápido de vacunas"""
    print("\n⚡ Probando registro rápido...")
    
    registro = {
        "gallo_ids": [1, 2],  # Asumiendo que existen gallos con estos IDs
        "tipo_vacunas": ["Newcastle", "Bronquitis"],
        "fecha_aplicacion": date.today().isoformat(),
        "veterinario_nombre": "Dr. Rápido",
        "clinica": "Clínica Express",
        "dosis": "0.5ml",
        "proxima_dosis": (date.today() + timedelta(days=90)).isoformat(),
        "notas": "Vacunación masiva de prueba"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/vacunas/registro-rapido",
        headers=headers,
        json=registro
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"✅ Registro rápido exitoso:")
        print(f"   - Registros creados: {result.get('registros_creados', 0)}")
        print(f"   - Mensaje: {result.get('message', '')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_actualizar_vacuna(headers: Dict[str, str], vacuna_id: int):
    """Probar actualización de vacuna"""
    if not vacuna_id:
        print("\n✏️ Saltando prueba de actualización (no hay ID)")
        return
    
    print(f"\n✏️ Probando actualizar vacuna ID {vacuna_id}...")
    
    actualizacion = {
        "notas": "Actualizado desde prueba API",
        "clinica": "Clínica Actualizada"
    }
    
    response = requests.put(
        f"{BASE_URL}/api/v1/vacunas/{vacuna_id}",
        headers=headers,
        json=actualizacion
    )
    
    if response.status_code == 200:
        print("✅ Vacuna actualizada exitosamente")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_eliminar_vacuna(headers: Dict[str, str], vacuna_id: int):
    """Probar eliminación de vacuna"""
    if not vacuna_id:
        print("\n🗑️ Saltando prueba de eliminación (no hay ID)")
        return
    
    print(f"\n🗑️ Probando eliminar vacuna ID {vacuna_id}...")
    
    response = requests.delete(
        f"{BASE_URL}/api/v1/vacunas/{vacuna_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ Vacuna eliminada exitosamente")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def main():
    """Ejecutar todas las pruebas"""
    print("=" * 50)
    print("🚀 PRUEBAS DE API DE VACUNAS")
    print("=" * 50)
    
    # Obtener token
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Ejecutar pruebas
    test_estadisticas(headers)
    test_proximas_vacunas(headers)
    test_listar_vacunas(headers)
    
    # Crear una vacuna y obtener su ID
    vacuna_id = test_crear_vacuna(headers)
    
    # Probar registro rápido
    test_registro_rapido(headers)
    
    # Actualizar la vacuna creada
    test_actualizar_vacuna(headers, vacuna_id)
    
    # Opcional: eliminar la vacuna de prueba
    # test_eliminar_vacuna(headers, vacuna_id)
    
    print("\n" + "=" * 50)
    print("✨ Pruebas completadas")
    print("=" * 50)

if __name__ == "__main__":
    main()