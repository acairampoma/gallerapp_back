-- 🐓📊 VISTA ÉPICA ADAPTADA A TU BASE DE DATOS REAL
-- 🎯 Sistema de reportes más completo adaptado a tu estructura actual
-- 📅 Creado: 2025-01-13
-- 🚀 Versión: 1.0-ADAPTADO

-- 🗄️ CREAR VISTA PRINCIPAL DE REPORTES (ADAPTADA)
CREATE OR REPLACE VIEW v_dashboard_reportes_adaptado AS
WITH 
-- 📊 MÉTRICAS ACTUALES BÁSICAS (ADAPTADO A TU BD)
metricas_actuales AS (
    SELECT 
        COUNT(DISTINCT g.id) as total_gallos,
        COUNT(DISTINCT g.id) FILTER (WHERE g.estado = 'activo') as gallos_activos,
        COUNT(DISTINCT p.id) FILTER (WHERE DATE_TRUNC('month', p.fecha_pelea) = DATE_TRUNC('month', CURRENT_DATE)) as peleas_mes,
        COUNT(DISTINCT p.id) FILTER (WHERE p.resultado = 'ganada' AND DATE_TRUNC('month', p.fecha_pelea) = DATE_TRUNC('month', CURRENT_DATE)) as ganadas_mes,
        COUNT(DISTINCT t.id) FILTER (WHERE DATE_TRUNC('month', t.fecha_tope) = DATE_TRUNC('month', CURRENT_DATE)) as topes_mes,
        COUNT(DISTINCT v.id) FILTER (WHERE v.fecha_aplicacion >= CURRENT_DATE - INTERVAL '6 months') as vacunas_recientes,
        -- ADAPTADO: Usar estado para identificar reproductores
        COUNT(DISTINCT CASE WHEN g.estado = 'padre' THEN g.id END) as total_padrillos,
        COUNT(DISTINCT CASE WHEN g.estado = 'madre' THEN g.id END) as total_madres
    FROM gallos g
    LEFT JOIN peleas p ON g.id = p.gallo_id
    LEFT JOIN topes t ON g.id = t.gallo_id  
    LEFT JOIN vacunas v ON g.id = v.gallo_id
),

-- 💰 ANÁLISIS FINANCIERO ÚLTIMOS 6 MESES (ADAPTADO)
gastos_6_meses AS (
    SELECT 
        año, mes,
        TO_CHAR(MAKE_DATE(año, mes, 1), 'Mon') as mes_nombre,
        EXTRACT(YEAR FROM MAKE_DATE(año, mes, 1)) as anio_num,
        EXTRACT(MONTH FROM MAKE_DATE(año, mes, 1)) as mes_num,
        SUM(costo) as gastos_totales,
        SUM(CASE WHEN tipo_gasto = 'alimento' THEN costo ELSE 0 END) as gastos_alimento,
        SUM(CASE WHEN tipo_gasto = 'medicina' THEN costo ELSE 0 END) as gastos_medicina,
        SUM(CASE WHEN tipo_gasto = 'entrenador' THEN costo ELSE 0 END) as gastos_entrenador,
        SUM(CASE WHEN tipo_gasto = 'limpieza_galpon' THEN costo ELSE 0 END) as gastos_limpieza,
        COUNT(DISTINCT id) as total_inversiones
    FROM inversiones 
    WHERE MAKE_DATE(año, mes, 1) >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '6 months')
    GROUP BY año, mes
    ORDER BY año, mes
),

-- 🏆 TOP GALLOS POR EFECTIVIDAD (ADAPTADO A TU BD)
top_gallos AS (
    SELECT 
        g.id,
        g.nombre,
        g.raza_id as raza,  -- USAR raza_id como tienes en la BD
        g.codigo_identificacion,
        -- CALCULAR edad_meses usando fecha_nacimiento
        CASE 
            WHEN g.fecha_nacimiento IS NOT NULL THEN 
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, g.fecha_nacimiento)) * 12 + 
                EXTRACT(MONTH FROM AGE(CURRENT_DATE, g.fecha_nacimiento))
            ELSE NULL 
        END as edad_meses,
        g.peso,
        g.color,
        g.estado,
        COUNT(p.id) as total_peleas,
        COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END) as peleas_ganadas,
        COUNT(CASE WHEN p.resultado = 'perdida' THEN 1 END) as peleas_perdidas,
        COUNT(CASE WHEN p.resultado = 'empate' THEN 1 END) as peleas_empates,
        ROUND(
            COALESCE(
                COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END)::numeric / 
                NULLIF(COUNT(p.id), 0) * 100, 
                0
            ), 
            1
        ) as efectividad,
        -- ESTIMAR ingresos (puedes ajustar el monto por pelea ganada)
        COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END) * 3000 as ingresos_estimados,
        MAX(p.fecha_pelea) as ultima_pelea,
        COUNT(t.id) as total_topes,
        COUNT(v.id) as total_vacunas,
        -- Racha actual de victorias
        (
            SELECT COUNT(*) 
            FROM peleas p2 
            WHERE p2.gallo_id = g.id 
            AND p2.fecha_pelea > COALESCE(
                (SELECT MAX(p3.fecha_pelea) 
                 FROM peleas p3 
                 WHERE p3.gallo_id = g.id 
                 AND p3.resultado != 'ganada'
                ), 
                '1900-01-01'::date
            )
            AND p2.resultado = 'ganada'
        ) as racha_victorias
    FROM gallos g
    LEFT JOIN peleas p ON g.id = p.gallo_id
    LEFT JOIN topes t ON g.id = t.gallo_id
    LEFT JOIN vacunas v ON g.id = v.gallo_id
    WHERE g.estado = 'activo'
    GROUP BY g.id, g.nombre, g.raza_id, g.codigo_identificacion, g.fecha_nacimiento, g.peso, g.color, g.estado
    HAVING COUNT(p.id) > 0  -- Solo gallos con peleas
    ORDER BY efectividad DESC, peleas_ganadas DESC
    LIMIT 10
),

-- 👑 RANKING DE PADRILLOS (ADAPTADO)
ranking_padrillos AS (
    SELECT 
        p.id,
        p.nombre as padrillo_nombre,
        p.raza_id as raza,
        p.codigo_identificacion,
        COUNT(DISTINCT h.id) as total_hijos,
        COUNT(DISTINCT hp.id) as hijos_con_peleas,
        COUNT(DISTINCT CASE WHEN hp.resultado = 'ganada' THEN hp.id END) as peleas_ganadas_hijos,
        COUNT(DISTINCT CASE WHEN hp.resultado = 'ganada' THEN h.id END) as hijos_ganadores,
        ROUND(
            COALESCE(
                COUNT(DISTINCT CASE WHEN hp.resultado = 'ganada' THEN hp.id END)::numeric / 
                NULLIF(COUNT(DISTINCT hp.id), 0) * 100, 
                0
            ), 
            1
        ) as efectividad_descendencia,
        ROUND(
            COALESCE(
                COUNT(DISTINCT CASE WHEN hp.resultado = 'ganada' THEN h.id END)::numeric / 
                NULLIF(COUNT(DISTINCT h.id), 0) * 100, 
                0
            ), 
            1
        ) as porcentaje_hijos_ganadores
    FROM gallos p
    LEFT JOIN gallos h ON h.padre_id = p.id  -- hijos
    LEFT JOIN peleas hp ON h.id = hp.gallo_id  -- peleas de los hijos
    WHERE p.estado IN ('padre', 'activo')  -- Incluir padres y activos que puedan ser reproductores
    GROUP BY p.id, p.nombre, p.raza_id, p.codigo_identificacion
    HAVING COUNT(DISTINCT h.id) > 0  -- Solo padrillos con descendencia
    ORDER BY efectividad_descendencia DESC, hijos_ganadores DESC
    LIMIT 10
),

-- 👸 RANKING DE MADRES (ADAPTADO)
ranking_madres AS (
    SELECT 
        m.id,
        m.nombre as madre_nombre,
        m.raza_id as raza,
        m.codigo_identificacion,
        COUNT(DISTINCT h.id) as total_hijos,
        COUNT(DISTINCT hp.id) as hijos_con_peleas,
        COUNT(DISTINCT CASE WHEN hp.resultado = 'ganada' THEN hp.id END) as peleas_ganadas_hijos,
        COUNT(DISTINCT CASE WHEN hp.resultado = 'ganada' THEN h.id END) as hijos_ganadores,
        ROUND(
            COALESCE(
                COUNT(DISTINCT CASE WHEN hp.resultado = 'ganada' THEN hp.id END)::numeric / 
                NULLIF(COUNT(DISTINCT hp.id), 0) * 100, 
                0
            ), 
            1
        ) as efectividad_descendencia,
        ROUND(
            COALESCE(
                COUNT(DISTINCT CASE WHEN hp.resultado = 'ganada' THEN h.id END)::numeric / 
                NULLIF(COUNT(DISTINCT h.id), 0) * 100, 
                0
            ), 
            1
        ) as porcentaje_hijos_ganadores
    FROM gallos m
    LEFT JOIN gallos h ON h.madre_id = m.id  -- hijos
    LEFT JOIN peleas hp ON h.id = hp.gallo_id  -- peleas de los hijos
    WHERE m.estado IN ('madre', 'activo')  -- Incluir madres y activas que puedan ser reproductoras
    GROUP BY m.id, m.nombre, m.raza_id, m.codigo_identificacion
    HAVING COUNT(DISTINCT h.id) > 0  -- Solo madres con descendencia
    ORDER BY efectividad_descendencia DESC, hijos_ganadores DESC
    LIMIT 10
),

-- 💎 MEJORES CRUCES (ADAPTADO)
mejores_cruces AS (
    SELECT 
        p.nombre as padrillo_nombre,
        m.nombre as madre_nombre,
        p.raza_id as raza_padrillo,
        m.raza_id as raza_madre,
        COUNT(DISTINCT h.id) as total_hijos,
        COUNT(DISTINCT hp.id) as peleas_total,
        COUNT(DISTINCT CASE WHEN hp.resultado = 'ganada' THEN hp.id END) as peleas_ganadas,
        ROUND(
            COALESCE(
                COUNT(DISTINCT CASE WHEN hp.resultado = 'ganada' THEN hp.id END)::numeric / 
                NULLIF(COUNT(DISTINCT hp.id), 0) * 100, 
                0
            ), 
            1
        ) as efectividad_cruce,
        STRING_AGG(DISTINCT h.nombre, ', ' ORDER BY h.nombre) as nombres_hijos
    FROM gallos p  -- padre
    JOIN gallos h ON h.padre_id = p.id  -- hijos
    JOIN gallos m ON h.madre_id = m.id  -- madre
    LEFT JOIN peleas hp ON h.id = hp.gallo_id  -- peleas de hijos
    WHERE p.estado IN ('padre', 'activo') 
      AND m.estado IN ('madre', 'activo')
    GROUP BY p.id, p.nombre, m.id, m.nombre, p.raza_id, m.raza_id
    HAVING COUNT(DISTINCT h.id) >= 2 AND COUNT(DISTINCT hp.id) >= 3  -- Mínimo 2 hijos y 3 peleas
    ORDER BY efectividad_cruce DESC, peleas_ganadas DESC
    LIMIT 5
),

-- 📈 EVOLUCIÓN TEMPORAL ÚLTIMOS 12 MESES (ADAPTADO)
evolucion_temporal AS (
    SELECT 
        TO_CHAR(fecha_mes, 'Mon YYYY') as periodo,
        TO_CHAR(fecha_mes, 'MM-YYYY') as periodo_orden,
        EXTRACT(YEAR FROM fecha_mes) as anio,
        EXTRACT(MONTH FROM fecha_mes) as mes,
        COALESCE(peleas_totales, 0) as peleas_mes,
        COALESCE(peleas_ganadas, 0) as ganadas_mes,
        COALESCE(topes_mes, 0) as entrenamientos,
        COALESCE(gastos_mes, 0) as gastos,
        COALESCE(peleas_ganadas, 0) * 3000 as ingresos_estimados
    FROM (
        SELECT DATE_TRUNC('month', CURRENT_DATE - INTERVAL '11 months') + INTERVAL '1 month' * generate_series(0, 11) as fecha_mes
    ) meses
    LEFT JOIN (
        SELECT 
            DATE_TRUNC('month', p.fecha_pelea) as mes_pelea,
            COUNT(*) as peleas_totales,
            COUNT(CASE WHEN p.resultado = 'ganada' THEN 1 END) as peleas_ganadas
        FROM peleas p
        WHERE p.fecha_pelea >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '11 months')
        GROUP BY DATE_TRUNC('month', p.fecha_pelea)
    ) peleas_data ON meses.fecha_mes = peleas_data.mes_pelea
    LEFT JOIN (
        SELECT 
            DATE_TRUNC('month', t.fecha_tope) as mes_tope,
            COUNT(*) as topes_mes
        FROM topes t
        WHERE t.fecha_tope >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '11 months')
        GROUP BY DATE_TRUNC('month', t.fecha_tope)
    ) topes_data ON meses.fecha_mes = topes_data.mes_tope
    LEFT JOIN (
        SELECT 
            MAKE_DATE(i.año, i.mes, 1) as mes_inversion,
            SUM(i.costo) as gastos_mes
        FROM inversiones i
        WHERE MAKE_DATE(i.año, i.mes, 1) >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '11 months')
        GROUP BY MAKE_DATE(i.año, i.mes, 1)
    ) gastos_data ON meses.fecha_mes = gastos_data.mes_inversion
    ORDER BY fecha_mes
)

-- 🎯 CONSULTA PRINCIPAL - JSON ÉPICO ADAPTADO
SELECT json_build_object(
    'timestamp', EXTRACT(EPOCH FROM NOW()),
    'fecha_generacion', NOW()::text,
    'moneda', 'PEN',
    'simbolo', 'S/',
    'version_reporte', '1.0-ADAPTADO',
    
    -- 📊 RESUMEN EJECUTIVO
    'resumen_ejecutivo', json_build_object(
        'total_gallos', (SELECT total_gallos FROM metricas_actuales),
        'gallos_activos', (SELECT gallos_activos FROM metricas_actuales),
        'peleas_mes', (SELECT peleas_mes FROM metricas_actuales),
        'ganadas_mes', (SELECT ganadas_mes FROM metricas_actuales),
        'topes_mes', (SELECT topes_mes FROM metricas_actuales),
        'padrillos', (SELECT total_padrillos FROM metricas_actuales),
        'madres', (SELECT total_madres FROM metricas_actuales),
        'efectividad_general', COALESCE(
            ROUND(
                (SELECT ganadas_mes FROM metricas_actuales)::numeric / 
                NULLIF((SELECT peleas_mes FROM metricas_actuales), 0) * 100, 
                1
            ), 
            0
        )
    ),
    
    -- 💰 ANÁLISIS FINANCIERO
    'finanzas', json_build_object(
        'mes_actual', json_build_object(
            'ingresos', (SELECT ganadas_mes FROM metricas_actuales) * 3000,
            'gastos_totales', COALESCE(
                (SELECT gastos_totales FROM gastos_6_meses 
                 WHERE anio_num = EXTRACT(YEAR FROM CURRENT_DATE) 
                 AND mes_num = EXTRACT(MONTH FROM CURRENT_DATE)), 
                0
            ),
            'ganancia_neta', 
                ((SELECT ganadas_mes FROM metricas_actuales) * 3000) - 
                COALESCE(
                    (SELECT gastos_totales FROM gastos_6_meses 
                     WHERE anio_num = EXTRACT(YEAR FROM CURRENT_DATE) 
                     AND mes_num = EXTRACT(MONTH FROM CURRENT_DATE)), 
                    0
                ),
            'roi_pct', ROUND(
                (
                    ((SELECT ganadas_mes FROM metricas_actuales) * 3000) - 
                    COALESCE(
                        (SELECT gastos_totales FROM gastos_6_meses 
                         WHERE anio_num = EXTRACT(YEAR FROM CURRENT_DATE) 
                         AND mes_num = EXTRACT(MONTH FROM CURRENT_DATE)), 
                        0
                    )
                ) / NULLIF(
                    COALESCE(
                        (SELECT gastos_totales FROM gastos_6_meses 
                         WHERE anio_num = EXTRACT(YEAR FROM CURRENT_DATE) 
                         AND mes_num = EXTRACT(MONTH FROM CURRENT_DATE)), 
                        1
                    ), 
                    0
                ) * 100, 
                1
            ),
            'detalle_gastos', json_build_object(
                'alimento', COALESCE(
                    (SELECT gastos_alimento FROM gastos_6_meses 
                     WHERE anio_num = EXTRACT(YEAR FROM CURRENT_DATE) 
                     AND mes_num = EXTRACT(MONTH FROM CURRENT_DATE)), 
                    0
                ),
                'medicina', COALESCE(
                    (SELECT gastos_medicina FROM gastos_6_meses 
                     WHERE anio_num = EXTRACT(YEAR FROM CURRENT_DATE) 
                     AND mes_num = EXTRACT(MONTH FROM CURRENT_DATE)), 
                    0
                ),
                'entrenador', COALESCE(
                    (SELECT gastos_entrenador FROM gastos_6_meses 
                     WHERE anio_num = EXTRACT(YEAR FROM CURRENT_DATE) 
                     AND mes_num = EXTRACT(MONTH FROM CURRENT_DATE)), 
                    0
                ),
                'limpieza', COALESCE(
                    (SELECT gastos_limpieza FROM gastos_6_meses 
                     WHERE anio_num = EXTRACT(YEAR FROM CURRENT_DATE) 
                     AND mes_num = EXTRACT(MONTH FROM CURRENT_DATE)), 
                    0
                )
            )
        ),
        'evolucion_6_meses', json_build_object(
            'labels', (SELECT json_agg(mes_nombre ORDER BY año, mes) FROM gastos_6_meses),
            'gastos_totales', (SELECT json_agg(gastos_totales ORDER BY año, mes) FROM gastos_6_meses),
            'gastos_alimento', (SELECT json_agg(gastos_alimento ORDER BY año, mes) FROM gastos_6_meses),
            'gastos_medicina', (SELECT json_agg(gastos_medicina ORDER BY año, mes) FROM gastos_6_meses),
            'gastos_entrenador', (SELECT json_agg(gastos_entrenador ORDER BY año, mes) FROM gastos_6_meses),
            'gastos_limpieza', (SELECT json_agg(gastos_limpieza ORDER BY año, mes) FROM gastos_6_meses)
        )
    ),
    
    -- 🏆 RANKINGS
    'rankings', json_build_object(
        'top_gallos', (
            SELECT json_agg(
                json_build_object(
                    'id', id,
                    'nombre', nombre,
                    'raza', raza,
                    'codigo_identificacion', codigo_identificacion,
                    'edad_meses', edad_meses,
                    'peso', peso,
                    'color', color,
                    'total_peleas', total_peleas,
                    'peleas_ganadas', peleas_ganadas,
                    'peleas_perdidas', peleas_perdidas,
                    'efectividad', efectividad,
                    'ingresos_estimados', ingresos_estimados,
                    'ultima_pelea', ultima_pelea,
                    'total_topes', total_topes,
                    'racha_victorias', racha_victorias
                ) ORDER BY efectividad DESC
            ) 
            FROM top_gallos
        ),
        'top_padrillos', (
            SELECT json_agg(
                json_build_object(
                    'id', id,
                    'nombre', padrillo_nombre,
                    'raza', raza,
                    'codigo_identificacion', codigo_identificacion,
                    'total_hijos', total_hijos,
                    'hijos_con_peleas', hijos_con_peleas,
                    'peleas_ganadas_hijos', peleas_ganadas_hijos,
                    'hijos_ganadores', hijos_ganadores,
                    'efectividad_descendencia', efectividad_descendencia,
                    'porcentaje_hijos_ganadores', porcentaje_hijos_ganadores
                ) ORDER BY efectividad_descendencia DESC
            ) 
            FROM ranking_padrillos
        ),
        'top_madres', (
            SELECT json_agg(
                json_build_object(
                    'id', id,
                    'nombre', madre_nombre,
                    'raza', raza,
                    'codigo_identificacion', codigo_identificacion,
                    'total_hijos', total_hijos,
                    'hijos_con_peleas', hijos_con_peleas,
                    'peleas_ganadas_hijos', peleas_ganadas_hijos,
                    'hijos_ganadores', hijos_ganadores,
                    'efectividad_descendencia', efectividad_descendencia,
                    'porcentaje_hijos_ganadores', porcentaje_hijos_ganadores
                ) ORDER BY efectividad_descendencia DESC
            ) 
            FROM ranking_madres
        ),
        'mejores_cruces', (
            SELECT json_agg(
                json_build_object(
                    'padrillo_nombre', padrillo_nombre,
                    'madre_nombre', madre_nombre,
                    'raza_padrillo', raza_padrillo,
                    'raza_madre', raza_madre,
                    'total_hijos', total_hijos,
                    'peleas_total', peleas_total,
                    'peleas_ganadas', peleas_ganadas,
                    'efectividad_cruce', efectividad_cruce,
                    'nombres_hijos', nombres_hijos
                ) ORDER BY efectividad_cruce DESC
            ) 
            FROM mejores_cruces
        )
    ),
    
    -- 📊 MÉTRICAS KPI
    'metricas_kpi', json_build_object(
        'efectividad', COALESCE(
            ROUND(
                (SELECT ganadas_mes FROM metricas_actuales)::numeric / 
                NULLIF((SELECT peleas_mes FROM metricas_actuales), 0) * 100, 
                1
            ), 
            0
        ),
        'intensidad_entrenamiento', ROUND(
            (SELECT topes_mes FROM metricas_actuales)::numeric / 15 * 100, 
            1
        ),
        'salud_general', ROUND(
            (SELECT vacunas_recientes FROM metricas_actuales)::numeric / 
            NULLIF((SELECT total_gallos FROM metricas_actuales), 0) * 100, 
            1
        ),
        'roi_general', ROUND(
            (
                ((SELECT ganadas_mes FROM metricas_actuales) * 3000) - 
                COALESCE(
                    (SELECT gastos_totales FROM gastos_6_meses 
                     WHERE anio_num = EXTRACT(YEAR FROM CURRENT_DATE) 
                     AND mes_num = EXTRACT(MONTH FROM CURRENT_DATE)), 
                    0
                )
            ) / NULLIF(
                COALESCE(
                    (SELECT gastos_totales FROM gastos_6_meses 
                     WHERE anio_num = EXTRACT(YEAR FROM CURRENT_DATE) 
                     AND mes_num = EXTRACT(MONTH FROM CURRENT_DATE)), 
                    1
                ), 
                0
            ) * 100, 
            1
        )
    ),
    
    -- 📈 EVOLUCIÓN TEMPORAL
    'evolucion_temporal', json_build_object(
        'labels', (SELECT json_agg(periodo ORDER BY periodo_orden) FROM evolucion_temporal),
        'peleas_totales', (SELECT json_agg(peleas_mes ORDER BY periodo_orden) FROM evolucion_temporal),
        'peleas_ganadas', (SELECT json_agg(ganadas_mes ORDER BY periodo_orden) FROM evolucion_temporal),
        'entrenamientos', (SELECT json_agg(entrenamientos ORDER BY periodo_orden) FROM evolucion_temporal),
        'gastos', (SELECT json_agg(gastos ORDER BY periodo_orden) FROM evolucion_temporal),
        'ingresos_estimados', (SELECT json_agg(ingresos_estimados ORDER BY periodo_orden) FROM evolucion_temporal)
    )
    
) as dashboard_data;

-- 🔍 ÍNDICES PARA OPTIMIZAR RENDIMIENTO (ADAPTADO)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_peleas_fecha_resultado_adaptado ON peleas(fecha_pelea, resultado);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_topes_fecha_adaptado ON topes(fecha_tope);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vacunas_fecha_adaptado ON vacunas(fecha_aplicacion);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_gallos_padre_madre_adaptado ON gallos(padre_id, madre_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_gallos_estado_adaptado ON gallos(estado);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_inversiones_fecha_adaptado ON inversiones(año, mes, tipo_gasto);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_gallos_raza_adaptado ON gallos(raza_id);

-- 📝 COMENTARIOS DE LA VISTA
COMMENT ON VIEW v_dashboard_reportes_adaptado IS '🐓📊 Vista épica para reportes gallísticos adaptada a la BD real. Incluye métricas financieras, rankings, análisis temporal y KPIs. Optimizada para tu estructura actual.';

-- 🎯 EJEMPLO DE USO
-- SELECT * FROM v_dashboard_reportes_adaptado;

-- 🧪 QUERY DE TESTING SIMPLE
-- SELECT json_extract_path_text(dashboard_data, 'resumen_ejecutivo', 'total_gallos') as total_gallos 
-- FROM v_dashboard_reportes_adaptado;