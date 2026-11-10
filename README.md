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
│   ├── raw/                     # Dataset original SIN modificaciones
│   └── processed/               # Datos limpios y transformados
│       ├── student_por_limpio.csv     (649 registros + variables derivadas)
│       ├── student_por_modelo.csv     (634 registros codificados, Unidad III)
│       ├── student_por_escalado.csv   (634 registros escalados, Unidad IV)
│       └── datamart/                  (una tabla CSV por tabla del Data Mart)
├── notebooks/
│   ├── 01_exploracion_datos.ipynb     # EDA y diccionario de datos
│   └── 02_limpieza_etl.ipynb          # Limpieza, transformación y ETL
├── src/
│   └── etl.py                   # Proceso ETL completo y reproducible
├── sql/
│   ├── 01_crear_datamart.sql    # Crea la base y el modelo estrella
│   ├── 02_cargar_datos.sql      # Inserta los datos (generado por etl.py)
│   └── 03_consultas_analiticas.sql
├── modelos/                     # Modelos entrenados (.joblib)
├── dashboard/                   # Archivo de Power BI (.pbix)
└── docs/
    ├── diccionario_de_datos.csv
    └── figuras/                 # Gráficas del análisis exploratorio
```

> **Regla de integridad:** `data/raw/` conserva siempre el dataset original sin modificar. Todo archivo limpio o transformado se guarda en `data/processed/`.

## Unidad II: preparación de datos

**Decisiones de limpieza**

| Hallazgo | Decisión |
|---|---|
| 0 nulos, 0 duplicados, sin valores fuera de rango | No se requiere imputación |
| 15 alumnos con G3 = 0 y 0 faltas (probable abandono) | Se marcan con `abandono = 1`; se conservan en el Data Mart y se excluyen del modelado |
| 21 alumnos con más de 15 faltas (atípicos por IQR) | Son válidos; para el modelado se recortan a 15 |
| 13 variables binarias y 4 nominales | Binarias → 0/1; nominales → one-hot |
| Escalas distintas entre variables | `StandardScaler` para clustering/PCA |

**Variables derivadas:** `id_estudiante`, `aprobado` (G3 ≥ 10), `nivel_desempeno` (Bajo/Medio/Alto), `abandono`.

**Data Mart `DM_RendimientoEstudiantil` (modelo estrella)**

- Hechos: `fact_rendimiento` (g1, g2, g3, faltas, reprobadas_previas, aprobado, abandono)
- Dimensiones: `dim_estudiante`, `dim_familia`, `dim_habitos`, `dim_escuela`, `dim_desempeno`

## Cómo ejecutar

```bash
pip install -r requirements.txt
python src/etl.py
```

Después, en SQL Server Management Studio (servidor `localhost\SQLEXPRESS`) ejecutar en orden los scripts de `sql/`.

## Avance por unidad

| Unidad | Entrega | Fecha | Estado |
|---|---|---|---|
| Actividad 0 | Inicio y registro | 25 sep 2026 | ✅ Entregada |
| I | Planeación del proyecto (`docs/Mendoza_Vigueras_Brisa_U1_PlaneacionProyecto.pdf`) | 2 oct 2026 | ✅ Entregada |
| II | Preparación de datos, ETL y Data Mart | 16 oct 2026 | ✅ En revisión |
| III | Análisis supervisado | 30 oct 2026 | ⏳ Pendiente |
| IV | Análisis no supervisado | 13 nov 2026 | ⏳ Pendiente |
| V | Dashboard, storytelling y defensa | 20 nov 2026 | ⏳ Pendiente |
