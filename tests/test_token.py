from datetime import datetime, timedelta
import time
from jose import jwt

# Simular creación de token
SECRET_KEY = "galloapp-super-secret-key-development"
ALGORITHM = "HS256"

# Crear token
data = {"sub": "14"}
expire = datetime.utcnow() + timedelta(minutes=30)
to_encode = data.copy()
to_encode.update({"exp": expire, "type": "access"})

print(f"Fecha actual UTC: {datetime.utcnow()}")
print(f"Fecha expiración: {expire}")
print(f"Diferencia en minutos: {(expire - datetime.utcnow()).total_seconds() / 60}")

# Crear token
token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
print(f"\nToken generado: {token}")

# Decodificar inmediatamente
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp_timestamp = payload.get("exp")
    exp_date = datetime.fromtimestamp(exp_timestamp)
    
    print(f"\nToken decodificado:")
    print(f"Timestamp exp: {exp_timestamp}")
    print(f"Fecha exp: {exp_date}")
    print(f"Fecha actual: {datetime.utcnow()}")
    print(f"¿Expirado? {datetime.utcnow() > exp_date}")
    
except Exception as e:
    print(f"Error: {e}")

# Esperar 1 segundo y verificar de nuevo
print("\n--- Esperando 1 segundo ---")
time.sleep(1)

try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp_date = datetime.fromtimestamp(payload.get("exp"))
    print(f"Fecha actual después de 1 seg: {datetime.utcnow()}")
    print(f"¿Expirado? {datetime.utcnow() > exp_date}")
except Exception as e:
    print(f"Error después de 1 segundo: {e}")
