-- 💳 Migración: Agregar campos de Mercado Pago a tabla suscripciones
-- Fecha: 2024-11-17
-- Descripción: Agrega campos para integración con Mercado Pago

-- Agregar columnas de Mercado Pago
ALTER TABLE suscripciones 
ADD COLUMN IF NOT EXISTS payment_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS preference_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS external_reference VARCHAR(200),
ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50),
ADD COLUMN IF NOT EXISTS payment_status VARCHAR(50),
ADD COLUMN IF NOT EXISTS payment_status_detail VARCHAR(100),
ADD COLUMN IF NOT EXISTS transaction_amount NUMERIC(10, 2),
ADD COLUMN IF NOT EXISTS fecha_pago TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS mercadopago_data TEXT;

-- Crear índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_suscripciones_payment_id ON suscripciones(payment_id);
CREATE INDEX IF NOT EXISTS idx_suscripciones_preference_id ON suscripciones(preference_id);
CREATE INDEX IF NOT EXISTS idx_suscripciones_external_reference ON suscripciones(external_reference);

-- Comentarios
COMMENT ON COLUMN suscripciones.payment_id IS 'ID del pago en Mercado Pago';
COMMENT ON COLUMN suscripciones.preference_id IS 'ID de la preferencia de pago';
COMMENT ON COLUMN suscripciones.external_reference IS 'Referencia única del pago';
COMMENT ON COLUMN suscripciones.payment_method IS 'Método de pago usado (yape, credit_card, etc)';
COMMENT ON COLUMN suscripciones.payment_status IS 'Estado del pago (approved, pending, rejected)';
COMMENT ON COLUMN suscripciones.payment_status_detail IS 'Detalle del estado del pago';
COMMENT ON COLUMN suscripciones.transaction_amount IS 'Monto real pagado';
COMMENT ON COLUMN suscripciones.fecha_pago IS 'Fecha en que se aprobó el pago';
COMMENT ON COLUMN suscripciones.mercadopago_data IS 'JSON con data completa de Mercado Pago';

-- Verificar que la migración se aplicó correctamente
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns
WHERE table_name = 'suscripciones'
AND column_name IN (
    'payment_id', 
    'preference_id', 
    'external_reference', 
    'payment_method', 
    'payment_status'
)
ORDER BY column_name;
