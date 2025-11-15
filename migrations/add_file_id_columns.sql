-- =====================================================
-- MIGRACIÓN: Agregar columnas file_id para ImageKit
-- Fecha: 2025-11-15
-- Descripción: Agregar campos file_id para almacenar
--              los IDs de archivos en ImageKit/Storage
-- =====================================================

-- 1. Agregar file_id a peleas (videos)
ALTER TABLE peleas 
ADD COLUMN IF NOT EXISTS file_id VARCHAR(255);

-- 2. Agregar file_id a topes (videos de entrenamientos)
ALTER TABLE topes 
ADD COLUMN IF NOT EXISTS file_id VARCHAR(255);

-- 3. Agregar file_id a peleas_evento (videos de eventos)
-- NOTA: El nombre correcto es "peleas_evento" (singular)
ALTER TABLE peleas_evento 
ADD COLUMN IF NOT EXISTS file_id VARCHAR(255);

-- 4. Agregar comprobante_file_id a pagos_pendientes (comprobantes)
ALTER TABLE pagos_pendientes 
ADD COLUMN IF NOT EXISTS comprobante_file_id VARCHAR(255);

-- =====================================================
-- VERIFICACIÓN
-- =====================================================

-- Verificar que las columnas se agregaron correctamente
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name IN ('peleas', 'topes', 'peleas_evento', 'pagos_pendientes')
  AND column_name IN ('file_id', 'comprobante_file_id')
ORDER BY table_name, column_name;

-- =====================================================
-- ROLLBACK (si necesitas revertir)
-- =====================================================

-- DESCOMENTA ESTAS LÍNEAS SOLO SI NECESITAS REVERTIR:
-- ALTER TABLE peleas DROP COLUMN IF EXISTS file_id;
-- ALTER TABLE topes DROP COLUMN IF EXISTS file_id;
-- ALTER TABLE peleas_evento DROP COLUMN IF EXISTS file_id;
-- ALTER TABLE pagos_pendientes DROP COLUMN IF EXISTS comprobante_file_id;
