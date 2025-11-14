-- INSERTAR TOKEN FCM DIRECTAMENTE PARA PROBAR
-- Usuario: alancairampoma@gmail.com (ID: 25)

INSERT INTO fcm_tokens (
    user_id,
    fcm_token,
    platform,
    device_info,
    is_active,
    created_at,
    updated_at
) VALUES (
    25,
    'TEST_FCM_TOKEN_' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS'),
    'android',
    'Test Manual desde SQL',
    true,
    NOW(),
    NOW()
) ON CONFLICT (fcm_token) DO UPDATE SET
    user_id = 25,
    is_active = true,
    updated_at = NOW()
RETURNING *;