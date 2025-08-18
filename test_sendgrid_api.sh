#!/bin/bash

echo "🧪 TESTING SENDGRID EMAILS - CASTA DE GALLOS"
echo "=============================================="

# Variables
BASE_URL="https://gallerappback-production.up.railway.app"
EMAIL="alancairampoma@gmail.com"
PASSWORD="M@tias252610"

echo "📍 Testing URL: $BASE_URL"
echo "👤 Email: $EMAIL"
echo ""

# 1. Health Check
echo "🏥 1. HEALTH CHECK"
echo "curl $BASE_URL/"
curl "$BASE_URL/" -w "\nStatus: %{http_code}\n" || echo "❌ Health check failed"
echo ""

# 2. Login
echo "🔑 2. LOGIN"
echo "curl -X POST $BASE_URL/auth/login"
LOGIN_RESPONSE=$(curl -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" \
  -w "\nStatus: %{http_code}\n" 2>/dev/null)

echo "$LOGIN_RESPONSE"

# Extraer token si existe
TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ ! -z "$TOKEN" ]; then
    echo "✅ Token obtenido: ${TOKEN:0:20}..."
    echo ""
    
    # 3. Test Forgot Password
    echo "📧 3. FORGOT PASSWORD"
    echo "curl -X POST $BASE_URL/auth/forgot-password"
    curl -X POST "$BASE_URL/auth/forgot-password" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d "{\"email\": \"$EMAIL\"}" \
      -w "\nStatus: %{http_code}\n"
    echo ""
    
else
    echo "❌ No se pudo obtener token"
    echo ""
    
    # Test sin autenticación
    echo "📧 3. FORGOT PASSWORD (sin auth)"
    echo "curl -X POST $BASE_URL/auth/forgot-password"
    curl -X POST "$BASE_URL/auth/forgot-password" \
      -H "Content-Type: application/json" \
      -d "{\"email\": \"$EMAIL\"}" \
      -w "\nStatus: %{http_code}\n"
    echo ""
fi

echo "🏁 Test completed!"
