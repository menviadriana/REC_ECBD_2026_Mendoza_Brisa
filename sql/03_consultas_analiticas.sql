/* Consultas de prueba sobre el Data Mart (ejecutar después de cargar los datos) */
USE DM_RendimientoEstudiantil;
GO

-- 1. Verificar conteo de registros por tabla
SELECT 'fact_rendimiento' AS tabla, COUNT(*) AS registros FROM dbo.fact_rendimiento
UNION ALL SELECT 'dim_estudiante', COUNT(*) FROM dbo.dim_estudiante
UNION ALL SELECT 'dim_familia',    COUNT(*) FROM dbo.dim_familia
UNION ALL SELECT 'dim_habitos',    COUNT(*) FROM dbo.dim_habitos
UNION ALL SELECT 'dim_escuela',    COUNT(*) FROM dbo.dim_escuela
UNION ALL SELECT 'dim_desempeno',  COUNT(*) FROM dbo.dim_desempeno;

-- 2. Promedio de calificación final y % de aprobación por escuela
SELECT e.nombre AS escuela,
       COUNT(*) AS alumnos,
       CAST(AVG(CAST(f.g3 AS DECIMAL(5,2))) AS DECIMAL(5,2)) AS promedio_g3,
       CAST(100.0 * SUM(CAST(f.aprobado AS INT)) / COUNT(*) AS DECIMAL(5,1)) AS pct_aprobados
FROM dbo.fact_rendimiento f
JOIN dbo.dim_escuela e ON e.id_escuela = f.id_escuela
GROUP BY e.nombre;

-- 3. Alumnos por nivel de desempeño
SELECT d.nivel, d.resultado, COUNT(*) AS alumnos
FROM dbo.fact_rendimiento f
JOIN dbo.dim_desempeno d ON d.id_desempeno = f.id_desempeno
GROUP BY d.id_desempeno, d.nivel, d.resultado
ORDER BY d.id_desempeno;

-- 4. Promedio de G3 según materias reprobadas previamente
SELECT f.reprobadas_previas,
       COUNT(*) AS alumnos,
       CAST(AVG(CAST(f.g3 AS DECIMAL(5,2))) AS DECIMAL(5,2)) AS promedio_g3
FROM dbo.fact_rendimiento f
WHERE f.abandono = 0
GROUP BY f.reprobadas_previas
ORDER BY f.reprobadas_previas;

-- 5. Promedio de G3 según aspiración a estudios superiores
SELECT s.quiere_estudios_superiores,
       COUNT(*) AS alumnos,
       CAST(AVG(CAST(f.g3 AS DECIMAL(5,2))) AS DECIMAL(5,2)) AS promedio_g3
FROM dbo.fact_rendimiento f
JOIN dbo.dim_estudiante s ON s.id_estudiante = f.id_estudiante
WHERE f.abandono = 0
GROUP BY s.quiere_estudios_superiores;

-- 6. Promedio de G3 según tiempo de estudio semanal
SELECT h.tiempo_estudio,
       COUNT(*) AS alumnos,
       CAST(AVG(CAST(f.g3 AS DECIMAL(5,2))) AS DECIMAL(5,2)) AS promedio_g3
FROM dbo.fact_rendimiento f
JOIN dbo.dim_habitos h ON h.id_habitos = f.id_habitos
WHERE f.abandono = 0
GROUP BY h.tiempo_estudio
ORDER BY h.tiempo_estudio;

-- 7. Porcentaje de no aprobados según escolaridad de la madre
SELECT fa.escolaridad_madre,
       COUNT(*) AS alumnos,
       CAST(100.0 * SUM(CASE WHEN f.aprobado = 0 THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(5,1)) AS pct_no_aprobados
FROM dbo.fact_rendimiento f
JOIN dbo.dim_familia fa ON fa.id_familia = f.id_familia
GROUP BY fa.escolaridad_madre
ORDER BY pct_no_aprobados DESC;
