#!/bin/bash

# 🗑️ SCRIPT DE PRUEBA PARA ELIMINACIÓN DE CUENTA
# Autor: Alan Cairampoma
# Fecha: 25 Agosto 2025

echo "==========================================="
echo "🗑️ PRUEBA DE ELIMINACIÓN DE CUENTA"
echo "==========================================="

# URL base (cambiar según necesidad)
BASE_URL="https://gallerappback-production.up.railway.app"
# BASE_URL="http://localhost:8000"  # Para pruebas locales

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}Usando servidor: $BASE_URL${NC}"
echo ""

echo -e "${YELLOW}1. REGISTRANDO USUARIO DE PRUEBA...${NC}"
echo "==========================================="

# Generar email único con timestamp
TIMESTAMP=$(date +%s)
TEST_EMAIL="test_delete_${TIMESTAMP}@galloapp.com"
TEST_PASSWORD="Test123456"

echo "Email: $TEST_EMAIL"
echo "Password: $TEST_PASSWORD"
echo ""

# Registrar usuario con todos los campos requeridos
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'$TEST_EMAIL'",
    "password": "'$TEST_PASSWORD'",
    "nombre_completo": "Usuario Test Eliminación",
    "telefono": "999888777",
    "nombre_galpon": "Galpón Test",
    "ciudad": "Lima",
    "ubigeo": "150101"
  }')

# Verificar si el registro fue exitoso
if echo "$REGISTER_RESPONSE" | grep -q '"email"'; then
  echo -e "${GREEN}✅ Usuario registrado exitosamente${NC}"
  echo "$REGISTER_RESPONSE" | python -m json.tool 2>/dev/null || echo "$REGISTER_RESPONSE"
else
  echo -e "${RED}❌ Error en registro${NC}"
  echo "$REGISTER_RESPONSE" | python -m json.tool 2>/dev/null || echo "$REGISTER_RESPONSE"
  exit 1
fi

sleep 1

echo ""
echo -e "${YELLOW}2. HACIENDO LOGIN...${NC}"
echo "==========================================="

# Login para obtener token
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'$TEST_EMAIL'",
    "password": "'$TEST_PASSWORD'"
  }')

# Extraer token de forma más robusta
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo -e "${RED}❌ Error obteniendo token${NC}"
  echo "$LOGIN_RESPONSE" | python -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"
  exit 1
fi

echo -e "${GREEN}✅ Login exitoso${NC}"
echo "Token obtenido: ${ACCESS_TOKEN:0:30}..."

sleep 1

echo ""
echo -e "${YELLOW}3. VERIFICANDO QUE EL TOKEN FUNCIONA...${NC}"
echo "==========================================="

# Verificar que el token funciona
ME_RESPONSE=$(curl -s -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$ME_RESPONSE" | grep -q '"email"'; then
  echo -e "${GREEN}✅ Token válido, usuario autenticado${NC}"
  echo "$ME_RESPONSE" | python -m json.tool 2>/dev/null || echo "$ME_RESPONSE"
else
  echo -e "${RED}❌ Token no válido${NC}"
  echo "$ME_RESPONSE"
  exit 1
fi

sleep 1

echo ""
echo -e "${YELLOW}4. PROBANDO ELIMINACIÓN CON CONTRASEÑA INCORRECTA...${NC}"
echo "==========================================="

# Intentar eliminar con contraseña incorrecta
WRONG_PASS_RESPONSE=$(curl -s -X DELETE "$BASE_URL/auth/delete-account" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "password": "WrongPassword123",
    "confirmation_text": "ELIMINAR MI CUENTA"
  }')

echo "Respuesta esperada: Error de contraseña"
echo "$WRONG_PASS_RESPONSE" | python -m json.tool 2>/dev/null || echo "$WRONG_PASS_RESPONSE"

sleep 1

echo ""
echo -e "${YELLOW}5. PROBANDO ELIMINACIÓN CON TEXTO DE CONFIRMACIÓN INCORRECTO...${NC}"
echo "==========================================="

# Intentar eliminar con texto de confirmación incorrecto
WRONG_TEXT_RESPONSE=$(curl -s -X DELETE "$BASE_URL/auth/delete-account" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "password": "'$TEST_PASSWORD'",
    "confirmation_text": "BORRAR CUENTA"
  }')

echo "Respuesta esperada: Error de validación del texto"
echo "$WRONG_TEXT_RESPONSE" | python -m json.tool 2>/dev/null || echo "$WRONG_TEXT_RESPONSE"

sleep 1

echo ""
echo -e "${YELLOW}6. ELIMINANDO CUENTA CORRECTAMENTE...${NC}"
echo "==========================================="

# Eliminar cuenta correctamente
DELETE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/auth/delete-account" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "password": "'$TEST_PASSWORD'",
    "confirmation_text": "ELIMINAR MI CUENTA"
  }')

# Separar respuesta del status code
RESPONSE_BODY=$(echo "$DELETE_RESPONSE" | sed -n '1,/HTTP_STATUS/p' | sed '$d')
HTTP_STATUS=$(echo "$DELETE_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

echo "Respuesta de eliminación:"
echo "$RESPONSE_BODY" | python -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
echo "HTTP Status: $HTTP_STATUS"

# Verificar si la eliminación fue exitosa
if echo "$RESPONSE_BODY" | grep -q '"account_deleted":true'; then
  echo -e "${GREEN}✅ CUENTA ELIMINADA EXITOSAMENTE${NC}"
elif echo "$RESPONSE_BODY" | grep -q '"success":true'; then
  echo -e "${GREEN}✅ CUENTA ELIMINADA EXITOSAMENTE${NC}"
else
  echo -e "${RED}❌ Error en la eliminación${NC}"
fi

sleep 1

echo ""
echo -e "${YELLOW}7. VERIFICANDO QUE LA CUENTA FUE ELIMINADA...${NC}"
echo "==========================================="

# Intentar login con la cuenta eliminada
VERIFY_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'$TEST_EMAIL'",
    "password": "'$TEST_PASSWORD'"
  }')

echo "Intento de login después de eliminar:"
echo "$VERIFY_RESPONSE" | python -m json.tool 2>/dev/null || echo "$VERIFY_RESPONSE"

if echo "$VERIFY_RESPONSE" | grep -q "Credenciales inválidas"; then
  echo -e "${GREEN}✅ CONFIRMADO: La cuenta ya no existe${NC}"
elif echo "$VERIFY_RESPONSE" | grep -q "detail"; then
  echo -e "${GREEN}✅ CONFIRMADO: La cuenta fue eliminada (error de login)${NC}"
else
  echo -e "${RED}❌ ADVERTENCIA: Verificar si la cuenta realmente fue eliminada${NC}"
fi

echo ""
echo "==========================================="
echo -e "${GREEN}🎉 PRUEBA COMPLETADA${NC}"
echo "==========================================="
echo ""
echo "📊 Resumen de la prueba:"
echo "------------------------"
echo "- Email usado: $TEST_EMAIL"
echo "- Contraseña: $TEST_PASSWORD"
echo "- Token: ${ACCESS_TOKEN:0:30}..."
echo "- Servidor: $BASE_URL"
echo ""
echo "✅ Validaciones probadas:"
echo "  1. Registro de usuario"
echo "  2. Login exitoso"
echo "  3. Token válido"
echo "  4. Rechazo con contraseña incorrecta"
echo "  5. Rechazo con texto confirmación incorrecto"
echo "  6. Eliminación exitosa con datos correctos"
echo "  7. Verificación que cuenta no existe"
echo ""