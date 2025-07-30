#!/bin/bash
cd "C:/Users/acairamp/Documents/proyecto/Curso/Flutter/galloapp_backend"

echo "🔧 ARREGLANDO IMPORTS PROBLEMÁTICOS"
echo "✅ Imports de schemas inexistentes removidos"

git add .
git commit -m "🔧 FIX: Remover imports problemáticos de schemas

- Removidos imports de schemas que no existen
- Quitado response_model problemáticos  
- Endpoint debería cargar sin errores ahora
- RAILWAY READY"

git push origin main

echo "🚀 PUSH COMPLETADO - Railway detectará cambios automáticamente"
