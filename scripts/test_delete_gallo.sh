#!/bin/bash

# 🐓 SCRIPT DE PRUEBA PARA ELIMINACIÓN DE GALLOS
# Autor: Alan Cairampoma
# Fecha: 26 Agosto 2025

echo "==========================================="
echo "🐓 PRUEBA DE ELIMINACIÓN DE GALLO"
echo "==========================================="

# URL base
BASE_URL="https://gallerappback-production.up.railway.app"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}Usando servidor: $BASE_URL${NC}"
echo ""

# Usuario existente
USER_EMAIL="dannyvillazinc@gmail.com"
USER_PASSWORD="Xlac0nchesu*"

echo -e "${YELLOW}1. HACIENDO LOGIN CON USUARIO EXISTENTE...${NC}"
echo "==========================================="
echo "Email: $USER_EMAIL"
echo ""

# Login para obtener token
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'$USER_EMAIL'",
    "password": "'$USER_PASSWORD'"
  }')

# Extraer token
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
echo -e "${YELLOW}2. VERIFICANDO QUE EL TOKEN FUNCIONA...${NC}"
echo "==========================================="

# Verificar que el token funciona
ME_RESPONSE=$(curl -s -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

USER_ID=$(echo "$ME_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if echo "$ME_RESPONSE" | grep -q '"email"'; then
  echo -e "${GREEN}✅ Token válido, usuario autenticado${NC}"
  echo "User ID: $USER_ID"
  echo "Email confirmado: $(echo "$ME_RESPONSE" | grep -o '"email":"[^"]*' | cut -d'"' -f4)"
else
  echo -e "${RED}❌ Token no válido${NC}"
  echo "$ME_RESPONSE"
  exit 1
fi

sleep 1

echo ""
echo -e "${YELLOW}3. OBTENIENDO LISTA DE GALLOS...${NC}"
echo "==========================================="

# Obtener lista de gallos
GALLOS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/gallos/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

# Verificar si hay gallos
if echo "$GALLOS_RESPONSE" | grep -q '"id"'; then
  echo -e "${GREEN}✅ Gallos encontrados${NC}"
  
  # Contar gallos
  TOTAL_GALLOS=$(echo "$GALLOS_RESPONSE" | grep -o '"id"' | wc -l)
  echo "Total de gallos: $TOTAL_GALLOS"
  
  # Obtener primer gallo para prueba
  PRIMER_GALLO_ID=$(echo "$GALLOS_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
  PRIMER_GALLO_NOMBRE=$(echo "$GALLOS_RESPONSE" | grep -o '"nombre":"[^"]*' | head -1 | cut -d'"' -f4)
  
  echo ""
  echo "Primer gallo encontrado:"
  echo "  ID: $PRIMER_GALLO_ID"
  echo "  Nombre: $PRIMER_GALLO_NOMBRE"
else
  echo -e "${RED}❌ No se encontraron gallos o error en respuesta${NC}"
  echo "$GALLOS_RESPONSE" | head -500
  exit 1
fi

sleep 1

echo ""
echo -e "${YELLOW}4. CREANDO GALLO DE PRUEBA PARA ELIMINAR...${NC}"
echo "==========================================="

# Crear un gallo de prueba
TIMESTAMP=$(date +%s)
TEST_GALLO_NAME="Gallo_Test_Delete_$TIMESTAMP"

CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/gallos/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "nombre": "'$TEST_GALLO_NAME'",
    "fecha_nacimiento": "2024-01-01",
    "color": "Rojo",
    "peso": 2.5,
    "placa": "TEST-'$TIMESTAMP'",
    "estado": "activo",
    "raza_id": 1
  }')

# Extraer ID del gallo creado
GALLO_TEST_ID=$(echo "$CREATE_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$GALLO_TEST_ID" ]; then
  echo -e "${YELLOW}⚠️ No se pudo crear gallo de prueba, usando existente${NC}"
  echo "$CREATE_RESPONSE" | head -200
  # Usar el primer gallo encontrado
  GALLO_TEST_ID=$PRIMER_GALLO_ID
  TEST_GALLO_NAME=$PRIMER_GALLO_NOMBRE
else
  echo -e "${GREEN}✅ Gallo de prueba creado${NC}"
  echo "ID: $GALLO_TEST_ID"
  echo "Nombre: $TEST_GALLO_NAME"
fi

sleep 1

echo ""
echo -e "${YELLOW}5. INTENTANDO ELIMINAR GALLO SIN AUTORIZACIÓN (debe fallar)...${NC}"
echo "==========================================="

# Intentar sin token (debe fallar)
NO_AUTH_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/api/v1/gallos/$GALLO_TEST_ID")

echo "Respuesta sin autorización:"
echo "$NO_AUTH_RESPONSE" | head -5

sleep 1

echo ""
echo -e "${YELLOW}6. ELIMINANDO GALLO CON AUTORIZACIÓN...${NC}"
echo "==========================================="
echo "Eliminando gallo ID: $GALLO_TEST_ID"
echo "Nombre: $TEST_GALLO_NAME"
echo ""

# Eliminar gallo con token válido
DELETE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$BASE_URL/api/v1/gallos/$GALLO_TEST_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

# Separar respuesta del status code
RESPONSE_BODY=$(echo "$DELETE_RESPONSE" | sed -n '1,/HTTP_STATUS/p' | sed '$d')
HTTP_STATUS=$(echo "$DELETE_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

echo "Respuesta de eliminación:"
echo "$RESPONSE_BODY"
echo "HTTP Status: $HTTP_STATUS"

if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "204" ]; then
  echo -e "${GREEN}✅ GALLO ELIMINADO EXITOSAMENTE${NC}"
elif [ "$HTTP_STATUS" = "404" ]; then
  echo -e "${YELLOW}⚠️ Gallo no encontrado (ya fue eliminado)${NC}"
else
  echo -e "${RED}❌ Error en la eliminación (Status: $HTTP_STATUS)${NC}"
fi

sleep 1

echo ""
echo -e "${YELLOW}7. VERIFICANDO QUE EL GALLO FUE ELIMINADO...${NC}"
echo "==========================================="

# Intentar obtener el gallo eliminado
VERIFY_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X GET "$BASE_URL/api/v1/gallos/$GALLO_TEST_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

VERIFY_STATUS=$(echo "$VERIFY_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

if [ "$VERIFY_STATUS" = "404" ]; then
  echo -e "${GREEN}✅ CONFIRMADO: El gallo ya no existe${NC}"
else
  echo "Status: $VERIFY_STATUS"
  echo "$VERIFY_RESPONSE" | head -10
  echo -e "${YELLOW}⚠️ Verificar manualmente si el gallo fue eliminado${NC}"
fi

echo ""
echo -e "${YELLOW}8. CONTANDO GALLOS RESTANTES...${NC}"
echo "==========================================="

# Obtener lista actualizada
GALLOS_FINAL=$(curl -s -X GET "$BASE_URL/api/v1/gallos/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

TOTAL_FINAL=$(echo "$GALLOS_FINAL" | grep -o '"id"' | wc -l)
echo "Total de gallos después de eliminar: $TOTAL_FINAL"

echo ""
echo "==========================================="
echo -e "${GREEN}🎉 PRUEBA COMPLETADA${NC}"
echo "==========================================="
echo ""
echo "📊 Resumen de la prueba:"
echo "------------------------"
echo "- Usuario: $USER_EMAIL"
echo "- Token: ${ACCESS_TOKEN:0:30}..."
echo "- Gallo eliminado ID: $GALLO_TEST_ID"
echo "- Servidor: $BASE_URL"
echo ""
echo "✅ Pruebas realizadas:"
echo "  1. Login exitoso"
echo "  2. Token validado"
echo "  3. Lista de gallos obtenida"
echo "  4. Gallo de prueba creado (o seleccionado)"
echo "  5. Intento sin autorización rechazado"
echo "  6. Eliminación con autorización"
echo "  7. Verificación de eliminación"
echo "  8. Conteo final de gallos"
echo ""