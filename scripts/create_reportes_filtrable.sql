-- 🐓📊 VISTA ÉPICA FILTRABLE POR AÑO Y MES
-- 🎯 Sistema de reportes con filtros dinámicos
-- 📅 Creado: 2025-01-13 - Versión rápida para el cumpa con sueño
-- 🚀 SIN ÍNDICES - Solo la vista

-- 🗄️ FUNCIÓN ÉPICA PARA FILTROS DINÁMICOS
CREATE OR REPLACE FUNCTION get_dashboard_filtrado(
    p_año INT DEFAULT NULL,
    p_mes INT DEFAULT NULL,
    p_user_id INT DEFAULT NULL
) 
RETURNS JSON AS $$
DECLARE
    result_json JSON;
    año_filtro INT;
    mes_filtro INT;
BEGIN
    -- Si no se pasan parámetros, usar fecha actual
    año_filtro := COALESCE(p_año, EXTRACT(YEAR FROM CURRENT_DATE));
    mes_filtro := COALESCE(p_mes, EXTRACT(MONTH FROM CURRENT_DATE));
    
    WITH 
    -- 📊 MÉTRICAS DEL PERÍODO SELECCIONADO
    metricas_periodo AS (
        SELECT 
            COUNT(DISTINCT g.id) as total_gallos,
            COUNT(DISTINCT g.id) FILTER (WHERE g.estado = 'activo') as gallos_activos,
            COUNT(DISTINCT p.id) FILTER (
                WHERE EXTRACT(YEAR FROM p.fecha_pelea) = año_filtro 
                AND EXTRACT(MONTH FROM p.fecha_pelea) = mes_filtro
            ) as peleas_periodo,
            COUNT(DISTINCT p.id) FILTER (
                WHERE p.resultado = 'ganada' 
                AND EXTRACT(YEAR FROM p.fecha_pelea) = año_filtro 
                AND EXTRACT(MONTH FROM p.fecha_pelea) = mes_filtro
            ) as ganadas_periodo,
            COUNT(DISTINCT t.id) FILTER (
                WHERE EXTRACT(YEAR FROM t.fecha_tope) = año_filtro 
                AND EXTRACT(MONTH FROM t.fecha_tope) = mes_filtro
            ) as topes_periodo,
            COUNT(DISTINCT v.id) FILTER (
                WHERE EXTRACT(YEAR FROM v.fecha_aplicacion) = año_filtro 
                AND EXTRACT(MONTH FROM v.fecha_aplicacion) = mes_filtro
            ) as vacunas_periodo
        FROM gallos g
        LEFT JOIN peleas p ON g.id = p.gallo_id AND (p_user_id IS NULL OR g.user_id = p_user_id)
        LEFT JOIN topes t ON g.id = t.gallo_id AND (p_user_id IS NULL OR g.user_id = p_user_id)
        LEFT JOIN vacunas v ON g.id = v.gallo_id AND (p_user_id IS NULL OR g.user_id = p_user_id)
        WHERE (p_user_id IS NULL OR g.user_id = p_user_id)
    ),
    
    -- 💰 GASTOS DEL PERÍODO
    gastos_periodo AS (
        SELECT 
            SUM(costo) as gastos_totales,
            SUM(CASE WHEN tipo_gasto = 'alimento' THEN costo ELSE 0 END) as gastos_alimento,
            SUM(CASE WHEN tipo_gasto = 'medicina' THEN costo ELSE 0 END) as gastos_medicina,
            SUM(CASE WHEN tipo_gasto = 'entrenador' THEN costo ELSE 0 END) as gastos_entrenador,
            SUM(CASE WHEN tipo_gasto = 'limpieza_galpon' THEN costo ELSE 0 END) as gastos_limpieza
        FROM inversiones i
        WHERE i.año = año_filtro 
        AND i.mes = mes_filtro
        AND (p_user_id IS NULL OR i.user_id = p_user_id)
    ),
    
    -- 🏆 TOP GALLOS DEL PERÍODO
    top_gallos_periodo AS (
        SELECT 
            g.id, g.nombre, g.raza_id as raza, g.codigo_identificacion,
            COUNT(p.id) as peleas_periodo,
            COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END) as ganadas_periodo,
            ROUND(COALESCE(COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END)::numeric / NULLIF(COUNT(p.id), 0) * 100, 0), 1) as efectividad_periodo
        FROM gallos g
        LEFT JOIN peleas p ON g.id = p.gallo_id 
            AND EXTRACT(YEAR FROM p.fecha_pelea) = año_filtro 
            AND EXTRACT(MONTH FROM p.fecha_pelea) = mes_filtro
        WHERE g.estado = 'activo'
        AND (p_user_id IS NULL OR g.user_id = p_user_id)
        GROUP BY g.id, g.nombre, g.raza_id, g.codigo_identificacion
        HAVING COUNT(p.id) > 0
        ORDER BY efectividad_periodo DESC, ganadas_periodo DESC
        LIMIT 10
    ),
    
    -- 📈 EVOLUCIÓN 6 MESES DESDE EL PERÍODO SELECCIONADO
    evolucion_6m AS (
        SELECT 
            TO_CHAR(fecha_mes, 'Mon YYYY') as periodo_label,
            EXTRACT(YEAR FROM fecha_mes) as año,
            EXTRACT(MONTH FROM fecha_mes) as mes,
            COALESCE(peleas_mes, 0) as peleas,
            COALESCE(ganadas_mes, 0) as ganadas,
            COALESCE(gastos_mes, 0) as gastos
        FROM (
            SELECT MAKE_DATE(año_filtro, mes_filtro, 1) - INTERVAL '5 months' + INTERVAL '1 month' * generate_series(0, 5) as fecha_mes
        ) meses
        LEFT JOIN (
            SELECT 
                DATE_TRUNC('month', p.fecha_pelea) as mes_pelea,
                COUNT(*) as peleas_mes,
                COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END) as ganadas_mes
            FROM peleas p
            JOIN gallos g ON p.gallo_id = g.id
            WHERE (p_user_id IS NULL OR g.user_id = p_user_id)
            AND p.fecha_pelea >= MAKE_DATE(año_filtro, mes_filtro, 1) - INTERVAL '5 months'
            AND p.fecha_pelea < MAKE_DATE(año_filtro, mes_filtro, 1) + INTERVAL '1 month'
            GROUP BY DATE_TRUNC('month', p.fecha_pelea)
        ) peleas_data ON meses.fecha_mes = peleas_data.mes_pelea
        LEFT JOIN (
            SELECT 
                MAKE_DATE(i.año, i.mes, 1) as mes_gasto,
                SUM(i.costo) as gastos_mes
            FROM inversiones i
            WHERE (p_user_id IS NULL OR i.user_id = p_user_id)
            AND MAKE_DATE(i.año, i.mes, 1) >= MAKE_DATE(año_filtro, mes_filtro, 1) - INTERVAL '5 months'
            AND MAKE_DATE(i.año, i.mes, 1) < MAKE_DATE(año_filtro, mes_filtro, 1) + INTERVAL '1 month'
            GROUP BY MAKE_DATE(i.año, i.mes, 1)
        ) gastos_data ON meses.fecha_mes = gastos_data.mes_gasto
        ORDER BY fecha_mes
    )
    
    -- 🎯 JSON FINAL
    SELECT json_build_object(
        'timestamp', EXTRACT(EPOCH FROM NOW()),
        'filtros_aplicados', json_build_object(
            'año', año_filtro,
            'mes', mes_filtro,
            'user_id', p_user_id,
            'periodo_nombre', TO_CHAR(MAKE_DATE(año_filtro, mes_filtro, 1), 'Month YYYY')
        ),
        
        'resumen_periodo', json_build_object(
            'total_gallos', (SELECT total_gallos FROM metricas_periodo),
            'gallos_activos', (SELECT gallos_activos FROM metricas_periodo),
            'peleas_periodo', (SELECT peleas_periodo FROM metricas_periodo),
            'ganadas_periodo', (SELECT ganadas_periodo FROM metricas_periodo),
            'topes_periodo', (SELECT topes_periodo FROM metricas_periodo),
            'efectividad_periodo', ROUND(COALESCE((SELECT ganadas_periodo FROM metricas_periodo)::numeric / NULLIF((SELECT peleas_periodo FROM metricas_periodo), 0) * 100, 0), 1)
        ),
        
        'finanzas_periodo', json_build_object(
            'ingresos', (SELECT ganadas_periodo FROM metricas_periodo) * 3000,
            'gastos_totales', COALESCE((SELECT gastos_totales FROM gastos_periodo), 0),
            'ganancia_neta', ((SELECT ganadas_periodo FROM metricas_periodo) * 3000) - COALESCE((SELECT gastos_totales FROM gastos_periodo), 0),
            'detalle_gastos', json_build_object(
                'alimento', COALESCE((SELECT gastos_alimento FROM gastos_periodo), 0),
                'medicina', COALESCE((SELECT gastos_medicina FROM gastos_periodo), 0),
                'entrenador', COALESCE((SELECT gastos_entrenador FROM gastos_periodo), 0),
                'limpieza', COALESCE((SELECT gastos_limpieza FROM gastos_periodo), 0)
            )
        ),
        
        'top_gallos_periodo', (
            SELECT json_agg(
                json_build_object(
                    'id', id,
                    'nombre', nombre,
                    'raza', raza,
                    'codigo', codigo_identificacion,
                    'peleas_periodo', peleas_periodo,
                    'ganadas_periodo', ganadas_periodo,
                    'efectividad_periodo', efectividad_periodo
                ) ORDER BY efectividad_periodo DESC
            ) FROM top_gallos_periodo
        ),
        
        'evolucion_6_meses', json_build_object(
            'labels', (SELECT json_agg(periodo_label ORDER BY año, mes) FROM evolucion_6m),
            'peleas', (SELECT json_agg(peleas ORDER BY año, mes) FROM evolucion_6m),
            'ganadas', (SELECT json_agg(ganadas ORDER BY año, mes) FROM evolucion_6m),
            'gastos', (SELECT json_agg(gastos ORDER BY año, mes) FROM evolucion_6m)
        )
        
    ) INTO result_json;
    
    RETURN result_json;
END;
$$ LANGUAGE plpgsql;

-- 🎯 VISTA SIMPLE QUE USA LA FUNCIÓN (SIN PARÁMETROS)
CREATE OR REPLACE VIEW v_dashboard_filtrable AS
SELECT get_dashboard_filtrado() as dashboard_data;

-- 📝 COMENTARIO
COMMENT ON FUNCTION get_dashboard_filtrado IS '🐓📊 Función para obtener dashboard filtrado por año y mes. Parámetros opcionales: p_año, p_mes, p_user_id';

-- 🧪 EJEMPLOS DE USO:
-- SELECT get_dashboard_filtrado();                    -- Mes actual
-- SELECT get_dashboard_filtrado(2024, 12);           -- Diciembre 2024
-- SELECT get_dashboard_filtrado(2025, 1, 123);       -- Enero 2025 para user 123
-- SELECT * FROM v_dashboard_filtrable;               -- Vista sin parámetros