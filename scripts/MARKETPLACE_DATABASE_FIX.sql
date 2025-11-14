-- 🔧 MARKETPLACE DATABASE FIX - Ejecutar PRIMERO
-- Este script corrige la estructura antes de insertar datos

-- ========================================
-- 1. VERIFICAR Y CREAR TABLAS MARKETPLACE
-- ========================================

-- Crear tabla marketplace_publicaciones si no existe
CREATE TABLE IF NOT EXISTS public.marketplace_publicaciones (
    id serial4 NOT NULL,
    user_id int4 NOT NULL,
    gallo_id int4 NOT NULL,
    precio numeric(10, 2) NOT NULL,
    estado varchar(50) DEFAULT 'venta'::character varying NOT NULL,
    fecha_publicacion timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    icono_ejemplo varchar(100) DEFAULT '🐓'::character varying,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_by int4 NOT NULL,
    CONSTRAINT marketplace_publicaciones_pkey PRIMARY KEY (id)
);

-- Crear tabla marketplace_favoritos si no existe
CREATE TABLE IF NOT EXISTS public.marketplace_favoritos (
    id serial4 NOT NULL,
    user_id int4 NOT NULL,
    publicacion_id int4 NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT marketplace_favoritos_pkey PRIMARY KEY (id)
);

-- ========================================
-- 2. AGREGAR FOREIGN KEYS SI NO EXISTEN
-- ========================================

-- FK marketplace_publicaciones -> users
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_marketplace_user'
    ) THEN
        ALTER TABLE marketplace_publicaciones
        ADD CONSTRAINT fk_marketplace_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- FK marketplace_publicaciones -> gallos
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_marketplace_gallo'
    ) THEN
        ALTER TABLE marketplace_publicaciones
        ADD CONSTRAINT fk_marketplace_gallo
        FOREIGN KEY (gallo_id) REFERENCES gallos(id) ON DELETE CASCADE;
    END IF;
END $$;

-- FK marketplace_favoritos -> users
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_favoritos_user'
    ) THEN
        ALTER TABLE marketplace_favoritos
        ADD CONSTRAINT fk_favoritos_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- FK marketplace_favoritos -> marketplace_publicaciones
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_favoritos_publicacion'
    ) THEN
        ALTER TABLE marketplace_favoritos
        ADD CONSTRAINT fk_favoritos_publicacion
        FOREIGN KEY (publicacion_id) REFERENCES marketplace_publicaciones(id) ON DELETE CASCADE;
    END IF;
END $$;

-- ========================================
-- 3. AGREGAR COLUMNAS FALTANTES
-- ========================================

-- Agregar marketplace_publicaciones_max a suscripciones
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'suscripciones'
        AND column_name = 'marketplace_publicaciones_max'
    ) THEN
        ALTER TABLE suscripciones
        ADD COLUMN marketplace_publicaciones_max int4 DEFAULT 0 NOT NULL;

        -- Actualizar valores por defecto según plan
        UPDATE suscripciones
        SET marketplace_publicaciones_max = CASE
            WHEN plan_type = 'gratuito' THEN 0
            WHEN plan_type = 'basico' THEN 3
            WHEN plan_type = 'premium' THEN 5
            WHEN plan_type = 'profesional' THEN 10
            ELSE 0
        END;
    END IF;
END $$;

-- Agregar fotos_adicionales a gallos si no existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'gallos'
        AND column_name = 'fotos_adicionales'
    ) THEN
        ALTER TABLE gallos
        ADD COLUMN fotos_adicionales jsonb DEFAULT '[]'::jsonb;
    END IF;
END $$;

-- ========================================
-- 4. CREAR ÍNDICES PARA PERFORMANCE
-- ========================================

-- Índices para marketplace_publicaciones
CREATE INDEX IF NOT EXISTS idx_marketplace_user_id ON marketplace_publicaciones(user_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_gallo_id ON marketplace_publicaciones(gallo_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_estado ON marketplace_publicaciones(estado);
CREATE INDEX IF NOT EXISTS idx_marketplace_precio ON marketplace_publicaciones(precio);
CREATE INDEX IF NOT EXISTS idx_marketplace_fecha ON marketplace_publicaciones(fecha_publicacion DESC);

-- Índices para marketplace_favoritos
CREATE INDEX IF NOT EXISTS idx_favoritos_user_id ON marketplace_favoritos(user_id);
CREATE INDEX IF NOT EXISTS idx_favoritos_publicacion_id ON marketplace_favoritos(publicacion_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_favoritos_unique ON marketplace_favoritos(user_id, publicacion_id);

-- ========================================
-- 5. VERIFICAR ESTRUCTURA CREADA
-- ========================================

-- Verificar tablas creadas
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columnas
FROM information_schema.tables t
WHERE t.table_name IN ('marketplace_publicaciones', 'marketplace_favoritos')
AND t.table_schema = 'public';

-- Verificar columna marketplace_publicaciones_max
SELECT
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'suscripciones'
AND column_name = 'marketplace_publicaciones_max';

-- Verificar columna fotos_adicionales
SELECT
    column_name,
    data_type,
    column_default
FROM information_schema.columns
WHERE table_name = 'gallos'
AND column_name = 'fotos_adicionales';

-- Verificar foreign keys
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_name LIKE 'marketplace_%';

-- ¡ESTRUCTURA LISTA! Ahora ejecutar API_MARKETPLACE_TEST_DATA.sql