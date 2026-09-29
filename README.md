# Análisis del rendimiento académico de estudiantes

**Recursamiento 2026 – Extracción de Conocimiento en Bases de Datos**
Universidad Tecnológica Tula-Tepeji · Grupo 10IDGS-G1
**Alumna:** Brisa Adriana Mendoza Vigueras
**Docente:** Ing. Jose Luis Herrera Gallardo, MTI

## Descripción
Proyecto integrador individual que recorre las cinco unidades de la asignatura usando el dataset *Student Performance*, con el fin de entender qué factores influyen en la calificación final de los estudiantes y predecir su desempeño.

## Dataset
- **Nombre:** Student Performance
- **Fuente:** UCI Machine Learning Repository – https://archive.ics.uci.edu/dataset/320/student+performance
- **Archivo de trabajo:** `student-por.csv` (curso de Portugués, 649 registros, 33 variables, separador `;`)
- Los archivos originales están en `data/raw/` y **no se modifican**. Los datos limpios se guardan en `data/processed/`.

## Objetivos del análisis
| Tarea | Objetivo |
|---|---|
| Regresión | Predecir la calificación final `G3` |
| Clasificación | Clasificar el desempeño (aprobado / no aprobado) a partir de `G3` |
| No supervisado | Perfiles académicos y sociales con clustering y PCA |

## Estructura del repositorio
```
├── data/
│   ├── raw/          # datos originales sin modificar
│   └── processed/    # datos limpios y transformados
├── notebooks/        # análisis en Jupyter
├── src/              # scripts en Python
├── sql/              # scripts del Data Mart (SQL Server)
├── modelos/          # modelos entrenados
├── dashboard/        # dashboard de Power BI
└── docs/             # documentación e informes
```

## Avance por unidad
- [x] Actividad 0 – Inicio y registro
- [ ] Unidad I – Planeación del proyecto
- [ ] Unidad II – Preparación de datos, ETL y Data Mart
- [ ] Unidad III – Análisis supervisado
- [ ] Unidad IV – Análisis no supervisado
- [ ] Unidad V – Dashboard y storytelling

## Herramientas
Python 3, Jupyter Notebook / VS Code, pandas, NumPy, scikit-learn, Matplotlib, SQL Server, Power BI, Git y GitHub.

## Cómo reproducir
```bash
pip install -r requirements.txt
jupyter notebook
```
