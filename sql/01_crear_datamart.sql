/* =====================================================================
   Data Mart: Rendimiento estudiantil (modelo estrella)
   Proyecto: Análisis del rendimiento académico de estudiantes
   Servidor: localhost\SQLEXPRESS

   Orden de ejecución en SSMS:
     1. Este archivo (crea la base de datos y las tablas)
     2. 02_cargar_datos.sql  (inserta los datos; lo genera src/etl.py)
     3. 03_consultas_analiticas.sql (consultas de prueba)
   ===================================================================== */

IF DB_ID('DM_RendimientoEstudiantil') IS NULL
    CREATE DATABASE DM_RendimientoEstudiantil;
GO

USE DM_RendimientoEstudiantil;
GO

-- Se borran en orden inverso para poder volver a ejecutar el script
DROP TABLE IF EXISTS dbo.fact_rendimiento;
DROP TABLE IF EXISTS dbo.dim_estudiante;
DROP TABLE IF EXISTS dbo.dim_familia;
DROP TABLE IF EXISTS dbo.dim_habitos;
DROP TABLE IF EXISTS dbo.dim_escuela;
DROP TABLE IF EXISTS dbo.dim_desempeno;
GO

/* ---------------------------- DIMENSIONES ---------------------------- */

CREATE TABLE dbo.dim_escuela (
    id_escuela  INT          NOT NULL PRIMARY KEY,
    codigo      CHAR(2)      NOT NULL,
    nombre      NVARCHAR(50) NOT NULL
);

CREATE TABLE dbo.dim_desempeno (
    id_desempeno INT          NOT NULL PRIMARY KEY,
    nivel        NVARCHAR(10) NOT NULL,
    calif_min    TINYINT      NOT NULL,
    calif_max    TINYINT      NOT NULL,
    resultado    NVARCHAR(15) NOT NULL
);

CREATE TABLE dbo.dim_estudiante (
    id_estudiante              INT          NOT NULL PRIMARY KEY,
    sexo                       NVARCHAR(10) NOT NULL,
    edad                       TINYINT      NOT NULL,
    domicilio                  NVARCHAR(10) NOT NULL,
    motivo_escuela             NVARCHAR(20) NOT NULL,
    quiere_estudios_superiores NVARCHAR(2)  NOT NULL,
    internet_en_casa           NVARCHAR(2)  NOT NULL,
    relacion_pareja            NVARCHAR(2)  NOT NULL,
    asistio_guarderia          NVARCHAR(2)  NOT NULL,
    salud                      TINYINT      NOT NULL   -- 1 muy mala a 5 muy buena
);

CREATE TABLE dbo.dim_familia (
    id_familia        INT          NOT NULL PRIMARY KEY,
    tamano_familia    NVARCHAR(10) NOT NULL,
    estado_padres     NVARCHAR(10) NOT NULL,
    escolaridad_madre NVARCHAR(15) NOT NULL,
    escolaridad_padre NVARCHAR(15) NOT NULL,
    trabajo_madre     NVARCHAR(10) NOT NULL,
    trabajo_padre     NVARCHAR(10) NOT NULL,
    tutor             NVARCHAR(10) NOT NULL,
    apoyo_familiar    NVARCHAR(2)  NOT NULL,
    relacion_familiar TINYINT      NOT NULL    -- 1 muy mala a 5 excelente
);

CREATE TABLE dbo.dim_habitos (
    id_habitos           INT         NOT NULL PRIMARY KEY,
    tiempo_estudio       TINYINT     NOT NULL,  -- 1: <2 h ... 4: >10 h
    tiempo_traslado      TINYINT     NOT NULL,  -- 1: <15 min ... 4: >1 h
    tiempo_libre         TINYINT     NOT NULL,  -- 1 a 5
    salidas_amigos       TINYINT     NOT NULL,  -- 1 a 5
    alcohol_entre_semana TINYINT     NOT NULL,  -- 1 a 5
    alcohol_fin_semana   TINYINT     NOT NULL,  -- 1 a 5
    actividades_extra    NVARCHAR(2) NOT NULL,
    apoyo_escolar        NVARCHAR(2) NOT NULL,
    clases_pagadas       NVARCHAR(2) NOT NULL
);

/* -------------------------- TABLA DE HECHOS -------------------------- */

CREATE TABLE dbo.fact_rendimiento (
    id_hecho           INT     NOT NULL PRIMARY KEY,
    id_estudiante      INT     NOT NULL REFERENCES dbo.dim_estudiante(id_estudiante),
    id_escuela         INT     NOT NULL REFERENCES dbo.dim_escuela(id_escuela),
    id_familia         INT     NOT NULL REFERENCES dbo.dim_familia(id_familia),
    id_habitos         INT     NOT NULL REFERENCES dbo.dim_habitos(id_habitos),
    id_desempeno       INT     NOT NULL REFERENCES dbo.dim_desempeno(id_desempeno),
    g1                 TINYINT NOT NULL,   -- calificación periodo 1 (0-20)
    g2                 TINYINT NOT NULL,   -- calificación periodo 2 (0-20)
    g3                 TINYINT NOT NULL,   -- calificación final (0-20)
    faltas             TINYINT NOT NULL,
    reprobadas_previas TINYINT NOT NULL,
    aprobado           BIT     NOT NULL,   -- 1 si g3 >= 10
    abandono           BIT     NOT NULL    -- 1 si g3 = 0 (no presentó)
);
GO
