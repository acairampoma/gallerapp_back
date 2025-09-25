-- 🔧 SUSCRIPCIONES NORMALIZED - Mejor diseño sin duplicar datos
-- Usamos JOIN con planes_catalogo en lugar de duplicar el campo

-- ========================================
-- 1. CREAR TABLAS MARKETPLACE ÚNICAMENTE
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
-- 2. FOREIGN KEYS
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
-- 3. AGREGAR FOTOS A GALLOS
-- ========================================

-- Agregar fotos_adicionales a gallos si no existe
ALTER TABLE public.gallos
ADD COLUMN IF NOT EXISTS fotos_adicionales jsonb DEFAULT '[]'::jsonb;

-- ========================================
-- 4. ÍNDICES PARA PERFORMANCE
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
-- 5. FUNCIÓN PARA OBTENER LÍMITES MARKETPLACE
-- ========================================

-- Función que obtiene el límite marketplace desde planes_catalogo via JOIN
CREATE OR REPLACE FUNCTION get_user_marketplace_limit(p_user_id INT)
RETURNS INT AS $$
DECLARE
    marketplace_limit INT DEFAULT 0;
BEGIN
    -- JOIN entre suscripciones y planes_catalogo
    SELECT pc.marketplace_publicaciones_max
    INTO marketplace_limit
    FROM public.suscripciones s
    JOIN public.planes_catalogo pc ON s.plan_type = pc.codigo
    WHERE s.user_id = p_user_id
    AND s.status = 'active'
    LIMIT 1;

    RETURN COALESCE(marketplace_limit, 0);
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- 6. FUNCIÓN PARA CONTAR PUBLICACIONES ACTIVAS
-- ========================================

-- Función que cuenta publicaciones activas del usuario
CREATE OR REPLACE FUNCTION count_user_active_publications(p_user_id INT)
RETURNS INT AS $$
DECLARE
    active_count INT DEFAULT 0;
BEGIN
    SELECT COUNT(*)
    INTO active_count
    FROM public.marketplace_publicaciones
    WHERE user_id = p_user_id
    AND estado IN ('venta', 'pausado');

    RETURN COALESCE(active_count, 0);
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- 7. VISTA PARA LÍMITES DE USUARIO
-- ========================================

-- Vista que une suscripciones con planes_catalogo para obtener límites
CREATE OR REPLACE VIEW v_user_marketplace_limits AS
SELECT
    s.user_id,
    s.plan_type,
    s.plan_name,
    pc.marketplace_publicaciones_max as limite_publicaciones,
    count_user_active_publications(s.user_id) as publicaciones_activas,
    (pc.marketplace_publicaciones_max - count_user_active_publications(s.user_id)) as publicaciones_disponibles,
    CASE
        WHEN count_user_active_publications(s.user_id) < pc.marketplace_publicaciones_max THEN true
        ELSE false
    END as puede_publicar
FROM public.suscripciones s
JOIN public.planes_catalogo pc ON s.plan_type = pc.codigo
WHERE s.status = 'active';

-- ========================================
-- 8. VERIFICACIÓN DEL DISEÑO NORMALIZADO
-- ========================================

-- Test: Verificar que podemos obtener límites via JOIN
SELECT
    s.user_id,
    s.plan_type,
    s.plan_name,
    pc.marketplace_publicaciones_max as limite_desde_catalogo,
    get_user_marketplace_limit(s.user_id) as limite_desde_funcion
FROM public.suscripciones s
JOIN public.planes_catalogo pc ON s.plan_type = pc.codigo
WHERE s.status = 'active'
LIMIT 5;

-- Test: Usar la vista de límites
SELECT * FROM v_user_marketplace_limits LIMIT 5;

-- ========================================
-- RESULTADO FINAL
-- ========================================
SELECT '✅ DISEÑO NORMALIZADO CREADO - Sin duplicar datos!' as status;