@echo off
echo 🚀 Desplegando fix para endpoint de limites...

cd "C:\Users\acairamp\Documents\proyecto\Curso\Flutter\galloapp_backend"

echo ✅ Agregando cambios al staging...
git add app/schemas/suscripcion.py

echo ✅ Haciendo commit...
git commit -m "🔧 Fix error 500 en /suscripciones/limites - hacer campos opcional"

echo ✅ Haciendo push a Railway...
git push origin main

echo 🎯 Esperando deploy de Railway...
echo Nota: El deploy puede tomar 2-3 minutos
echo ⏳ Una vez completado, probar: curl -X GET "URL/api/v1/suscripciones/limites" -H "Authorization: Bearer TOKEN"

pause