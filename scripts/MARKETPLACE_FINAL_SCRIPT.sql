-- 🔧 MARKETPLACE FINAL SCRIPT - Compatible con PostgreSQL
-- Sin usar IF NOT EXISTS en ALTER TABLE para evitar errores de sintaxis

-- ========================================
-- 1. CREAR TABLAS MARKETPLACE
-- ========================================

-- Crear tabla marketplace_publicaciones
CREATE TABLE IF NOT EXISTS public.marketplace_publicaciones (
    id serial4 NOT NULL,
    user_id int4 NOT NULL,
    gallo_id int4 NOT NULL,
    precio numeric(10, 2) NOT NULL,
    estado varchar(50) DEFAULT 'venta' NOT NULL,
    fecha_publicacion timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    icono_ejemplo varchar(100) DEFAULT '🐓',
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_by int4 NOT NULL,
    CONSTRAINT marketplace_publicaciones_pkey PRIMARY KEY (id)
);

-- Crear tabla marketplace_favoritos
CREATE TABLE IF NOT EXISTS public.marketplace_favoritos (
    id serial4 NOT NULL,
    user_id int4 NOT NULL,
    publicacion_id int4 NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT marketplace_favoritos_pkey PRIMARY KEY (id)
);

-- ========================================
-- 2. AGREGAR COLUMNA FOTOS A GALLOS (con verificación manual)
-- ========================================

-- Verificar si la columna ya existe antes de agregarla
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'gallos'
        AND column_name = 'fotos_adicionales'
    ) THEN
        ALTER TABLE public.gallos ADD COLUMN fotos_adicionales jsonb DEFAULT '[]'::jsonb;
    END IF;
END $$;

-- ========================================
-- 3. CREAR FOREIGN KEYS (con verificación manual)
-- ========================================

-- FK marketplace_publicaciones -> users
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_marketplace_user'
    ) THEN
        ALTER TABLE public.marketplace_publicaciones
        ADD CONSTRAINT fk_marketplace_user
        FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- FK marketplace_publicaciones -> gallos
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_marketplace_gallo'
    ) THEN
        ALTER TABLE public.marketplace_publicaciones
        ADD CONSTRAINT fk_marketplace_gallo
        FOREIGN KEY (gallo_id) REFERENCES public.gallos(id) ON DELETE CASCADE;
    END IF;
END $$;

-- FK marketplace_favoritos -> users
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_favoritos_user'
    ) THEN
        ALTER TABLE public.marketplace_favoritos
        ADD CONSTRAINT fk_favoritos_user
        FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- FK marketplace_favoritos -> marketplace_publicaciones
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_favoritos_publicacion'
    ) THEN
        ALTER TABLE public.marketplace_favoritos
        ADD CONSTRAINT fk_favoritos_publicacion
        FOREIGN KEY (publicacion_id) REFERENCES public.marketplace_publicaciones(id) ON DELETE CASCADE;
    END IF;
END $$;

-- ========================================
-- 4. CREAR ÍNDICES (con verificación manual)
-- ========================================

-- Índices para marketplace_publicaciones
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_marketplace_user_id') THEN
        CREATE INDEX idx_marketplace_user_id ON public.marketplace_publicaciones(user_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_marketplace_gallo_id') THEN
        CREATE INDEX idx_marketplace_gallo_id ON public.marketplace_publicaciones(gallo_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_marketplace_estado') THEN
        CREATE INDEX idx_marketplace_estado ON public.marketplace_publicaciones(estado);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_marketplace_precio') THEN
        CREATE INDEX idx_marketplace_precio ON public.marketplace_publicaciones(precio);
    END IF;
END $$;

-- Índices para marketplace_favoritos
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_favoritos_user_id') THEN
        CREATE INDEX idx_favoritos_user_id ON public.marketplace_favoritos(user_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_favoritos_publicacion_id') THEN
        CREATE INDEX idx_favoritos_publicacion_id ON public.marketplace_favoritos(publicacion_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_favoritos_unique') THEN
        CREATE UNIQUE INDEX idx_favoritos_unique ON public.marketplace_favoritos(user_id, publicacion_id);
    END IF;
END $$;

-- ========================================
-- 5. INSERTAR DATOS DE PRUEBA
-- ========================================

-- Actualizar algunos usuarios a premium para testing
UPDATE public.users
SET is_premium = true
WHERE id IN (27, 62, 65, 68, 49);

-- Actualizar gallos con fotos de ejemplo
UPDATE public.gallos
SET fotos_adicionales = '[
    {"url": "https://res.cloudinary.com/demo/image/upload/gallo1.jpg", "public_id": "gallo1", "order": 1},
    {"url": "https://res.cloudinary.com/demo/image/upload/gallo1_2.jpg", "public_id": "gallo1_2", "order": 2}
]'::jsonb
WHERE id IN (213, 214, 215, 212, 210);

-- Insertar publicaciones marketplace de prueba
INSERT INTO public.marketplace_publicaciones
(user_id, gallo_id, precio, estado, fecha_publicacion, icono_ejemplo, created_by, updated_by)
VALUES
-- Usuario 27
(27, 213, 450.00, 'venta', CURRENT_TIMESTAMP - INTERVAL '1 day', '🐓', 27, 27),
(27, 214, 380.50, 'venta', CURRENT_TIMESTAMP - INTERVAL '2 hours', '⚡', 27, 27),
(27, 215, 520.75, 'pausado', CURRENT_TIMESTAMP - INTERVAL '30 minutes', '👑', 27, 27),

-- Usuario 62
(62, 209, 320.00, 'venta', CURRENT_TIMESTAMP - INTERVAL '3 hours', '🏃', 62, 62),
(62, 208, 275.50, 'venta', CURRENT_TIMESTAMP - INTERVAL '1 hour', '🥊', 62, 62),

-- Usuario 65
(65, 210, 420.00, 'venta', CURRENT_TIMESTAMP - INTERVAL '45 minutes', '⚡', 65, 65),

-- Usuario 68
(68, 212, 350.00, 'venta', CURRENT_TIMESTAMP - INTERVAL '15 minutes', '🥇', 68, 68)

ON CONFLICT DO NOTHING;

-- Insertar favoritos de prueba
INSERT INTO public.marketplace_favoritos (user_id, publicacion_id)
VALUES
-- Usuario 68 marca favoritos
(68, 1), (68, 2), (68, 4),
-- Usuario 62 marca favoritos
(62, 1), (62, 6),
-- Usuario 27 marca favoritos
(27, 6), (27, 7)
ON CONFLICT DO NOTHING;

-- ========================================
-- 6. VERIFICACIONES FINALES
-- ========================================

-- Verificar tablas creadas
SELECT
    'marketplace_publicaciones' as tabla,
    COUNT(*) as registros
FROM public.marketplace_publicaciones

UNION ALL

SELECT
    'marketplace_favoritos' as tabla,
    COUNT(*) as registros
FROM public.marketplace_favoritos

UNION ALL

SELECT
    'gallos_con_fotos' as tabla,
    COUNT(*) as registros
FROM public.gallos
WHERE fotos_adicionales IS NOT NULL AND fotos_adicionales != '[]'::jsonb;

-- Verificar JOIN entre suscripciones y planes_catalogo para marketplace
SELECT
    s.user_id,
    s.plan_type,
    pc.marketplace_publicaciones_max as limite,
    COUNT(mp.id) as publicaciones_activas,
    (pc.marketplace_publicaciones_max - COUNT(mp.id)) as disponibles
FROM public.suscripciones s
JOIN public.planes_catalogo pc ON s.plan_type = pc.codigo
LEFT JOIN public.marketplace_publicaciones mp ON s.user_id = mp.user_id
    AND mp.estado IN ('venta', 'pausado')
WHERE s.status = 'active'
AND s.user_id IN (27, 62, 65, 68)
GROUP BY s.user_id, s.plan_type, pc.marketplace_publicaciones_max
ORDER BY s.user_id;

-- Mostrar resultado final
SELECT '🚀 MARKETPLACE COMPLETAMENTE CONFIGURADO!' as resultado;