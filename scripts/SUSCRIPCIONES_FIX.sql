-- 🔧 FIX SUSCRIPCIONES - Agregar columna marketplace_publicaciones_max
-- Este es el script correcto para arreglar el error

-- ========================================
-- 1. AGREGAR COLUMNA FALTANTE A SUSCRIPCIONES
-- ========================================

-- Agregar marketplace_publicaciones_max a tabla suscripciones
ALTER TABLE public.suscripciones
ADD COLUMN IF NOT EXISTS marketplace_publicaciones_max int4 DEFAULT 0 NOT NULL;

-- ========================================
-- 2. ACTUALIZAR VALORES SEGÚN PLAN ACTUAL
-- ========================================

-- Actualizar marketplace_publicaciones_max basado en el plan_type actual
UPDATE public.suscripciones
SET marketplace_publicaciones_max = CASE
    WHEN plan_type = 'gratuito' THEN 0
    WHEN plan_type = 'basico' THEN 3
    WHEN plan_type = 'premium' THEN 5
    WHEN plan_type = 'profesional' THEN 10
    ELSE 0
END;

-- ========================================
-- 3. VERIFICAR ESTRUCTURA ACTUALIZADA
-- ========================================

-- Verificar que la columna fue agregada
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_name = 'suscripciones'
AND column_name = 'marketplace_publicaciones_max';

-- Ver algunos registros actualizados
SELECT
    id,
    user_id,
    plan_type,
    plan_name,
    gallos_maximo,
    marketplace_publicaciones_max
FROM public.suscripciones
ORDER BY updated_at DESC
LIMIT 5;

-- ========================================
-- 4. CREAR TABLAS MARKETPLACE SI NO EXISTEN
-- ========================================

-- Crear tabla marketplace_publicaciones
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

-- Crear tabla marketplace_favoritos
CREATE TABLE IF NOT EXISTS public.marketplace_favoritos (
    id serial4 NOT NULL,
    user_id int4 NOT NULL,
    publicacion_id int4 NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT marketplace_favoritos_pkey PRIMARY KEY (id)
);

-- ========================================
-- 5. AGREGAR FOREIGN KEYS
-- ========================================

-- FK marketplace_publicaciones -> users
ALTER TABLE public.marketplace_publicaciones
ADD CONSTRAINT IF NOT EXISTS fk_marketplace_user
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- FK marketplace_publicaciones -> gallos
ALTER TABLE public.marketplace_publicaciones
ADD CONSTRAINT IF NOT EXISTS fk_marketplace_gallo
FOREIGN KEY (gallo_id) REFERENCES public.gallos(id) ON DELETE CASCADE;

-- FK marketplace_favoritos -> users
ALTER TABLE public.marketplace_favoritos
ADD CONSTRAINT IF NOT EXISTS fk_favoritos_user
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- FK marketplace_favoritos -> marketplace_publicaciones
ALTER TABLE public.marketplace_favoritos
ADD CONSTRAINT IF NOT EXISTS fk_favoritos_publicacion
FOREIGN KEY (publicacion_id) REFERENCES public.marketplace_publicaciones(id) ON DELETE CASCADE;

-- ========================================
-- 6. AGREGAR COLUMNA FOTOS A GALLOS
-- ========================================

-- Agregar fotos_adicionales a gallos si no existe
ALTER TABLE public.gallos
ADD COLUMN IF NOT EXISTS fotos_adicionales jsonb DEFAULT '[]'::jsonb;

-- ========================================
-- 7. CREAR ÍNDICES
-- ========================================

-- Índices para marketplace_publicaciones
CREATE INDEX IF NOT EXISTS idx_marketplace_user_id ON public.marketplace_publicaciones(user_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_gallo_id ON public.marketplace_publicaciones(gallo_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_estado ON public.marketplace_publicaciones(estado);
CREATE INDEX IF NOT EXISTS idx_marketplace_precio ON public.marketplace_publicaciones(precio);

-- Índices para marketplace_favoritos
CREATE INDEX IF NOT EXISTS idx_favoritos_user_id ON public.marketplace_favoritos(user_id);
CREATE INDEX IF NOT EXISTS idx_favoritos_publicacion_id ON public.marketplace_favoritos(publicacion_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_favoritos_unique ON public.marketplace_favoritos(user_id, publicacion_id);

-- ========================================
-- RESULTADO FINAL
-- ========================================
SELECT '✅ ESTRUCTURA MARKETPLACE CREADA CORRECTAMENTE' as status;