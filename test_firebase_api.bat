@echo off
echo ========================================
echo 🔧 TEST FIREBASE STATUS
echo ========================================

echo.
echo 1. Verificando Health con Firebase status:
curl -X GET https://gallerappback-production.up.railway.app/health

echo.
echo.
echo 2. Si tienes tu JWT token, prueba el test de notificacion:
echo curl -X POST https://gallerappback-production.up.railway.app/api/v1/notifications/test-notification -H "Authorization: Bearer TU_TOKEN_JWT"

echo.
echo ========================================
pause