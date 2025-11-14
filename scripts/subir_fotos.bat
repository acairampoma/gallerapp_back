@echo off
echo === Subiendo fotos a los 7 gallos de la familia ===
echo.

set TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNSIsImV4cCI6MTc1MzYwMTY2NywidHlwZSI6ImFjY2VzcyJ9.JP-SlTSoyeKJnotGcMzTiungeSZXnog-CrCg0T3tDKY
set BASE_URL=http://localhost:8000/api/v1/gallos

echo 1. Subiendo foto a Rey Supremo (ID: 17)...
curl -X POST %BASE_URL%/17/foto-principal -H "Authorization: Bearer %TOKEN%" -F "foto=@C:/Users/acairamp/Documents/proyecto/Curso/Flutter/gallos_app_new/assets/images/gallos/gallo1.webp" -F "descripcion=Rey Supremo - Gallo Principal"
echo.

echo 2. Subiendo foto a Padre Rey (ID: 18)...
curl -X POST %BASE_URL%/18/foto-principal -H "Authorization: Bearer %TOKEN%" -F "foto=@C:/Users/acairamp/Documents/proyecto/Curso/Flutter/gallos_app_new/assets/images/gallos/gallo2.webp" -F "descripcion=Padre Rey"
echo.

echo 3. Subiendo foto a Madre Reina (ID: 19)...
curl -X POST %BASE_URL%/19/foto-principal -H "Authorization: Bearer %TOKEN%" -F "foto=@C:/Users/acairamp/Documents/proyecto/Curso/Flutter/gallos_app_new/assets/images/gallos/gallo3.webp" -F "descripcion=Madre Reina"
echo.

echo 4. Subiendo foto a Abuelo Paterno Rey (ID: 20)...
curl -X POST %BASE_URL%/20/foto-principal -H "Authorization: Bearer %TOKEN%" -F "foto=@C:/Users/acairamp/Documents/proyecto/Curso/Flutter/gallos_app_new/assets/images/gallos/gallo4.webp" -F "descripcion=Abuelo Paterno Rey"
echo.

echo 5. Subiendo foto a Abuela Paterna Rey (ID: 21)...
curl -X POST %BASE_URL%/21/foto-principal -H "Authorization: Bearer %TOKEN%" -F "foto=@C:/Users/acairamp/Documents/proyecto/Curso/Flutter/gallos_app_new/assets/images/gallos/gallo5.webp" -F "descripcion=Abuela Paterna Rey"
echo.

echo 6. Subiendo foto a Abuelo Materno Rey (ID: 22)...
curl -X POST %BASE_URL%/22/foto-principal -H "Authorization: Bearer %TOKEN%" -F "foto=@C:/Users/acairamp/Documents/proyecto/Curso/Flutter/gallos_app_new/assets/images/gallos/gallo6.webp" -F "descripcion=Abuelo Materno Rey"
echo.

echo 7. Subiendo foto a Abuela Materna Rey (ID: 23)...
curl -X POST %BASE_URL%/23/foto-principal -H "Authorization: Bearer %TOKEN%" -F "foto=@C:/Users/acairamp/Documents/proyecto/Curso/Flutter/gallos_app_new/assets/images/gallos/gallo7.webp" -F "descripcion=Abuela Materna Rey"
echo.

echo === Proceso completado ===
