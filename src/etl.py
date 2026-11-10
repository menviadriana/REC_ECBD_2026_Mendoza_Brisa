"""
ETL del proyecto: Análisis del rendimiento académico de estudiantes
Dataset: Student Performance (UCI) - archivo student-por.csv

Extract   -> lee el CSV original de data/raw (sin modificarlo)
Transform -> limpia, crea variables derivadas y codifica
Load      -> guarda los archivos en data/processed y genera el script SQL
             para cargar el Data Mart en SQL Server

Uso (desde la raíz del repositorio):
    python src/etl.py
"""
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw" / "student-por.csv"
PROCESSED = RAIZ / "data" / "processed"
DATAMART = PROCESSED / "datamart"
SQL_CARGA = RAIZ / "sql" / "02_cargar_datos.sql"

BINARIAS = ["school", "sex", "address", "famsize", "Pstatus", "schoolsup", "famsup",
            "paid", "activities", "nursery", "higher", "internet", "romantic"]
NOMINALES = ["Mjob", "Fjob", "reason", "guardian"]

# Valor que se convierte en 1 para cada variable binaria
MAPEO_BINARIAS = {
    "school": "GP", "sex": "F", "address": "U", "famsize": "GT3", "Pstatus": "T",
    "schoolsup": "yes", "famsup": "yes", "paid": "yes", "activities": "yes",
    "nursery": "yes", "higher": "yes", "internet": "yes", "romantic": "yes",
}

# Traducciones para el Data Mart (las ve el usuario final en Power BI)
SI_NO = {"yes": "Sí", "no": "No"}
TRABAJOS = {"teacher": "Docente", "health": "Salud", "services": "Servicios",
            "at_home": "Hogar", "other": "Otro"}
MOTIVOS = {"home": "Cercanía", "reputation": "Reputación", "course": "Plan de estudios",
           "other": "Otro"}
TUTORES = {"mother": "Madre", "father": "Padre", "other": "Otro"}
ESCOLARIDAD = {0: "Ninguna", 1: "Primaria (4°)", 2: "5° a 9°", 3: "Secundaria",
               4: "Superior"}


# ----------------------------------------------------------------- EXTRACT
def extraer(ruta=RAW):
    return pd.read_csv(ruta, sep=";")


# --------------------------------------------------------------- TRANSFORM
def nivel_desempeno(g3):
    if g3 <= 9:
        return "Bajo"
    if g3 <= 13:
        return "Medio"
    return "Alto"


def limpiar(df):
    """Datos limpios con variables derivadas. Conserva los 649 registros."""
    df = df.copy()
    df.insert(0, "id_estudiante", range(1, len(df) + 1))
    # G3 = 0 con 0 faltas -> no presentó la evaluación final (abandono)
    df["abandono"] = (df["G3"] == 0).astype(int)
    df["aprobado"] = (df["G3"] >= 10).astype(int)
    df["nivel_desempeno"] = df["G3"].apply(nivel_desempeno)
    # Faltas: se recortan al límite superior del IQR para el modelado
    q1, q3 = df["absences"].quantile([0.25, 0.75])
    limite = q3 + 1.5 * (q3 - q1)
    df["absences_recortado"] = df["absences"].clip(upper=limite)
    return df


def codificar(df_limpio):
    """Dataset numérico para los modelos (Unidad III). Excluye abandonos."""
    df = df_limpio[df_limpio["abandono"] == 0].copy()
    for col in BINARIAS:
        df[col] = (df[col] == MAPEO_BINARIAS[col]).astype(int)
    df = pd.get_dummies(df, columns=NOMINALES, drop_first=True, dtype=int)
    df["absences"] = df["absences_recortado"]
    df = df.drop(columns=["absences_recortado", "abandono", "nivel_desempeno"])
    return df


def escalar(df_modelo):
    """Versión escalada para clustering y PCA (Unidad IV)."""
    excluir = ["id_estudiante", "G1", "G2", "G3", "aprobado"]
    columnas = [c for c in df_modelo.columns if c not in excluir]
    df = df_modelo.copy()
    df[columnas] = StandardScaler().fit_transform(df[columnas])
    return df


def tablas_datamart(df):
    """Modelo estrella: 5 dimensiones y 1 tabla de hechos."""
    dim_escuela = pd.DataFrame({
        "id_escuela": [1, 2],
        "codigo": ["GP", "MS"],
        "nombre": ["Gabriel Pereira", "Mousinho da Silveira"],
    })
    dim_desempeno = pd.DataFrame({
        "id_desempeno": [1, 2, 3],
        "nivel": ["Bajo", "Medio", "Alto"],
        "calif_min": [0, 10, 14],
        "calif_max": [9, 13, 20],
        "resultado": ["No aprobado", "Aprobado", "Aprobado"],
    })
    dim_estudiante = pd.DataFrame({
        "id_estudiante": df["id_estudiante"],
        "sexo": df["sex"].map({"F": "Femenino", "M": "Masculino"}),
        "edad": df["age"],
        "domicilio": df["address"].map({"U": "Urbano", "R": "Rural"}),
        "motivo_escuela": df["reason"].map(MOTIVOS),
        "quiere_estudios_superiores": df["higher"].map(SI_NO),
        "internet_en_casa": df["internet"].map(SI_NO),
        "relacion_pareja": df["romantic"].map(SI_NO),
        "asistio_guarderia": df["nursery"].map(SI_NO),
        "salud": df["health"],
    })
    dim_familia = pd.DataFrame({
        "id_familia": df["id_estudiante"],
        "tamano_familia": df["famsize"].map({"LE3": "3 o menos", "GT3": "Más de 3"}),
        "estado_padres": df["Pstatus"].map({"T": "Juntos", "A": "Separados"}),
        "escolaridad_madre": df["Medu"].map(ESCOLARIDAD),
        "escolaridad_padre": df["Fedu"].map(ESCOLARIDAD),
        "trabajo_madre": df["Mjob"].map(TRABAJOS),
        "trabajo_padre": df["Fjob"].map(TRABAJOS),
        "tutor": df["guardian"].map(TUTORES),
        "apoyo_familiar": df["famsup"].map(SI_NO),
        "relacion_familiar": df["famrel"],
    })
    dim_habitos = pd.DataFrame({
        "id_habitos": df["id_estudiante"],
        "tiempo_estudio": df["studytime"],
        "tiempo_traslado": df["traveltime"],
        "tiempo_libre": df["freetime"],
        "salidas_amigos": df["goout"],
        "alcohol_entre_semana": df["Dalc"],
        "alcohol_fin_semana": df["Walc"],
        "actividades_extra": df["activities"].map(SI_NO),
        "apoyo_escolar": df["schoolsup"].map(SI_NO),
        "clases_pagadas": df["paid"].map(SI_NO),
    })
    fact_rendimiento = pd.DataFrame({
        "id_hecho": df["id_estudiante"],
        "id_estudiante": df["id_estudiante"],
        "id_escuela": df["school"].map({"GP": 1, "MS": 2}),
        "id_familia": df["id_estudiante"],
        "id_habitos": df["id_estudiante"],
        "id_desempeno": df["nivel_desempeno"].map({"Bajo": 1, "Medio": 2, "Alto": 3}),
        "g1": df["G1"],
        "g2": df["G2"],
        "g3": df["G3"],
        "faltas": df["absences"],
        "reprobadas_previas": df["failures"],
        "aprobado": df["aprobado"],
        "abandono": df["abandono"],
    })
    return {
        "dim_escuela": dim_escuela,
        "dim_desempeno": dim_desempeno,
        "dim_estudiante": dim_estudiante,
        "dim_familia": dim_familia,
        "dim_habitos": dim_habitos,
        "fact_rendimiento": fact_rendimiento,
    }


# -------------------------------------------------------------------- LOAD
def valor_sql(v):
    if pd.isna(v):
        return "NULL"
    if isinstance(v, str):
        return "N'" + v.replace("'", "''") + "'"
    return str(v)


def generar_sql(tablas, ruta=SQL_CARGA):
    """Script de INSERTs para ejecutar en SSMS después de 01_crear_datamart.sql."""
    lineas = ["-- Carga del Data Mart generada por src/etl.py", "USE DM_RendimientoEstudiantil;",
              "GO", ""]
    for nombre, tabla in tablas.items():
        columnas = ", ".join(tabla.columns)
        lineas.append(f"-- {nombre}: {len(tabla)} registros")
        filas = [f"({', '.join(valor_sql(v) for v in fila)})"
                 for fila in tabla.itertuples(index=False)]
        # SQL Server permite máximo 1000 filas por INSERT
        for i in range(0, len(filas), 500):
            lineas.append(f"INSERT INTO dbo.{nombre} ({columnas}) VALUES")
            lineas.append(",\n".join(filas[i:i + 500]) + ";")
        lineas.append("GO\n")
    ruta.write_text("\n".join(lineas), encoding="utf-8")


def cargar(df_limpio, df_modelo, df_escalado, tablas):
    DATAMART.mkdir(parents=True, exist_ok=True)
    df_limpio.to_csv(PROCESSED / "student_por_limpio.csv", index=False)
    df_modelo.to_csv(PROCESSED / "student_por_modelo.csv", index=False)
    df_escalado.to_csv(PROCESSED / "student_por_escalado.csv", index=False)
    for nombre, tabla in tablas.items():
        tabla.to_csv(DATAMART / f"{nombre}.csv", index=False)
    generar_sql(tablas)


def main():
    df = extraer()
    df_limpio = limpiar(df)
    df_modelo = codificar(df_limpio)
    df_escalado = escalar(df_modelo)
    tablas = tablas_datamart(df_limpio)
    cargar(df_limpio, df_modelo, df_escalado, tablas)
    print(f"ETL terminado: {len(df_limpio)} limpios, {len(df_modelo)} para modelado.")


if __name__ == "__main__":
    main()
