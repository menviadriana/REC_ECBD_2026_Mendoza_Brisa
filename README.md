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
│   ├── raw/          # Dataset original SIN modificaciones
│   └── processed/    # Datos limpios y transformados
├── notebooks/        # Jupyter Notebooks (EDA, modelos)
├── src/              # Scripts de Python (ETL, funciones)
├── sql/              # Scripts del Data Mart en SQL Server
├── modelos/          # Modelos entrenados (.joblib)
├── dashboard/        # Archivo de Power BI (.pbix)
└── docs/             # Documentos entregables por unidad
```

> **Regla de integridad:** `data/raw/` conserva siempre el dataset original sin modificar. Todo archivo limpio o transformado se guarda en `data/processed/`.

## Forma de trabajo

- Metodología **CRISP-DM**: comprensión del negocio → comprensión de los datos → preparación → modelado → evaluación → despliegue.
- Herramientas: Python 3, Jupyter Notebook / VS Code, pandas, NumPy, Matplotlib, Seaborn, scikit-learn, SQL Server, Power BI, Git y GitHub.
- Avance progresivo por unidad, registrado mediante commits.

Instalación de dependencias:

```bash
pip install -r requirements.txt
```

## Avance por unidad

| Unidad | Entrega | Fecha | Estado |
|---|---|---|---|
| Actividad 0 | Inicio y registro | 25 sep 2026 | ✅ Entregada |
| I | Planeación del proyecto (`docs/Mendoza_Vigueras_Brisa_U1_PlaneacionProyecto.pdf`) | 2 oct 2026 | ✅ Entregada |
| II | Preparación de datos, ETL y Data Mart | 16 oct 2026 | ⏳ Pendiente |
| III | Análisis supervisado | 30 oct 2026 | ⏳ Pendiente |
| IV | Análisis no supervisado | 13 nov 2026 | ⏳ Pendiente |
| V | Dashboard, storytelling y defensa | 20 nov 2026 | ⏳ Pendiente |
