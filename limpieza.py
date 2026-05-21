# ============================================================
#  LIMPIEZA PRE-RECORD LINKAGE — Cruz Azul Intelligence
#  Datasets: LigaMX · Transfermarkt · FIFA 23 · OpenPublicDomain
# ============================================================

import os
import glob
import re
import unicodedata

import numpy as np
import pandas as pd

# ── Rutas ────────────────────────────────────────────────────
BASE  = os.path.abspath(os.path.join(os.getcwd(), ".."))
RAW   = os.path.join(BASE, "Datos_originales")
MOD   = os.path.join(BASE, "Datos_modificados")
CLEAN = os.path.join(BASE, "Datos_limpios")
os.makedirs(CLEAN, exist_ok=True)


# ╔══════════════════════════════════════════════════════════╗
#  FUNCIONES UTILITARIAS
# ╚══════════════════════════════════════════════════════════╝

def resumen(df: pd.DataFrame, nombre: str) -> None:
    """Imprime métricas de calidad básicas (DAMA-DMBOK)."""
    total = df.shape[0] * df.shape[1]
    nulos = df.isnull().sum().sum()
    dupes = df.duplicated().sum()
    print(f"\n{'─'*55}")
    print(f"  {nombre}")
    print(f"  Filas        : {df.shape[0]:>8,}")
    print(f"  Columnas     : {df.shape[1]:>8}")
    print(f"  Nulos        : {nulos:>8,}  ({nulos/total*100:.1f} %)")
    print(f"  Duplicados   : {dupes:>8,}  ({dupes/df.shape[0]*100:.1f} %)")
    cols_nulas = df.columns[df.isnull().any()].tolist()
    if cols_nulas:
        pct = (df[cols_nulas].isnull().mean() * 100).round(1)
        print("  Columnas con nulos:")
        for col, p in pct.items():
            print(f"    {col:<45} {p:>5.1f} %")


def normalizar_texto(texto) -> "str | float":
    """
    Normalización canónica para strings (jugadores, países, etc.):
      - strip · minúsculas · elimina acentos/diacríticos
      - colapsa espacios múltiples
      - elimina puntuación excepto espacios
    Retorna np.nan si el valor está ausente.
    """
    if pd.isna(texto):
        return np.nan
    s = str(texto).strip().lower()
    # Descomponer Unicode y descartar marcas de acento
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    # Solo letras, dígitos y espacios
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    # Colapsar espacios
    return re.sub(r"\s+", " ", s).strip()


def normalizar_nombre(texto) -> "str | float":
    """
    Normalización para nombres propios usados como clave de bloqueo en RL.
    Igual que normalizar_texto pero en MAYÚSCULAS (convención de linkage).
    """
    resultado = normalizar_texto(texto)
    if pd.isna(resultado):
        return np.nan
    return resultado.upper()


# Diccionario de variantes → nombre canónico de equipos Liga MX
_ALIAS_EQUIPOS: dict[str, str] = {
    # Cruz Azul
    "cruz azul"             : "CRUZ AZUL",
    "la maquina"            : "CRUZ AZUL",
    "la maquina celeste"    : "CRUZ AZUL",
    # America
    "america"               : "CLUB AMERICA",
    "aguilas"               : "CLUB AMERICA",
    "aguilas america"       : "CLUB AMERICA",
    "club america"          : "CLUB AMERICA",
    # Chivas
    "guadalajara"           : "CHIVAS GUADALAJARA",
    "chivas"                : "CHIVAS GUADALAJARA",
    "deportivo guadalajara" : "CHIVAS GUADALAJARA",
    "chivas guadalajara"    : "CHIVAS GUADALAJARA",
    # Tigres
    "tigres"                : "TIGRES UANL",
    "uanl"                  : "TIGRES UANL",
    "tigres uanl"           : "TIGRES UANL",
    # Monterrey
    "monterrey"             : "MONTERREY",
    "rayados"               : "MONTERREY",
    "rayados de monterrey"  : "MONTERREY",
    # Pumas
    "pumas"                 : "PUMAS UNAM",
    "unam"                  : "PUMAS UNAM",
    "pumas unam"            : "PUMAS UNAM",
    # Atlas
    "atlas"                 : "ATLAS",
    "atlas guadalajara"     : "ATLAS",
    # Necaxa
    "necaxa"                : "NECAXA",
    "rayos"                 : "NECAXA",
    "rayos del necaxa"      : "NECAXA",
    # Santos
    "santos"                : "SANTOS LAGUNA",
    "santos laguna"         : "SANTOS LAGUNA",
    # Toluca
    "toluca"                : "TOLUCA",
    "diablos rojos"         : "TOLUCA",
    # Pachuca
    "pachuca"               : "PACHUCA",
    "tuzos"                 : "PACHUCA",
    # Leon
    "leon"                  : "LEON",
    "club leon"             : "LEON",
    # Tijuana
    "tijuana"               : "TIJUANA",
    "club tijuana"          : "TIJUANA",
    "xolos"                 : "TIJUANA",
    # Mazatlan
    "mazatlan"              : "MAZATLAN FC",
    "mazatlan fc"           : "MAZATLAN FC",
    # Puebla
    "puebla"                : "PUEBLA",
    "club puebla"           : "PUEBLA",
    # FC Juarez
    "fc juarez"             : "FC JUAREZ",
    "juarez"                : "FC JUAREZ",
    # Queretaro
    "queretaro"             : "QUERETARO",
    # San Luis
    "atletico san luis"     : "ATLETICO SAN LUIS",
    "san luis"              : "ATLETICO SAN LUIS",
}

# Palabras genéricas que se eliminan antes de buscar en el alias dict
_STOPWORDS_EQUIPOS = [
    r"\bf\.?c\.?\b", r"\bc\.?f\.?\b", r"\ba\.?c\.?\b",
    r"\bs\.?a\.?\b", r"\bde\b",  r"\blos\b", r"\blas\b",
    r"\bel\b",       r"\bla\b",
]


def normalizar_equipo(nombre) -> "str | float":
    """
    Normalización de nombres de clubes/equipos.
      1. Aplica normalizar_texto (minúsculas, sin acentos).
      2. Elimina stopwords genéricas (FC, CF, AC, etc.).
      3. Busca en el diccionario de alias;
         si no está, devuelve el texto limpio en MAYÚSCULAS.
    """
    if pd.isna(nombre):
        return np.nan
    s = normalizar_texto(nombre)           # minúsculas, sin acentos
    for pat in _STOPWORDS_EQUIPOS:
        s = re.sub(pat, "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return _ALIAS_EQUIPOS.get(s, s.upper())


# Tabla de equivalencia FIFA 23 <-> Transfermarkt para posiciones
_EQUIV_POSICIONES: dict[str, str] = {
    "GK"  : "Goalkeeper",
    "SW"  : "Sweeper",
    "RB"  : "Right-Back",
    "LB"  : "Left-Back",
    "CB"  : "Centre-Back",
    "RWB" : "Right Wing Back",
    "LWB" : "Left Wing Back",
    "CDM" : "Defensive Midfield",
    "CM"  : "Central Midfield",
    "RM"  : "Right Midfield",
    "LM"  : "Left Midfield",
    "CAM" : "Attacking Midfield",
    "RW"  : "Right Winger",
    "LW"  : "Left Winger",
    "CF"  : "Centre-Forward",
    "ST"  : "Centre-Forward",
    "RF"  : "Right Winger",
    "LF"  : "Left Winger",
}


def normalizar_posicion(valor) -> "str | float":
    """
    Traduce abreviaturas FIFA 23 al vocabulario canónico de Transfermarkt.
    Si el valor ya es un nombre largo (viene de TM), lo retorna sin cambios.
    """
    if pd.isna(valor):
        return np.nan
    s = str(valor).strip().upper()
    return _EQUIV_POSICIONES.get(s, valor)


def exportar(df: pd.DataFrame, directorio: str, nombre_archivo: str) -> None:
    """Exporta el DataFrame a Parquet en el directorio indicado."""
    os.makedirs(directorio, exist_ok=True)
    if not nombre_archivo.endswith(".parquet"):
        nombre_archivo = nombre_archivo.rstrip(".") + ".parquet"
    ruta = os.path.join(directorio, nombre_archivo)
    df.to_parquet(ruta, index=False)
    print(f"\n  Exportado -> {ruta}  ({len(df):,} filas)")


# ╔══════════════════════════════════════════════════════════╗
#  1. FIFA 23 — male_players  (TXT separado por tabulaciones)
# ╚══════════════════════════════════════════════════════════╝

def limpiar_fifa_players() -> pd.DataFrame:
    """
    Limpieza de jugadores FIFA 23 (male_players).

    Problemas identificados:
      - Archivo enorme (cientos de miles de filas); se filtra a
        seleccion mexicana (nationality_name == 'Mexico') antes
        de procesar en detalle -> reduce memoria y tiempo.
      - player_positions puede traer multiples abreviaturas
        separadas por coma ('ST, CF') -> se toma la primera.
      - Columnas de URLs y atributos de portero son irrelevantes
        para jugadores de campo.
      - dob viene como string YYYY-MM-DD.

    Acciones:
      1. Leer con low_memory=False para evitar DtypeWarning.
      2. Filtrar a jugadores mexicanos por nationality_name.
      3. Extraer posicion principal de player_positions.
      4. Crear name_key y dob_key para bloqueo en RL.
      5. Convertir value_eur / wage_eur a numerico.
      6. Normalizar club_name y nationality_name.
      7. Eliminar URLs, ratings posicionales redundantes y GK attrs.
      8. Eliminar duplicados por (player_id, fifa_version, fifa_update).
    """
    ruta = os.path.join(MOD, "FIFA23complete_player_dataset",
                        "male_players (legacy).txt")
    df = pd.read_csv(ruta, sep="\t", low_memory=False, encoding="utf-8")
    resumen(df, "ANTES — FIFA23 Players (completo)")

    # 1. Filtrar seleccion mexicana
    if "nationality_name" in df.columns:
        df = df[df["nationality_name"].str.strip().str.lower() == "mexico"].copy()
        print(f"  -> Filtrado a jugadores mexicanos: {len(df):,} filas")
    else:
        print("  AVISO: Columna 'nationality_name' no encontrada; "
              "se procesa sin filtro.")

    # 2. Eliminar duplicados por clave compuesta
    id_cols = [c for c in ["player_id", "fifa_version", "fifa_update"]
               if c in df.columns]
    if id_cols:
        antes = len(df)
        df.drop_duplicates(subset=id_cols, keep="last", inplace=True)
        print(f"  -> Duplicados eliminados: {antes - len(df)}")

    # 3. Posicion principal (primer token de player_positions)
    if "player_positions" in df.columns:
        df["main_position"] = (
            df["player_positions"]
            .astype(str)
            .str.split(",")
            .str[0]
            .str.strip()
            .apply(normalizar_posicion)
        )

    # 4. Claves para RL
    df["name_key"]       = df["long_name"].apply(normalizar_nombre)
    df["short_name_key"] = df["short_name"].apply(normalizar_nombre)
    if "dob" in df.columns:
        df["dob"] = pd.to_datetime(df["dob"], errors="coerce")
        df["dob_key"] = df["dob"].dt.strftime("%Y-%m-%d")
    else:
        df["dob_key"] = np.nan

    # 5. Valores monetarios a numerico
    for col in ["value_eur", "wage_eur", "release_clause_eur"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 6. Normalizar campos de texto utiles para analisis
    if "club_name" in df.columns:
        df["club_name_norm"] = df["club_name"].apply(normalizar_equipo)
    if "nationality_name" in df.columns:
        df["nationality_name"] = df["nationality_name"].apply(normalizar_nombre)

    # 7. Eliminar columnas innecesarias:
    #    - ratings por posicion (ls, st, rs, etc.)
    #    - atributos de portero (salvo goalkeeping_diving como referencia)
    #    - URLs de imagenes
    #    - tags / traits (texto libre sin valor estadistico)
    _RATING_POSITIONS = {"ls","st","rs","lw","lf","cf","rf","rw",
                         "lam","cam","ram","lm","lcm","cm","rcm",
                         "rm","lwb","ldm","cdm","rdm","rwb","lb",
                         "lcb","cb","rcb","rb","gk"}
    gk_attrs     = [c for c in df.columns
                    if c.startswith("goalkeeping_") and c != "goalkeeping_diving"]
    url_cols     = [c for c in df.columns if "url" in c.lower()]
    rating_p_cols = [c for c in df.columns if c.lower() in _RATING_POSITIONS]
    misc_cols    = ["player_tags", "player_traits"]

    cols_drop = list(set(gk_attrs + url_cols + rating_p_cols +
                         [c for c in misc_cols if c in df.columns]))
    df.drop(columns=[c for c in cols_drop if c in df.columns], inplace=True)

    df.reset_index(drop=True, inplace=True)
    resumen(df, "DESPUES — FIFA23 Players (Mexico)")
    exportar(df, os.path.join(CLEAN, "FIFA23"),
             "fifa23_players_mexico_clean.parquet")
    return df


# ╔══════════════════════════════════════════════════════════╗
#  2. LigaMX 2016-2024  (JSON)
# ╚══════════════════════════════════════════════════════════╝

def limpiar_ligamx() -> pd.DataFrame:
    """
    Limpieza de partidos LigaMX 2016-2024.

    Problemas identificados:
      - 22.4 % de nulos: venue_id/city, home/away_win,
        goles extra_time (~99 %) y penales (~99 %).
      - 'timezone' constante -> columna inutil.
      - 'date' llega como string -> parsear a datetime.
      - home_goals_fulltime == home_goals en partidos normales
        -> verificar y eliminar redundante.
      - Inconsistencia de nombres entre temporadas.

    Acciones:
      1. Parsear 'date' y crear date_key YYYY-MM-DD.
      2. Convertir goles extra_time / penalty a int (NaN -> 0).
      3. Normalizar home_team / away_team -> columnas _norm.
      4. Eliminar 'timezone' y columnas fulltime redundantes.
      5. Imputar venue_city faltante con 'DESCONOCIDA'.
      6. Crear result_home ('W'/'D'/'L') para analisis P3/P8.
      7. Eliminar duplicados exactos.
    """
    ruta = os.path.join(MOD, "LigaMX", "2016-2024_liga_mx.json")
    df = pd.read_json(ruta)
    resumen(df, "ANTES — LigaMX")

    # 1. Fecha
    df["date"]     = pd.to_datetime(df["date"], errors="coerce", utc=True)
    df["date_key"] = df["date"].dt.strftime("%Y-%m-%d")
    df["season"]   = df["season"].astype("Int64")

    # 2. Goles extra_time y penales -> int (relleno 0)
    for col in ["home_goals_extra_time", "away_goals_extratime",
                "home_goals_penalty",    "away_goals_penalty"]:
        if col in df.columns:
            df[col] = (pd.to_numeric(df[col], errors="coerce")
                       .fillna(0).astype(int))

    # 3. Normalizar nombres de equipos
    df["home_team_norm"] = df["home_team"].apply(normalizar_equipo)
    df["away_team_norm"] = df["away_team"].apply(normalizar_equipo)

    # 4. Columnas a eliminar
    cols_drop = ["timezone"]
    # fulltime duplica goals cuando no hay prorroga -> comparar y eliminar si iguales
    for base, full in [("home_goals", "home_goals_fulltime"),
                       ("away_goals", "away_goals_fulltime")]:
        if base in df.columns and full in df.columns:
            # Comparar rellenando NaN con centinela -1
            if df[base].fillna(-1).equals(df[full].fillna(-1)):
                cols_drop.append(full)
    df.drop(columns=[c for c in cols_drop if c in df.columns], inplace=True)

    # 5. Imputar venue_city
    df["venue_city"] = df["venue_city"].fillna("DESCONOCIDA")

    # 6. Resultado desde perspectiva local
    if {"home_goals", "away_goals"}.issubset(df.columns):
        def _result(row):
            h, a = row["home_goals"], row["away_goals"]
            if pd.isna(h) or pd.isna(a):
                return np.nan
            if h > a:  return "W"
            if h < a:  return "L"
            return "D"
        df["result_home"] = df.apply(_result, axis=1)

    # 7. Eliminar duplicados exactos
    antes = len(df)
    df.drop_duplicates(inplace=True)
    print(f"  -> Duplicados eliminados: {antes - len(df)}")

    df.reset_index(drop=True, inplace=True)
    resumen(df, "DESPUES — LigaMX")
    exportar(df, os.path.join(CLEAN, "LigaMX"), "ligamx_clean.parquet")
    return df


# ╔══════════════════════════════════════════════════════════╗
#  3. Transfermarkt players  (XLSX)
# ╚══════════════════════════════════════════════════════════╝

def _impute_by_group(df: pd.DataFrame, target_col: str,
                     group_col: str, strategy: str = "median") -> pd.Series:
    """
    Imputa nulos en target_col usando la mediana o moda del grupo group_col.
    strategy: 'median' para numerico, 'mode' para categorico.
    Retorna la serie imputada (NO modifica df in-place).

    NOTA: evita el uso de apply() fila a fila que degradaba el rendimiento
    en el script original (47 k filas x 3 llamadas = ~140 k iteraciones).
    """
    if target_col not in df.columns or group_col not in df.columns:
        return df.get(target_col, pd.Series(dtype=object))

    if strategy == "median":
        lookup = (df.dropna(subset=[target_col])
                    .groupby(group_col)[target_col]
                    .median())
    else:  # mode
        lookup = (df.dropna(subset=[target_col])
                    .groupby(group_col)[target_col]
                    .agg(lambda x: x.mode().iloc[0]
                         if not x.mode().empty else np.nan))

    serie = df[target_col].copy()
    mask  = serie.isna() & df[group_col].isin(lookup.index)
    serie.loc[mask] = df.loc[mask, group_col].map(lookup)
    return serie


def limpiar_transfermarkt() -> pd.DataFrame:
    """
    Limpieza de jugadores Transfermarkt.

    Problemas identificados:
      - 14.8 % de nulos: first_name, city_of_birth, agent_name,
        contract_expiration_date, market_value, caps/goals,
        foot, height_in_cm, current_national_team_id.
      - Fechas como strings.
      - Nombres con diacriticos -> inconsistencia en RL.
      - image_url / player_code / agent_name -> irrelevantes.
      - international_caps/goals: 63 % nulos; se imputan con 0.

    Acciones:
      1. Parsear fechas (date_of_birth, contract_expiration_date).
      2. Crear name_key, first_name_key, last_name_key, dob_key.
      3. Normalizar country_of_citizenship y country_of_birth.
      4. Imputar foot (moda/sub_position) y height_in_cm
         (mediana/sub_position) — vectorizado con _impute_by_group.
      5. Imputar market_value_in_eur (mediana/sub_position).
      6. Imputar international_caps / international_goals con 0.
      7. Normalizar columnas de posicion al vocabulario canonico.
      8. Eliminar columnas irrelevantes.
      9. Eliminar duplicados por player_id.
    """
    ruta = os.path.join(MOD, "FootballDatafromTransfermarkt", "players.xlsx")
    df = pd.read_excel(ruta, engine="openpyxl")
    resumen(df, "ANTES — Transfermarkt")

    # 1. Parsear fechas
    for col_fecha in ["date_of_birth", "contract_expiration_date"]:
        if col_fecha in df.columns:
            df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")

    # 2. Claves para RL
    df["name_key"]       = df["name"].apply(normalizar_nombre)
    df["first_name_key"] = df["first_name"].apply(normalizar_nombre)
    df["last_name_key"]  = df["last_name"].apply(normalizar_nombre)
    df["dob_key"] = (df["date_of_birth"].dt.strftime("%Y-%m-%d")
                     if "date_of_birth" in df.columns else np.nan)

    # 3. Normalizar paises
    for col in ["country_of_citizenship", "country_of_birth"]:
        if col in df.columns:
            df[col] = df[col].apply(normalizar_nombre)

    # 4. Imputar foot y height (vectorizado, sin apply fila a fila)
    df["foot"]         = _impute_by_group(df, "foot",         "sub_position", "mode")
    df["height_in_cm"] = _impute_by_group(df, "height_in_cm", "sub_position", "median")

    # 5. Imputar market_value
    df["market_value_in_eur"] = _impute_by_group(
        df, "market_value_in_eur", "sub_position", "median"
    )

    # 6. Caps / goals internacionales: NaN -> 0
    for col in ["international_caps", "international_goals"]:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype("Int64")

    # 7. Normalizar posiciones
    for col in ["position", "sub_position"]:
        if col in df.columns:
            df[col] = df[col].apply(normalizar_posicion)

    # 8. Eliminar columnas irrelevantes para RL y analisis
    cols_drop = ["image_url", "player_code", "agent_name",
                 "current_national_team_id",
                 "current_club_domestic_competition_id"]
    df.drop(columns=[c for c in cols_drop if c in df.columns], inplace=True)

    # 9. Duplicados por player_id
    if "player_id" in df.columns:
        antes = len(df)
        df.drop_duplicates(subset=["player_id"], keep="last", inplace=True)
        print(f"  -> Duplicados por player_id eliminados: {antes - len(df)}")

    df.reset_index(drop=True, inplace=True)
    resumen(df, "DESPUES — Transfermarkt")
    exportar(df, os.path.join(CLEAN, "Transfermarkt"),
             "transfermarkt_players_clean.parquet")
    return df


# ╔══════════════════════════════════════════════════════════╗
#  4. OpenPublicDomain — partidos historicos (CSV multi-temporada)
# ╚══════════════════════════════════════════════════════════╝

def _split_score(score_str) -> tuple:
    """'2-1' -> (2, 1) como int. Formato invalido -> (nan, nan)."""
    if pd.isna(score_str):
        return np.nan, np.nan
    partes = str(score_str).strip().split("-")
    if len(partes) != 2:
        return np.nan, np.nan
    try:
        return int(partes[0]), int(partes[1])
    except ValueError:
        return np.nan, np.nan


def limpiar_opfd() -> pd.DataFrame:
    """
    Limpieza de partidos historicos OpenPublicDomainFootballData.

    Problemas identificados:
      - 24.2 % de nulos: Time, Timezone, HT, FT, UTC,
        ET (99.8 %), P (99.5 %), Comments (97 %).
      - 'Round' marcado como Unsupported en profiling.
      - FT y HT en formato '2-1' -> separar en columnas numericas.
      - Nombres de equipos distintos a LigaMX.
      - Timezone: mezcla 'CDT', '-0500', etc.

    Acciones:
      1. Leer y concatenar todos los archivos mx.1.csv.
      2. Renombrar columnas a snake_case.
      3. Parsear Date -> datetime y date_key.
      4. Separar FT -> ft_home_goals / ft_away_goals (int).
      5. Separar HT -> ht_home_goals / ht_away_goals (int, acepta NaN).
      6. Normalizar home_team / away_team -> columnas _norm.
      7. Crear result_home para joins con LigaMX.
      8. Eliminar: timezone, utc, et, penalties, comments,
                   ft, ht (raw), time, round_raw.
      9. Eliminar duplicados exactos.
    """
    patron = os.path.join(RAW, "OpenPublicDomainFootballData", "*", "mx.1.csv")
    archivos = sorted(glob.glob(patron))
    if not archivos:
        raise FileNotFoundError(
            f"No se encontraron archivos mx.1.csv bajo:\n  {patron}\n"
            "Verifica la ruta RAW y la estructura de carpetas."
        )
    df = pd.concat(
        [pd.read_csv(f, encoding="utf-8", na_values=["", " ", "N/A"])
         for f in archivos],
        ignore_index=True
    )
    print(f"  Archivos cargados : {len(archivos)} temporadas")
    resumen(df, "ANTES — OpenPublicDomain")

    # 1. Renombrar a snake_case
    rename_map = {
        "Stage"   : "stage",
        "Round"   : "round_raw",   # Unsupported -> guardar pero no usar en RL
        "Date"    : "date",
        "Time"    : "time",
        "Timezone": "timezone",
        "Team 1"  : "home_team",
        "FT"      : "ft",
        "HT"      : "ht",
        "Team 2"  : "away_team",
        "UTC"     : "utc",
        "ET"      : "et",
        "P"       : "penalties",
        "Comments": "comments",
    }
    df.rename(columns={k: v for k, v in rename_map.items()
                       if k in df.columns}, inplace=True)

    # 2. Fecha
    if "date" in df.columns:
        df["date"]     = pd.to_datetime(df["date"], errors="coerce", dayfirst=False)
        df["date_key"] = df["date"].dt.strftime("%Y-%m-%d")
        df["season"]   = df["date"].dt.year  # aproximacion de temporada

    # 3. Separar marcadores FT y HT
    if "ft" in df.columns:
        df[["ft_home_goals", "ft_away_goals"]] = \
            df["ft"].apply(lambda x: pd.Series(_split_score(x)))
    if "ht" in df.columns:
        df[["ht_home_goals", "ht_away_goals"]] = \
            df["ht"].apply(lambda x: pd.Series(_split_score(x)))

    # 4. Normalizar nombres de equipos
    for col in ["home_team", "away_team"]:
        if col in df.columns:
            df[f"{col}_norm"] = df[col].apply(normalizar_equipo)

    # 5. Resultado desde perspectiva local
    if {"ft_home_goals", "ft_away_goals"}.issubset(df.columns):
        def _result(row):
            h, a = row["ft_home_goals"], row["ft_away_goals"]
            if pd.isna(h) or pd.isna(a): return np.nan
            if h > a:  return "W"
            if h < a:  return "L"
            return "D"
        df["result_home"] = df.apply(_result, axis=1)

    # 6. Eliminar columnas dispersas o irrelevantes para RL
    cols_drop = ["timezone", "utc", "et", "penalties", "comments",
                 "ft", "ht", "time", "round_raw"]
    df.drop(columns=[c for c in cols_drop if c in df.columns], inplace=True)

    # 7. Duplicados exactos
    antes = len(df)
    df.drop_duplicates(inplace=True)
    print(f"  -> Duplicados eliminados: {antes - len(df)}")

    df.reset_index(drop=True, inplace=True)
    resumen(df, "DESPUES — OpenPublicDomain")
    exportar(df, os.path.join(CLEAN, "OpenPublicDomain"), "opfd_clean.parquet")
    return df


# ╔══════════════════════════════════════════════════════════╗
#  MAIN
# ╚══════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    print("=" * 55)
    print("  LIMPIEZA PRE-RECORD LINKAGE — Cruz Azul Intelligence")
    print("=" * 55)

    df_fifa   = limpiar_fifa_players()
    df_ligamx = limpiar_ligamx()
    df_tm     = limpiar_transfermarkt()
    df_opfd   = limpiar_opfd()

    print("\n\n" + "=" * 55)
    print("  RESUMEN FINAL")
    print("=" * 55)
    for nombre, df in [
        ("FIFA23 Players (MX)", df_fifa),
        ("LigaMX",              df_ligamx),
        ("Transfermarkt",       df_tm),
        ("OpenPublicDomain",    df_opfd),
    ]:
        total = df.shape[0] * df.shape[1]
        nulos = df.isnull().sum().sum()
        print(f"\n  {nombre:<25}  {df.shape[0]:>7,} filas x {df.shape[1]:>2} cols"
              f"  | nulos: {nulos/total*100:.1f} %")

    print(f"\n  Todos los datasets limpios exportados a: {CLEAN}")
