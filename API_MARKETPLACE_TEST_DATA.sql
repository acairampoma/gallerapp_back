-- 🛒 MARKETPLACE TEST DATA - Datos de Prueba
-- Ejecutar estos comandos en orden para crear data de prueba

-- ========================================
-- 1. ACTUALIZAR USUARIOS A PREMIUM
-- ========================================
-- Actualizar algunos usuarios para que puedan publicar
UPDATE users
SET is_premium = true
WHERE id IN (27, 62, 65, 68, 49);

-- ========================================
-- 2. ACTUALIZAR SUSCRIPCIONES CON LÍMITES MARKETPLACE
-- ========================================
-- Actualizar suscripciones existentes para incluir límites marketplace
UPDATE suscripciones
SET marketplace_publicaciones_max = 5,
    plan_type = 'premium',
    plan_name = 'Plan Premium'
WHERE user_id IN (27, 62, 65, 68, 49);

-- ========================================
-- 3. ACTUALIZAR GALLOS CON FOTOS ADICIONALES
-- ========================================
-- Agregar fotos en formato JSON a algunos gallos
UPDATE gallos
SET fotos_adicionales = '[
    {"url": "https://res.cloudinary.com/demo/image/upload/gallo1.jpg", "public_id": "gallo1", "order": 1},
    {"url": "https://res.cloudinary.com/demo/image/upload/gallo1_2.jpg", "public_id": "gallo1_2", "order": 2}
]'::jsonb
WHERE id IN (213, 214, 215);

UPDATE gallos
SET fotos_adicionales = '[
    {"url": "https://res.cloudinary.com/demo/image/upload/gallo2.jpg", "public_id": "gallo2", "order": 1},
    {"url": "https://res.cloudinary.com/demo/image/upload/gallo2_2.jpg", "public_id": "gallo2_2", "order": 2},
    {"url": "https://res.cloudinary.com/demo/image/upload/gallo2_3.jpg", "public_id": "gallo2_3", "order": 3}
]'::jsonb
WHERE id IN (212, 210, 209);

-- ========================================
-- 4. INSERTAR PUBLICACIONES MARKETPLACE
-- ========================================

-- Publicaciones del usuario 27 (3 gallos)
INSERT INTO marketplace_publicaciones
(user_id, gallo_id, precio, estado, fecha_publicacion, icono_ejemplo, created_by, updated_by)
VALUES
-- Vraem - Usuario 27, Gallo 213
(27, 213, 450.00, 'venta', '2025-09-24 21:30:00', '🐓', 27, 27),
-- Trueno - Usuario 27, Gallo 214
(27, 214, 380.50, 'venta', '2025-09-24 21:35:00', '⚡', 27, 27),
-- Reyna del sur - Usuario 27, Gallo 215
(27, 215, 520.75, 'pausado', '2025-09-24 21:40:00', '👑', 27, 27);

-- Publicaciones del usuario 62 (2 gallos)
INSERT INTO marketplace_publicaciones
(user_id, gallo_id, precio, estado, fecha_publicacion, icono_ejemplo, created_by, updated_by)
VALUES
-- Ralito - Usuario 62, Gallo 209
(62, 209, 320.00, 'venta', '2025-09-24 08:15:00', '🏃', 62, 62),
-- Israel Morales - Usuario 62, Gallo 208
(62, 208, 275.50, 'venta', '2025-09-24 08:20:00', '🥊', 62, 62);

-- Publicaciones del usuario 65 (1 gallo)
INSERT INTO marketplace_publicaciones
(user_id, gallo_id, precio, estado, fecha_publicacion, icono_ejemplo, created_by, updated_by)
VALUES
-- EL RAYO - Usuario 65, Gallo 210
(65, 210, 420.00, 'venta', '2025-09-24 10:00:00', '⚡', 65, 65);

-- Publicaciones del usuario 68 (1 gallo)
INSERT INTO marketplace_publicaciones
(user_id, gallo_id, precio, estado, fecha_publicacion, icono_ejemplo, created_by, updated_by)
VALUES
-- el primero - Usuario 68, Gallo 212
(68, 212, 350.00, 'venta', '2025-09-24 12:00:00', '🥇', 68, 68);

-- Publicación vendida (para testing)
INSERT INTO marketplace_publicaciones
(user_id, gallo_id, precio, estado, fecha_publicacion, icono_ejemplo, created_by, updated_by)
VALUES
-- Claudio - Usuario 49, Gallo 204 (VENDIDO)
(49, 204, 290.00, 'vendido', '2025-09-20 14:30:00', '🏆', 49, 49);

-- ========================================
-- 5. INSERTAR FAVORITOS
-- ========================================

-- Usuario 68 marca como favoritos publicaciones de otros usuarios
INSERT INTO marketplace_favoritos (user_id, publicacion_id)
VALUES
(68, 1), -- Vraem
(68, 2), -- Trueno
(68, 4); -- Ralito

-- Usuario 62 marca como favoritos
INSERT INTO marketplace_favoritos (user_id, publicacion_id)
VALUES
(62, 1), -- Vraem
(62, 6); -- EL RAYO

-- Usuario 27 marca como favoritos
INSERT INTO marketplace_favoritos (user_id, publicacion_id)
VALUES
(27, 6), -- EL RAYO
(27, 7); -- el primero

-- ========================================
-- 6. VERIFICAR DATA INSERTADA
-- ========================================

-- Verificar publicaciones con JOIN
SELECT
    mp.id,
    mp.precio,
    mp.estado,
    mp.fecha_publicacion,
    g.nombre as gallo_nombre,
    g.codigo_identificacion,
    u.email as vendedor_email,
    (SELECT COUNT(*) FROM marketplace_favoritos WHERE publicacion_id = mp.id) as total_favoritos
FROM marketplace_publicaciones mp
JOIN gallos g ON mp.gallo_id = g.id
JOIN users u ON mp.user_id = u.id
ORDER BY mp.fecha_publicacion DESC;

-- Verificar favoritos
SELECT
    mf.id,
    u.email as usuario_email,
    mp.precio,
    g.nombre as gallo_nombre
FROM marketplace_favoritos mf
JOIN marketplace_publicaciones mp ON mf.publicacion_id = mp.id
JOIN gallos g ON mp.gallo_id = g.id
JOIN users u ON mf.user_id = u.id
ORDER BY mf.created_at DESC;

-- Verificar límites de usuario
SELECT
    u.id,
    u.email,
    s.plan_type,
    s.marketplace_publicaciones_max,
    (SELECT COUNT(*)
     FROM marketplace_publicaciones
     WHERE user_id = u.id AND estado IN ('venta', 'pausado')) as publicaciones_activas
FROM users u
JOIN suscripciones s ON u.id = s.user_id
WHERE u.id IN (27, 62, 65, 68, 49)
ORDER BY u.id;