-- ============================================================================
-- Script: 002_mejora_peleas_evento.sql
-- Descripción: Mejora tabla peleas_evento para manejo de galpones
-- Autor: Sistema
-- Fecha: 2025-10-01
-- ============================================================================

-- ============================================================================
-- PASO 1: ELIMINAR TABLA EXISTENTE (Si existe)
-- ============================================================================
DROP TABLE IF EXISTS public.peleas_evento CASCADE;

-- ============================================================================
-- PASO 2: CREAR TABLA MEJORADA peleas_evento
-- ============================================================================
CREATE TABLE public.peleas_evento (
    id SERIAL4 PRIMARY KEY,
    evento_id INT4 NOT NULL,

    -- 🎯 Información de la pelea
    numero_pelea INT4 NOT NULL,
    titulo_pelea VARCHAR(255) NOT NULL,
    descripcion_pelea TEXT NULL,

    -- 🐔 GALLO IZQUIERDA (Lado izquierdo del juez)
    galpon_izquierda VARCHAR(100) NOT NULL,
    gallo_izquierda_nombre VARCHAR(100) NOT NULL,

    -- 🐔 GALLO DERECHA (Lado derecho del juez)
    galpon_derecha VARCHAR(100) NOT NULL,
    gallo_derecha_nombre VARCHAR(100) NOT NULL,

    -- ⏰ Tiempos
    hora_inicio_estimada TIME NULL,
    hora_inicio_real TIMESTAMP NULL,
    hora_fin_real TIMESTAMP NULL,
    duracion_minutos INT4 NULL,

    -- 📊 Resultado
    resultado VARCHAR(100) NULL, -- 'izquierda', 'derecha', 'empate', null

    -- 🎥 Video y Media
    video_url TEXT NULL,
    thumbnail_pelea_url TEXT NULL,
    estado_video VARCHAR(50) DEFAULT 'sin_video' NULL,

    -- 👤 Auditoría
    admin_editor_id INT4 NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NULL,

    -- 🔗 Foreign Keys
    CONSTRAINT peleas_evento_evento_id_fkey
        FOREIGN KEY (evento_id)
        REFERENCES public.eventos_transmision(id)
        ON DELETE CASCADE,

    CONSTRAINT peleas_evento_admin_editor_id_fkey
        FOREIGN KEY (admin_editor_id)
        REFERENCES public.users(id)
);

-- ============================================================================
-- PASO 3: CREAR ÍNDICES PARA PERFORMANCE
-- ============================================================================
CREATE INDEX idx_peleas_evento ON public.peleas_evento USING btree (evento_id);
CREATE INDEX idx_peleas_evento_numero ON public.peleas_evento USING btree (evento_id, numero_pelea);
CREATE INDEX idx_peleas_estado_video ON public.peleas_evento USING btree (estado_video);
CREATE INDEX idx_peleas_admin_editor ON public.peleas_evento USING btree (admin_editor_id);
CREATE INDEX idx_peleas_fecha_real ON public.peleas_evento USING btree (hora_inicio_real);

-- ============================================================================
-- PASO 4: COMENTARIOS PARA DOCUMENTACIÓN
-- ============================================================================
COMMENT ON TABLE public.peleas_evento IS 'Peleas que pertenecen a un evento de transmisión';
COMMENT ON COLUMN public.peleas_evento.numero_pelea IS 'Número y orden de la pelea (1, 2, 3...) - puede cambiar';
COMMENT ON COLUMN public.peleas_evento.galpon_izquierda IS 'Nombre del galpón - Lado IZQUIERDO del juez';
COMMENT ON COLUMN public.peleas_evento.galpon_derecha IS 'Nombre del galpón - Lado DERECHO del juez';
COMMENT ON COLUMN public.peleas_evento.gallo_izquierda_nombre IS 'Nombre del gallo - Lado IZQUIERDO del juez';
COMMENT ON COLUMN public.peleas_evento.gallo_derecha_nombre IS 'Nombre del gallo - Lado DERECHO del juez';
COMMENT ON COLUMN public.peleas_evento.resultado IS 'Resultado: izquierda, derecha, empate, o null si no ha ocurrido';
COMMENT ON COLUMN public.peleas_evento.estado_video IS 'Estado del video: sin_video, procesando, disponible';

-- ============================================================================
-- PASO 5: TRIGGER PARA ACTUALIZAR updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION update_peleas_evento_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_peleas_evento_updated_at ON public.peleas_evento;
CREATE TRIGGER trg_peleas_evento_updated_at
    BEFORE UPDATE ON public.peleas_evento
    FOR EACH ROW
    EXECUTE FUNCTION update_peleas_evento_timestamp();

-- ============================================================================
-- PASO 6: DATOS DE EJEMPLO (OPCIONAL - Comentado)
-- ============================================================================
/*
INSERT INTO public.peleas_evento
(evento_id, numero_pelea, titulo_pelea, galpon_izquierda, gallo_izquierda_nombre,
 galpon_derecha, gallo_derecha_nombre, hora_inicio_estimada)
VALUES
(16, 1, 'PELEA ESTELAR', 'El Campeón', 'Relámpago', 'Los Invencibles', 'Trueno', '15:00:00'),
(16, 2, 'SEMIFINAL A', 'Casa Blanca', 'Centurión', 'El Dorado', 'Spartacus', '15:30:00'),
(16, 3, 'SEMIFINAL B', 'Los Tigres', 'Tornado', 'La Victoria', 'Huracán', '16:00:00');
*/

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================
SELECT
    '✅ Tabla peleas_evento recreada exitosamente' as status,
    COUNT(*) as total_peleas
FROM public.peleas_evento;

SELECT
    'Índices creados:' as info,
    indexname
FROM pg_indexes
WHERE tablename = 'peleas_evento'
ORDER BY indexname;
