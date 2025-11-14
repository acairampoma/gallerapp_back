import requests
import os

# Configuración
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNSIsImV4cCI6MTc1MzYwMTY2NywidHlwZSI6ImFjY2VzcyJ9.JP-SlTSoyeKJnotGcMzTiungeSZXnog-CrCg0T3tDKY"
BASE_URL = "http://localhost:8000/api/v1/gallos"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Mapeo de gallos y fotos
gallos_fotos = [
    (17, "gallo1.webp", "Rey Supremo"),
    (18, "gallo2.webp", "Padre Rey"),
    (19, "gallo3.webp", "Madre Reina"),
    (20, "gallo4.webp", "Abuelo Paterno Rey"),
    (21, "gallo5.webp", "Abuela Paterna Rey"),
    (22, "gallo6.webp", "Abuelo Materno Rey"),
    (23, "gallo7.webp", "Abuela Materna Rey")
]

base_path = "C:/Users/acairamp/Documents/proyecto/Curso/Flutter/gallos_app_new/assets/images/gallos/"

print("=== SUBIENDO FOTOS A LOS 7 GALLOS ===\n")

for gallo_id, foto_nombre, descripcion in gallos_fotos:
    print(f"Subiendo foto para {descripcion} (ID: {gallo_id})...")
    
    file_path = os.path.join(base_path, foto_nombre)
    
    try:
        with open(file_path, 'rb') as f:
            files = {'foto': (foto_nombre, f, 'image/webp')}
            data = {'descripcion': f'{descripcion} - Foto principal'}
            
            response = requests.post(
                f"{BASE_URL}/{gallo_id}/foto",
                headers=HEADERS,
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ ÉXITO: {result['message']}")
                    print(f"   URL: {result['data']['cloudinary']['secure_url']}")
                else:
                    print(f"❌ ERROR: {result}")
            else:
                print(f"❌ ERROR HTTP {response.status_code}: {response.text}")
                
    except Exception as e:
        print(f"❌ EXCEPCIÓN: {str(e)}")
    
    print()

print("=== PROCESO COMPLETADO ===")
