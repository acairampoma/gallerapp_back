import requests
import json
import time

print("=== PRUEBA DE TOKEN JWT ===\n")

# 1. Login
print("1. Haciendo login...")
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"email": "prueba@test.com", "password": "Test123@"}
)

if login_response.status_code != 200:
    print(f"Error en login: {login_response.text}")
    exit(1)

login_data = login_response.json()
token = login_data["token"]["access_token"]
print(f"Login exitoso. Token obtenido (primeros 50 chars): {token[:50]}...")

# 2. Probar token inmediatamente
print("\n2. Probando token INMEDIATAMENTE...")
headers = {"Authorization": f"Bearer {token}"}
test_response = requests.get("http://localhost:8000/auth/me", headers=headers)

if test_response.status_code == 200:
    user_data = test_response.json()
    print(f"✅ TOKEN FUNCIONA! Usuario: {user_data['email']}")
else:
    print(f"❌ TOKEN NO FUNCIONA! Error: {test_response.text}")

# 3. Esperar y probar de nuevo
print("\n3. Esperando 5 segundos...")
time.sleep(5)

print("\n4. Probando token de nuevo...")
test_response2 = requests.get("http://localhost:8000/auth/me", headers=headers)

if test_response2.status_code == 200:
    print(f"✅ TOKEN SIGUE FUNCIONANDO después de 5 segundos!")
else:
    print(f"❌ TOKEN YA NO FUNCIONA! Error: {test_response2.text}")

# 5. Decodificar el token para ver la expiración
try:
    import base64
    import json
    
    # Decodificar el payload del JWT (sin verificar firma)
    parts = token.split('.')
    payload = parts[1]
    # Agregar padding si es necesario
    payload += '=' * (4 - len(payload) % 4)
    decoded = base64.b64decode(payload)
    payload_data = json.loads(decoded)
    
    print(f"\n5. Información del token:")
    print(f"   - Usuario ID: {payload_data.get('sub')}")
    print(f"   - Tipo: {payload_data.get('type')}")
    print(f"   - Timestamp expiración: {payload_data.get('exp')}")
    
    # Convertir timestamp a fecha
    from datetime import datetime
    exp_date = datetime.fromtimestamp(payload_data.get('exp'))
    now = datetime.now()
    
    print(f"   - Fecha expiración: {exp_date}")
    print(f"   - Fecha actual: {now}")
    print(f"   - Tiempo restante: {(exp_date - now).total_seconds() / 60:.1f} minutos")
    
except Exception as e:
    print(f"\nError decodificando token: {e}")
