@echo off
echo === Probando login y token inmediatamente ===
echo.

echo 1. Haciendo login...
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"email\": \"prueba@test.com\", \"password\": \"Test123@\"}" > temp_login.txt 2>nul

echo.
echo 2. Respuesta del login:
type temp_login.txt

echo.
echo 3. Extrayendo token...
for /f "tokens=2 delims=:" %%a in ('findstr "access_token" temp_login.txt') do set TOKEN=%%a
set TOKEN=%TOKEN:"=%
set TOKEN=%TOKEN:,refresh_token=%
set TOKEN=%TOKEN: =%

echo Token extraido (primeros 50 chars): %TOKEN:~0,50%...

echo.
echo 4. Probando token INMEDIATAMENTE (deberia funcionar)...
curl -X GET http://localhost:8000/auth/me -H "Authorization: Bearer %TOKEN%"

echo.
echo.
echo 5. Esperando 5 segundos...
timeout /t 5 /nobreak > nul

echo.
echo 6. Probando token de nuevo (deberia seguir funcionando)...
curl -X GET http://localhost:8000/auth/me -H "Authorization: Bearer %TOKEN%"

del temp_login.txt
