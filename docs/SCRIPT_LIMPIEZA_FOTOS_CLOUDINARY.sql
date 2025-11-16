-- ============================================================================
-- SCRIPT: Limpieza de Fotos de Cloudinary Antiguas
-- Fecha: 2025-11-16
-- Propósito: Eliminar fotos de Cloudinary para forzar uso de ImageKit
-- ============================================================================

-- PASO 1: Ver gallos afectados (SOLO LECTURA)
-- ============================================================================
SELECT 
    id,
    nombre,
    codigo_identificacion,
    foto_principal_url,
    CASE 
        WHEN foto_principal_url LIKE '%cloudinary%' THEN '🔴 CLOUDINARY'
        WHEN foto_principal_url LIKE '%imagekit%' THEN '🟢 IMAGEKIT'
        ELSE '⚪ SIN_FOTO'
    END as tipo_foto,
    created_at,
    updated_at
FROM gallos 
WHERE user_id = (SELECT id FROM users WHERE email = 'alancairampoma@gmail.com')
  AND foto_principal_url LIKE '%cloudinary%'
ORDER BY id;

-- Resultado esperado: 3 gallos (IDs: 143, 146, 227)


-- PASO 2: Backup de datos antes de limpiar (RECOMENDADO)
-- ============================================================================
CREATE TABLE IF NOT EXISTS gallos_fotos_backup_20251116 AS
SELECT 
    id,
    nombre,
    codigo_identificacion,
    foto_principal_url,
    url_foto_cloudinary,
    fotos_adicionales,
    updated_at,
    CURRENT_TIMESTAMP as backup_at
FROM gallos 
WHERE user_id = (SELECT id FROM users WHERE email = 'alancairampoma@gmail.com')
  AND foto_principal_url LIKE '%cloudinary%';

-- Verificar backup
SELECT COUNT(*) as registros_backup FROM gallos_fotos_backup_20251116;


-- PASO 3: Limpiar fotos de Cloudinary (EJECUTAR CON CUIDADO)
-- ============================================================================
UPDATE gallos 
SET foto_principal_url = NULL,
    url_foto_cloudinary = NULL,
    fotos_adicionales = NULL,
    updated_at = CURRENT_TIMESTAMP
WHERE user_id = (SELECT id FROM users WHERE email = 'alancairampoma@gmail.com')
  AND foto_principal_url LIKE '%cloudinary%';

-- Resultado esperado: UPDATE 3


-- PASO 4: Verificar limpieza
-- ============================================================================
SELECT 
    id,
    nombre,
    codigo_identificacion,
    foto_principal_url,
    url_foto_cloudinary,
    fotos_adicionales,
    updated_at
FROM gallos 
WHERE id IN (143, 146, 227);

-- Resultado esperado: Todos los campos de fotos en NULL


-- PASO 5: Ver estado final de todos los gallos del usuario
-- ============================================================================
SELECT 
    id,
    nombre,
    CASE 
        WHEN foto_principal_url LIKE '%cloudinary%' THEN '🔴 CLOUDINARY'
        WHEN foto_principal_url LIKE '%imagekit%' THEN '🟢 IMAGEKIT'
        WHEN foto_principal_url IS NULL THEN '⚪ SIN_FOTO'
        ELSE '❓ OTRO'
    END as tipo_foto,
    foto_principal_url,
    updated_at
FROM gallos 
WHERE user_id = (SELECT id FROM users WHERE email = 'alancairampoma@gmail.com')
ORDER BY updated_at DESC
LIMIT 10;


-- ============================================================================
-- ROLLBACK (Si algo sale mal)
-- ============================================================================
-- SOLO SI NECESITAS RESTAURAR:
/*
UPDATE gallos g
SET foto_principal_url = b.foto_principal_url,
    url_foto_cloudinary = b.url_foto_cloudinary,
    fotos_adicionales = b.fotos_adicionales
FROM gallos_fotos_backup_20251116 b
WHERE g.id = b.id;
*/


-- ============================================================================
-- ESTADÍSTICAS FINALES
-- ============================================================================
SELECT 
    'Total gallos' as metrica,
    COUNT(*) as valor
FROM gallos 
WHERE user_id = (SELECT id FROM users WHERE email = 'alancairampoma@gmail.com')

UNION ALL

SELECT 
    'Con fotos ImageKit' as metrica,
    COUNT(*) as valor
FROM gallos 
WHERE user_id = (SELECT id FROM users WHERE email = 'alancairampoma@gmail.com')
  AND foto_principal_url LIKE '%imagekit%'

UNION ALL

SELECT 
    'Sin fotos' as metrica,
    COUNT(*) as valor
FROM gallos 
WHERE user_id = (SELECT id FROM users WHERE email = 'alancairampoma@gmail.com')
  AND foto_principal_url IS NULL

UNION ALL

SELECT 
    'Con fotos Cloudinary (debe ser 0)' as metrica,
    COUNT(*) as valor
FROM gallos 
WHERE user_id = (SELECT id FROM users WHERE email = 'alancairampoma@gmail.com')
  AND foto_principal_url LIKE '%cloudinary%';


-- ============================================================================
-- NOTAS IMPORTANTES
-- ============================================================================
-- 1. Este script limpia SOLO los gallos del usuario alancairampoma@gmail.com
-- 2. Las fotos siguen existiendo en Cloudinary, solo se eliminan las referencias
-- 3. Los usuarios tendrán que subir fotos nuevas con ImageKit
-- 4. Se crea un backup automático antes de limpiar
-- 5. Si algo sale mal, usar el ROLLBACK de arriba

-- ============================================================================
-- INSTRUCCIONES DE USO
-- ============================================================================
-- 1. Conectar a la base de datos:
--    psql -h localhost -U postgres -d galloapp
--
-- 2. Ejecutar PASO 1 para ver gallos afectados
--
-- 3. Ejecutar PASO 2 para crear backup
--
-- 4. Ejecutar PASO 3 para limpiar (CUIDADO)
--
-- 5. Ejecutar PASO 4 y 5 para verificar
--
-- 6. Probar en frontend que ahora pide subir fotos nuevas
