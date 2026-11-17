# REC_ECBD_2026_Mendoza_Brisa

**Proyecto Integrador de Recursamiento – Extracción de Conocimiento en Bases de Datos (2026)**
Universidad Tecnológica Tula-Tepeji · Grupo 10IDGS-G1
Alumna: Brisa Adriana Mendoza Vigueras · Docente: Ing. José Luis Herrera Gallardo, MTI

---

## Proyecto: Análisis del rendimiento académico de estudiantes

El proyecto busca identificar qué factores académicos, familiares y sociales influyen en la calificación final de estudiantes de bachillerato, predecir esa calificación y anticipar el riesgo de reprobación, siguiendo la metodología **CRISP-DM**.

**Pregunta principal:** ¿Qué factores académicos, familiares y sociales influyen en la calificación final de los estudiantes y en qué medida es posible predecirla y anticipar el riesgo de reprobación a partir de ellos?

| Análisis | Definición |
|---|---|
| Regresión | Predecir `G3` (calificación final, 0–20), con y sin `G1`/`G2` |
| Clasificación | Aprobado (`G3 ≥ 10`) / No aprobado (`G3 < 10`); alternativa: bajo (0–9), medio (10–13), alto (14–20) |
| No supervisado | K-Means + PCA para identificar perfiles de estudiantes |

## Dataset

| Dato | Valor |
|---|---|
| Nombre | Student Performance |
| Fuente | UCI Machine Learning Repository |
| Enlace | https://archive.ics.uci.edu/dataset/320/student+performance |
| DOI | 10.24432/C5TG7T |
| Archivo de trabajo | `student-por.csv` (curso de Portugués), separador `;` |
| Tamaño | 649 registros × 33 columnas (30 características + G1, G2, G3) |
| Calidad inicial | 0 nulos, 0 duplicados, 15 registros con G3 = 0 |

El paquete descargado también incluye `student-mat.csv`, `student-merge.R` y `student.txt`; se conservan en `data/raw/` pero solo se analiza `student-por.csv`.

**Cita:** Cortez, P. (2008). *Student Performance* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5TG7T

## Estructura del repositorio

```
REC_ECBD_2026_Mendoza_Brisa/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                         # Dataset original SIN modificaciones
│   └── processed/                   # Datos limpios, transformados y resultados
│       ├── student_por_limpio.csv         (dataset limpio: 649 registros + variables derivadas)
│       ├── student_por_modelo.csv         (634 registros codificados, Unidad III)
│       ├── student_por_escalado.csv       (634 registros escalados, Unidad IV)
│       ├── datamart/                      (una tabla CSV por tabla del Data Mart)
│       ├── predicciones_supervisado.csv   (predicciones de los modelos, Unidad III)
│       ├── metricas_supervisado.csv       (métricas de todos los modelos, Unidad III)
│       ├── clusters_estudiantes.csv       (cluster y componentes PCA por alumno, Unidad IV)
│       └── resumen_clusters.csv           (perfil promedio de cada cluster, Unidad IV)
├── notebooks/
│   ├── Mendoza_Vigueras_Brisa_U2_AE1_Exploracion.ipynb
│   ├── Mendoza_Vigueras_Brisa_U2_AE2_ETL.ipynb
│   ├── Mendoza_Vigueras_Brisa_U3_AnalisisSupervisado.ipynb
│   └── Mendoza_Vigueras_Brisa_U4_AnalisisNoSupervisado.ipynb
├── src/
│   └── etl.py                       # Proceso ETL completo y reproducible
├── sql/
│   ├── 01_crear_datamart.sql        # Script de creación del Data Mart (modelo estrella)
│   ├── 02_cargar_datos.sql          # Carga de datos (generado por etl.py)
│   └── 03_consultas_analiticas.sql  # Consultas de verificación y análisis
├── modelos/                         # Modelos entrenados (.joblib)
├── dashboard/                       # Dashboard de Power BI (.pbix)
└── docs/                            # Informes PDF, diccionario, diagrama y figuras
```

> **Regla de integridad:** `data/raw/` conserva siempre el dataset original sin modificar. Todo archivo limpio o transformado se guarda en `data/processed/`.

## Unidad II: preparación de datos

**AE1 – Exploración y diagnóstico:** `notebooks/Mendoza_Vigueras_Brisa_U2_AE1_Exploracion.ipynb` · informe `docs/Mendoza_Vigueras_Brisa_U2_AE1_Diagnostico.pdf`.
Hallazgos: 0 nulos, 0 duplicados, 0 valores fuera de rango; 15 alumnos con G3 = 0 (abandono), 1 con G1 = 0 (dato no capturado), 21 atípicos en faltas, clases desbalanceadas (84.6 % / 15.4 %).

**AE2 – Limpieza, ETL y Data Mart:** `notebooks/Mendoza_Vigueras_Brisa_U2_AE2_ETL.ipynb` · `src/etl.py` · `sql/` · diagrama `docs/figuras/diagrama_datamart.png`.

| Hallazgo | Decisión |
|---|---|
| Sin nulos, duplicados ni valores fuera de rango | No se requiere imputación ni eliminación |
| 15 alumnos con G3 = 0 y 0 faltas (abandono) | Se marcan con `abandono = 1`; se conservan en el Data Mart y se excluyen del modelado |
| 21 alumnos con más de 15 faltas | Válidos; se recortan a 15 solo para el modelado |
| 13 binarias y 4 nominales de texto | Binarias → 0/1; nominales → one-hot |
| Escalas distintas | `StandardScaler` para clustering y PCA |

Data Mart `DM_RendimientoEstudiantil` en SQL Server (`localhost\SQLEXPRESS`): tabla de hechos `fact_rendimiento` (g1, g2, g3, faltas, reprobadas_previas, aprobado, abandono) y dimensiones `dim_estudiante`, `dim_familia`, `dim_habitos`, `dim_escuela`, `dim_desempeno`.

## Unidad III: análisis supervisado

`notebooks/Mendoza_Vigueras_Brisa_U3_AnalisisSupervisado.ipynb` · modelos en `modelos/`.

Se comparan tres escenarios según el momento del curso: **inicio** (sin calificaciones), **alerta temprana** (con G1) y **final** (con G1 y G2). El escenario principal es el de alerta temprana.

| Tarea | Modelo final (escenario alerta temprana) | Resultado en prueba |
|---|---|---|
| Regresión de G3 | Random Forest optimizado (GridSearchCV) | MAE = 0.95 · RMSE = 1.18 · R² = 0.77 |
| Clasificación aprobado / no aprobado | Random Forest optimizado (`class_weight="balanced"`, max_depth = 3) | Recall (no aprobado) = 0.82 · F1 = 0.56 · Accuracy = 0.83 |

Variables más relevantes sin calificaciones: materias reprobadas previas, aspiración a estudios superiores, faltas, escolaridad de la madre y tiempo de estudio.

## Unidad IV: análisis no supervisado

`notebooks/Mendoza_Vigueras_Brisa_U4_AnalisisNoSupervisado.ipynb`

K-Means (k = 4) sobre 11 variables de hábitos y entorno, estandarizadas; PCA para la visualización (PC1 = vida social y alcohol, PC2 = escolaridad de los padres).

| Perfil | Alumnos | Promedio G3 | % no aprobados |
|---|---|---|---|
| Entorno favorable | 217 | 13.46 | 4.1 % |
| Tranquilos con menor apoyo escolar familiar | 237 | 12.16 | 11.4 % |
| Vida social intensa | 130 | 11.25 | 18.5 % |
| Historial de reprobación | 50 | 9.22 | 50.0 % |

## Cómo ejecutar

```bash
pip install -r requirements.txt
python src/etl.py
```

1. En SQL Server Management Studio (servidor `localhost\SQLEXPRESS`), ejecutar en orden los scripts de `sql/`.
2. Abrir los notebooks de `notebooks/` en orden (U2_AE1 → U2_AE2 → U3 → U4) y ejecutar **Run All**.

## Avance por unidad

| Unidad | Entrega | Fecha | Estado |
|---|---|---|---|
| Actividad 0 | Inicio y registro | 25 sep 2026 | ✅ Entregada |
| I | Planeación del proyecto | 2 oct 2026 | ✅ Entregada |
| II – AE1 | Exploración y diagnóstico | 11 nov 2026 | ✅ Entregada |
| II – AE2 | Limpieza, ETL y Data Mart | 13 nov 2026 | ✅ Completa |
| III | Análisis supervisado | 16 nov 2026 | ✅ Completa |
| IV | Análisis no supervisado | 18 nov 2026 | 🔄 Notebook completo; informe en desarrollo |
| V | Dashboard, storytelling y defensa | 20 nov 2026 | 🔄 Dashboard iniciado |
