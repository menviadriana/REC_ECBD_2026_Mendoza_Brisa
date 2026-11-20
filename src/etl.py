"""
ETL del proyecto: Análisis del rendimiento académico de estudiantes
Dataset: Student Performance (UCI) - archivo student-por.csv

Extract   -> lee el CSV original de data/raw (sin modificarlo)
Transform -> limpia, crea variables derivadas y codifica
Load      -> guarda los archivos en data/processed Y carga automáticamente
             el Data Mart en SQL Server (localhost\\SQLEXPRESS) usando pyodbc

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

# Configuración de SQL Server
SERVIDOR = r"localhost\SQLEXPRESS"
BASE_DATOS = "DM_RendimientoEstudiantil"
DRIVER = "{ODBC Driver 17 for SQL Server}"


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

def _conectar_sqlserver(base=None):
    """Abre una conexión a SQL Server con pyodbc."""
    import pyodbc
    cadena = f"DRIVER={DRIVER};SERVER={SERVIDOR};Trusted_Connection=yes;"
    if base:
        cadena += f"DATABASE={base};"
    conn = pyodbc.connect(cadena, autocommit=True)
    return conn


def _crear_base_datos():
    """Crea la base de datos si no existe."""
    conn = _conectar_sqlserver()
    cursor = conn.cursor()
    cursor.execute(f"""
        IF DB_ID('{BASE_DATOS}') IS NULL
            CREATE DATABASE [{BASE_DATOS}];
    """)
    cursor.close()
    conn.close()


DDL_TABLAS = """
-- Se borran en orden inverso para respetar las llaves foráneas
DROP TABLE IF EXISTS dbo.fact_rendimiento;
DROP TABLE IF EXISTS dbo.dim_estudiante;
DROP TABLE IF EXISTS dbo.dim_familia;
DROP TABLE IF EXISTS dbo.dim_habitos;
DROP TABLE IF EXISTS dbo.dim_escuela;
DROP TABLE IF EXISTS dbo.dim_desempeno;

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
    salud                      TINYINT      NOT NULL
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
    relacion_familiar TINYINT      NOT NULL
);

CREATE TABLE dbo.dim_habitos (
    id_habitos           INT         NOT NULL PRIMARY KEY,
    tiempo_estudio       TINYINT     NOT NULL,
    tiempo_traslado      TINYINT     NOT NULL,
    tiempo_libre         TINYINT     NOT NULL,
    salidas_amigos       TINYINT     NOT NULL,
    alcohol_entre_semana TINYINT     NOT NULL,
    alcohol_fin_semana   TINYINT     NOT NULL,
    actividades_extra    NVARCHAR(2) NOT NULL,
    apoyo_escolar        NVARCHAR(2) NOT NULL,
    clases_pagadas       NVARCHAR(2) NOT NULL
);

CREATE TABLE dbo.fact_rendimiento (
    id_hecho           INT     NOT NULL PRIMARY KEY,
    id_estudiante      INT     NOT NULL REFERENCES dbo.dim_estudiante(id_estudiante),
    id_escuela         INT     NOT NULL REFERENCES dbo.dim_escuela(id_escuela),
    id_familia         INT     NOT NULL REFERENCES dbo.dim_familia(id_familia),
    id_habitos         INT     NOT NULL REFERENCES dbo.dim_habitos(id_habitos),
    id_desempeno       INT     NOT NULL REFERENCES dbo.dim_desempeno(id_desempeno),
    g1                 TINYINT NOT NULL,
    g2                 TINYINT NOT NULL,
    g3                 TINYINT NOT NULL,
    faltas             TINYINT NOT NULL,
    reprobadas_previas TINYINT NOT NULL,
    aprobado           BIT     NOT NULL,
    abandono           BIT     NOT NULL
);
"""


def _crear_tablas(conn):
    """Ejecuta el DDL para crear las 6 tablas del modelo estrella."""
    cursor = conn.cursor()
    # Primero borrar: hechos antes que dimensiones (por las FK)
    for tabla in ["fact_rendimiento", "dim_estudiante", "dim_familia",
                  "dim_habitos", "dim_escuela", "dim_desempeno"]:
        cursor.execute(f"DROP TABLE IF EXISTS dbo.{tabla}")
    # Después crear: dimensiones antes que hechos (para que las FK funcionen)
    for sentencia in DDL_TABLAS.split(";"):
        sentencia = sentencia.strip()
        if sentencia and sentencia.upper().startswith("CREATE"):
            cursor.execute(sentencia)
    cursor.close()


def _insertar_tabla(conn, nombre, df):
    """Inserta los registros de un DataFrame en la tabla correspondiente."""
    if len(df) == 0:
        return
    columnas = ", ".join(df.columns)
    placeholders = ", ".join(["?"] * len(df.columns))
    sql = f"INSERT INTO dbo.{nombre} ({columnas}) VALUES ({placeholders})"
    cursor = conn.cursor()
    # Convierte el DataFrame a lista de tuplas
    datos = [tuple(fila) for fila in df.itertuples(index=False)]
    cursor.executemany(sql, datos)
    cursor.close()
    print(f"  -> {nombre}: {len(datos)} registros insertados")


def cargar_sqlserver(tablas):
    """
    Carga automática del Data Mart en SQL Server:
    1. Crea la base de datos DM_RendimientoEstudiantil (si no existe)
    2. Elimina y recrea las 6 tablas (carga full: DROP + CREATE)
    3. Inserta todos los registros con pyodbc

    Requiere: pip install pyodbc
    Servidor: localhost\\SQLEXPRESS con autenticación de Windows
    """
    print("Conectando a SQL Server...")
    _crear_base_datos()
    conn = _conectar_sqlserver(BASE_DATOS)
    print("Creando tablas del Data Mart...")
    _crear_tablas(conn)
    print("Insertando datos...")
    # Orden: dimensiones primero (por las FK), hechos al final
    orden = ["dim_escuela", "dim_desempeno", "dim_estudiante",
             "dim_familia", "dim_habitos", "fact_rendimiento"]
    for nombre in orden:
        _insertar_tabla(conn, nombre, tablas[nombre])
    conn.close()
    print("Data Mart cargado exitosamente en SQL Server.")


def limpiar_base_datos():
    """
    Borra TODAS las tablas y la base de datos del Data Mart.
    Usar antes de demostrar el ETL al profesor.
    Uso: python src/etl.py --limpiar
    """
    print("Limpiando base de datos...")
    try:
        conn = _conectar_sqlserver(BASE_DATOS)
        cursor = conn.cursor()
        for tabla in ["fact_rendimiento", "dim_estudiante", "dim_familia",
                      "dim_habitos", "dim_escuela", "dim_desempeno"]:
            cursor.execute(f"DROP TABLE IF EXISTS dbo.{tabla}")
        cursor.close()
        conn.close()
        print(f"  Tablas eliminadas de {BASE_DATOS}.")
    except Exception:
        pass
    # Borrar la base de datos completa
    conn = _conectar_sqlserver()
    cursor = conn.cursor()
    cursor.execute(f"""
        IF DB_ID('{BASE_DATOS}') IS NOT NULL
        BEGIN
            ALTER DATABASE [{BASE_DATOS}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
            DROP DATABASE [{BASE_DATOS}];
        END
    """)
    cursor.close()
    conn.close()
    print(f"  Base de datos {BASE_DATOS} eliminada.")
    print("Listo. Ahora ejecuta: python src/etl.py")


def cargar_csv(df_limpio, df_modelo, df_escalado, tablas):
    """Guarda los archivos CSV en data/processed."""
    DATAMART.mkdir(parents=True, exist_ok=True)
    df_limpio.to_csv(PROCESSED / "student_por_limpio.csv", index=False)
    df_modelo.to_csv(PROCESSED / "student_por_modelo.csv", index=False)
    df_escalado.to_csv(PROCESSED / "student_por_escalado.csv", index=False)
    for nombre, tabla in tablas.items():
        tabla.to_csv(DATAMART / f"{nombre}.csv", index=False)


def main():
    # --- EXTRACT ---
    print("=" * 60)
    print("ETL - Análisis del rendimiento académico de estudiantes")
    print("=" * 60)
    print("\n[1/4] Extrayendo datos de", RAW.name, "...")
    df = extraer()
    print(f"      {len(df)} registros x {df.shape[1]} columnas")

    # --- TRANSFORM ---
    print("\n[2/4] Transformando datos...")
    df_limpio = limpiar(df)
    print(f"      Limpio: {len(df_limpio)} registros ({df_limpio['abandono'].sum()} abandonos marcados)")
    df_modelo = codificar(df_limpio)
    print(f"      Modelado: {len(df_modelo)} registros (sin abandonos)")
    df_escalado = escalar(df_modelo)
    print(f"      Escalado: {len(df_escalado)} registros")
    tablas = tablas_datamart(df_limpio)
    print(f"      Data Mart: {len(tablas)} tablas construidas")

    # --- LOAD: archivos CSV ---
    print("\n[3/4] Guardando archivos CSV en data/processed/...")
    cargar_csv(df_limpio, df_modelo, df_escalado, tablas)
    print("      Archivos CSV guardados.")

    # --- LOAD: SQL Server ---
    print("\n[4/4] Cargando Data Mart en SQL Server...")
    try:
        cargar_sqlserver(tablas)
    except ImportError:
        print("      ERROR: pyodbc no está instalado.")
        print("      Instálalo con: pip install pyodbc")
        print("      Los archivos CSV se guardaron correctamente.")
    except Exception as e:
        print(f"      ERROR al conectar a SQL Server: {e}")
        print("      Verifica que SQL Server esté corriendo y que el servicio")
        print("      SQLEXPRESS esté iniciado (Get-Service MSSQL*)")
        print("      Los archivos CSV se guardaron correctamente.")

    print("\n" + "=" * 60)
    print(f"ETL terminado: {len(df_limpio)} limpios, {len(df_modelo)} para modelado.")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    if "--limpiar" in sys.argv:
        limpiar_base_datos()
    else:
        main()
