# ============================================================
#  RECORD LINKAGE — Cruz Azul Intelligence
#  Une: FIFA23 <-> Transfermarkt (jugadores)
#       LigaMX  <-> OpenPublicDomain (partidos)
#
#  Outputs (Parquet en CLEAN/LinkedData/):
#    jugadores_linked.parquet   → P1, P2, P4, P5, P6, P7, P9, P10
#    partidos_linked.parquet    → P3, P8, P10
# ============================================================

import os
import numpy as np
import pandas as pd
import recordlinkage
from recordlinkage.preprocessing import clean, phonetic

# ── Rutas (misma convención que limpieza_pulida.py) ─────────
BASE  = os.path.abspath(os.path.join(os.getcwd(), ".."))
CLEAN = os.path.join(BASE, "Datos_limpios")
OUT   = os.path.join(CLEAN, "LinkedData")
os.makedirs(OUT, exist_ok=True)

# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def cargar(subdir: str, archivo: str) -> pd.DataFrame:
    ruta = os.path.join(CLEAN, subdir, archivo)
    df = pd.read_parquet(ruta)
    print(f"  Cargado {archivo}: {len(df):,} filas")
    return df


def resumen_links(titulo: str, candidatos: pd.MultiIndex,
                  matches: pd.MultiIndex, total_a: int, total_b: int) -> None:
    print(f"\n{'─'*55}")
    print(f"  {titulo}")
    print(f"  Pares candidatos (bloqueo)  : {len(candidatos):>8,}")
    print(f"  Pares aceptados (threshold) : {len(matches):>8,}")
    cobertura = len(matches) / min(total_a, total_b) * 100
    print(f"  Cobertura estimada          : {cobertura:>7.1f} %")


# ╔══════════════════════════════════════════════════════════╗
#  BLOQUE A — JUGADORES: FIFA 23 <-> Transfermarkt
#
#  Estrategia de bloqueo:
#    Bloque 1 (preciso):  dob_key exacto + soundex del primer token del nombre
#    Bloque 2 (flexible): dob_key exacto  (para nombres con grafía muy distinta)
#
#  Comparadores:
#    - Jaro-Winkler sobre name_key           (peso alto)
#    - Jaro-Winkler sobre first/last_name_key (pesos medios)
#    - Exact match en dob_key               (peso medio)
#    - Exact match en main_position         (peso bajo)
#
#  Clasificación: SVM con threshold de score ≥ 0.75
# ╚══════════════════════════════════════════════════════════╝

def linkear_jugadores() -> pd.DataFrame:
    print("\n" + "=" * 55)
    print("  RECORD LINKAGE — Jugadores (FIFA23 <-> Transfermarkt)")
    print("=" * 55)

    # 1. Cargar datasets limpios
    fifa = cargar("FIFA23", "fifa23_players_mexico_clean.parquet")
    tm   = cargar("Transfermarkt", "transfermarkt_players_clean.parquet")

    # 2. Asegurar índices únicos y limpios
    fifa = fifa.reset_index(drop=True)
    tm   = tm.reset_index(drop=True)

    # 3. Columnas auxiliares para bloqueo
    #    soundex del primer token del nombre (robusto a errores tipográficos)
    def primer_token(s):
        if pd.isna(s):
            return ""
        return str(s).split()[0]

    fifa["_name_token"] = fifa["name_key"].apply(primer_token)
    tm["_name_token"]   = tm["name_key"].apply(primer_token)

    # recordlinkage.preprocessing.phonetic espera Series de strings limpios
    fifa["_phonetic"] = phonetic(clean(fifa["_name_token"]), method="soundex")
    tm["_phonetic"]   = phonetic(clean(tm["_name_token"]),  method="soundex")

    # Rellenar nulos en claves de bloqueo (evita perder filas válidas)
    for df_ in [fifa, tm]:
        df_["dob_key"]    = df_["dob_key"].fillna("__MISSING__")
        df_["_phonetic"]  = df_["_phonetic"].fillna("__MISSING__")

    # 4. Indexación (bloqueo) ─ dos bloques OR-ed
    indexer = recordlinkage.Index()
    # Bloque 1: fecha de nacimiento + soundex nombre
    indexer.block(left_on=["dob_key", "_phonetic"],
                  right_on=["dob_key", "_phonetic"])
    candidatos_b1 = indexer.index(fifa, tm)

    # Bloque 2: solo fecha de nacimiento (captura variantes ortográficas raras)
    indexer2 = recordlinkage.Index()
    indexer2.block(left_on="dob_key", right_on="dob_key")
    candidatos_b2 = indexer2.index(fifa, tm)

    # Unión de candidatos (eliminando duplicados de pares)
    candidatos = candidatos_b1.union(candidatos_b2)
    # Filtrar pares __MISSING__ × __MISSING__ (no aportan)
    mask_miss = (
        fifa.loc[candidatos.get_level_values(0), "dob_key"].values == "__MISSING__"
    ) & (
        tm.loc[candidatos.get_level_values(1), "dob_key"].values == "__MISSING__"
    )
    candidatos = candidatos[~mask_miss]
    print(f"\n  Candidatos tras bloqueo: {len(candidatos):,}")

    # 5. Comparación de features
    compare = recordlinkage.Compare()

    # Nombre completo (Jaro-Winkler, threshold 0.85)
    compare.string("name_key", "name_key",
                   method="jarowinkler", threshold=0.85,
                   label="sim_nombre_completo")

    # Primer nombre (Jaro-Winkler)
    compare.string("short_name_key", "first_name_key",
                   method="jarowinkler", threshold=0.80,
                   label="sim_primer_nombre")

    # Apellido (Jaro-Winkler, mayor tolerancia a abreviaciones)
    compare.string("name_key", "last_name_key",
                   method="jarowinkler", threshold=0.80,
                   label="sim_apellido")

    # Fecha de nacimiento exacta
    compare.exact("dob_key", "dob_key", label="exact_dob")

    # Posición principal (vocabulario normalizado al mismo estándar)
    compare.exact("main_position", "position", label="exact_posicion")

    features = compare.compute(candidatos, fifa, tm)

    # 6. Clasificación por score ponderado
    #    Pesos: nombre_completo=0.40, primer_nombre=0.20,
    #           apellido=0.20, dob=0.15, posición=0.05
    pesos = {
        "sim_nombre_completo": 0.40,
        "sim_primer_nombre"  : 0.20,
        "sim_apellido"       : 0.20,
        "exact_dob"          : 0.15,
        "exact_posicion"     : 0.05,
    }
    features["score"] = sum(
        features[col] * w for col, w in pesos.items()
    )

    THRESHOLD = 0.75
    matches = features[features["score"] >= THRESHOLD].index
    resumen_links("Jugadores FIFA23 ↔ Transfermarkt",
                  candidatos, matches, len(fifa), len(tm))

    # 7. Resolver 1-a-1: para cada FIFA player quedarse con el mejor TM match
    match_scores = features.loc[matches, "score"].copy()
    match_scores.index.names = ["fifa_idx", "tm_idx"]

    # Mejor TM por jugador FIFA (elimina duplicados de lado FIFA)
    best_per_fifa = (match_scores
                     .reset_index()
                     .sort_values("score", ascending=False)
                     .drop_duplicates(subset="fifa_idx", keep="first")
                     .set_index("fifa_idx"))

    # Mejor FIFA por jugador TM (elimina duplicados de lado TM)
    best_pairs = (best_per_fifa
                  .reset_index()
                  .sort_values("score", ascending=False)
                  .drop_duplicates(subset="tm_idx", keep="first"))

    final_idx_fifa = best_pairs["fifa_idx"].values
    final_idx_tm   = best_pairs["tm_idx"].values
    scores         = best_pairs["score"].values

    print(f"\n  Pares únicos finales (1-a-1): {len(final_idx_fifa):,}")

    # 8. Construir DataFrame enlazado
    cols_fifa = [
        "player_id", "long_name", "short_name",
        "dob", "dob_key", "name_key", "short_name_key",
        "club_name", "club_name_norm",
        "nationality_name", "main_position",
        "overall", "potential", "value_eur", "wage_eur",
        "age", "height_cm", "weight_kg",
        "goals", "assists",
        "pace", "shooting", "passing", "dribbling",
        "defending", "physic",
        "fifa_version", "fifa_update",
    ]
    cols_tm = [
        "player_id", "name", "first_name", "last_name",
        "name_key", "first_name_key", "last_name_key",
        "dob_key", "date_of_birth",
        "current_club_id", "current_club_name",
        "country_of_citizenship", "country_of_birth",
        "position", "sub_position",
        "market_value_in_eur", "highest_market_value_in_eur",
        "contract_expiration_date",
        "foot", "height_in_cm",
        "international_caps", "international_goals",
        "agent_name" if "agent_name" in tm.columns else None,
    ]
    cols_tm = [c for c in cols_tm if c is not None and c in tm.columns]
    cols_fifa = [c for c in cols_fifa if c in fifa.columns]

    df_fifa_sel = (fifa.loc[final_idx_fifa, cols_fifa]
                   .reset_index(drop=True)
                   .add_prefix("fifa_"))
    df_tm_sel   = (tm.loc[final_idx_tm, cols_tm]
                   .reset_index(drop=True)
                   .add_prefix("tm_"))

    linked = pd.concat([df_fifa_sel, df_tm_sel], axis=1)
    linked["rl_score"] = scores

    # Columnas de conveniencia para análisis
    linked["jugador"]            = linked["fifa_long_name"].fillna(linked["tm_name"])
    linked["club_norm"]          = linked["fifa_club_name_norm"]
    linked["posicion"]           = linked["fifa_main_position"].fillna(linked["tm_position"])
    linked["edad"]               = linked["fifa_age"]
    linked["overall_fifa"]       = linked["fifa_overall"]
    linked["valor_tm_eur"]       = linked["tm_market_value_in_eur"]
    linked["valor_fifa_eur"]     = linked["fifa_value_eur"]
    linked["nacionalidad"]       = linked["fifa_nationality_name"].fillna(
                                       linked["tm_country_of_citizenship"])

    # Índice de sobre/subvaloración (P1, P5, P7)
    #   ratio > 1: FIFA sobrevalora vs TM; < 1: TM sobrevalora vs FIFA
    linked["ratio_fifa_tm"] = (
        linked["valor_fifa_eur"] / linked["valor_tm_eur"].replace(0, np.nan)
    )

    ruta_out = os.path.join(OUT, "jugadores_linked.parquet")
    linked.to_parquet(ruta_out, index=False)
    print(f"\n  Exportado -> {ruta_out}  ({len(linked):,} filas)")
    return linked


# ╔══════════════════════════════════════════════════════════╗
#  BLOQUE B — PARTIDOS: LigaMX <-> OpenPublicDomain
#
#  Estrategia de bloqueo:
#    Bloque 1 (principal): date_key exacto + equipo_local_norm
#    Bloque 2 (alternativo): date_key + equipo_visitante_norm
#      (cubre casos donde un dataset tenga los equipos invertidos)
#
#  Comparadores:
#    - Exact match en date_key             (peso alto)
#    - Exact match equipo local normalizado (peso alto)
#    - Exact match equipo visitante        (peso alto)
#    - Numeric en goles_local              (peso medio, tolerancia ±0)
#    - Numeric en goles_visitante          (peso medio)
#
#  Clasificación: threshold ≥ 0.80
# ╚══════════════════════════════════════════════════════════╝

def linkear_partidos() -> pd.DataFrame:
    print("\n" + "=" * 55)
    print("  RECORD LINKAGE — Partidos (LigaMX <-> OpenPublicDomain)")
    print("=" * 55)

    ligamx = cargar("LigaMX", "ligamx_clean.parquet")
    opfd   = cargar("OpenPublicDomain", "opfd_clean.parquet")

    ligamx = ligamx.reset_index(drop=True)
    opfd   = opfd.reset_index(drop=True)

    # Rellenar nulos en claves de bloqueo
    for df_ in [ligamx, opfd]:
        df_["date_key"]        = df_["date_key"].fillna("__MISSING__")
        df_["home_team_norm"]  = df_["home_team_norm"].fillna("__MISSING__")
        df_["away_team_norm"]  = df_["away_team_norm"].fillna("__MISSING__")

    # 1. Bloqueo 1: fecha + equipo local
    indexer1 = recordlinkage.Index()
    indexer1.block(left_on=["date_key", "home_team_norm"],
                   right_on=["date_key", "home_team_norm"])
    cands1 = indexer1.index(ligamx, opfd)

    # 2. Bloqueo 2: fecha + equipo visitante (fallback)
    indexer2 = recordlinkage.Index()
    indexer2.block(left_on=["date_key", "away_team_norm"],
                   right_on=["date_key", "away_team_norm"])
    cands2 = indexer2.index(ligamx, opfd)

    candidatos = cands1.union(cands2)
    print(f"\n  Candidatos tras bloqueo: {len(candidatos):,}")

    # 3. Comparación
    compare = recordlinkage.Compare()

    compare.exact("date_key",       "date_key",       label="exact_fecha")
    compare.exact("home_team_norm", "home_team_norm", label="exact_local")
    compare.exact("away_team_norm", "away_team_norm", label="exact_visitante")

    # Goles: numeric con tolerancia 0 (son datos discretos exactos)
    compare.numeric("home_goals", "ft_home_goals",
                    method="gauss", offset=0.5,
                    label="sim_goles_local")
    compare.numeric("away_goals", "ft_away_goals",
                    method="gauss", offset=0.5,
                    label="sim_goles_visitante")

    features = compare.compute(candidatos, ligamx, opfd)

    # 4. Score ponderado
    pesos = {
        "exact_fecha"      : 0.30,
        "exact_local"      : 0.30,
        "exact_visitante"  : 0.25,
        "sim_goles_local"  : 0.075,
        "sim_goles_visitante": 0.075,
    }
    features["score"] = sum(
        features[col] * w for col, w in pesos.items()
    )

    THRESHOLD = 0.80
    matches = features[features["score"] >= THRESHOLD].index
    resumen_links("Partidos LigaMX ↔ OpenPublicDomain",
                  candidatos, matches, len(ligamx), len(opfd))

    # 5. Resolver 1-a-1
    match_scores = features.loc[matches, "score"].copy()
    match_scores.index.names = ["ligamx_idx", "opfd_idx"]

    best_pairs = (match_scores
                  .reset_index()
                  .sort_values("score", ascending=False)
                  .drop_duplicates(subset="ligamx_idx", keep="first")
                  .drop_duplicates(subset="opfd_idx",   keep="first"))

    final_idx_lx   = best_pairs["ligamx_idx"].values
    final_idx_opfd = best_pairs["opfd_idx"].values
    scores         = best_pairs["score"].values
    print(f"\n  Pares únicos finales (1-a-1): {len(final_idx_lx):,}")

    # 6. Columnas seleccionadas de cada fuente
    cols_lx = [
        "date", "date_key", "season",
        "home_team", "home_team_norm",
        "away_team", "away_team_norm",
        "home_goals", "away_goals",
        "home_goals_extra_time", "away_goals_extratime",
        "home_goals_penalty", "away_goals_penalty",
        "result_home",
        "venue_name", "venue_city",
        "home_win", "away_win",
    ]
    cols_opfd = [
        "date_key", "stage", "season",
        "home_team", "home_team_norm",
        "away_team", "away_team_norm",
        "ft_home_goals", "ft_away_goals",
        "ht_home_goals", "ht_away_goals",
        "result_home",
    ]
    cols_lx   = [c for c in cols_lx   if c in ligamx.columns]
    cols_opfd = [c for c in cols_opfd if c in opfd.columns]

    df_lx_sel   = (ligamx.loc[final_idx_lx, cols_lx]
                   .reset_index(drop=True)
                   .add_prefix("lx_"))
    df_opfd_sel = (opfd.loc[final_idx_opfd, cols_opfd]
                   .reset_index(drop=True)
                   .add_prefix("opfd_"))

    linked = pd.concat([df_lx_sel, df_opfd_sel], axis=1)
    linked["rl_score"] = scores

    # Columnas maestras (fuente de verdad: LigaMX cuando disponible)
    linked["fecha"]           = linked["lx_date"]
    linked["temporada"]       = linked["lx_season"]
    linked["equipo_local"]    = linked["lx_home_team_norm"]
    linked["equipo_visitante"]= linked["lx_away_team_norm"]
    linked["goles_local"]     = linked["lx_home_goals"].fillna(linked["opfd_ft_home_goals"])
    linked["goles_visitante"] = linked["lx_away_goals"].fillna(linked["opfd_ft_away_goals"])
    linked["goles_ht_local"]  = linked.get("opfd_ht_home_goals", np.nan)
    linked["goles_ht_visitante"] = linked.get("opfd_ht_away_goals", np.nan)
    linked["resultado_local"] = linked["lx_result_home"].fillna(linked["opfd_result_home"])
    linked["stage"]           = linked.get("opfd_stage", np.nan)

    # Flag Apertura / Clausura (útil para P3)
    def _torneo(fecha):
        if pd.isna(fecha):
            return np.nan
        mes = pd.Timestamp(fecha).month
        return "APERTURA" if mes >= 7 else "CLAUSURA"
    linked["torneo"] = linked["fecha"].apply(_torneo)

    ruta_out = os.path.join(OUT, "partidos_linked.parquet")
    linked.to_parquet(ruta_out, index=False)
    print(f"\n  Exportado -> {ruta_out}  ({len(linked):,} filas)")
    return linked


# ╔══════════════════════════════════════════════════════════╗
#  DIAGNÓSTICO — qué registros NO se enlazaron
# ╚══════════════════════════════════════════════════════════╝

def diagnostico_no_enlazados(fifa, tm, jugadores_linked,
                              ligamx, opfd, partidos_linked) -> None:
    print("\n" + "=" * 55)
    print("  DIAGNÓSTICO — Registros NO enlazados")
    print("=" * 55)

    # Jugadores FIFA sin match
    fifa_enlazados = set(jugadores_linked["fifa_player_id"].dropna())
    fifa_sin       = fifa[~fifa["player_id"].isin(fifa_enlazados)]
    print(f"\n  FIFA jugadores sin match   : {len(fifa_sin):,}")
    if len(fifa_sin) > 0:
        print("  Ejemplos:")
        print(fifa_sin[["long_name", "club_name", "dob_key"]].head(10).to_string(index=False))

    # Jugadores TM sin match
    tm_enlazados = set(jugadores_linked["tm_player_id"].dropna())
    tm_sin       = tm[~tm["player_id"].isin(tm_enlazados)]
    print(f"\n  TM  jugadores sin match    : {len(tm_sin):,}")
    if len(tm_sin) > 0:
        print("  Ejemplos:")
        print(tm_sin[["name", "current_club_name", "dob_key"]].head(10).to_string(index=False))

    # Partidos LigaMX sin match
    lx_enlazados = set(partidos_linked["lx_date_key"].dropna() + "_" +
                       partidos_linked["lx_home_team_norm"].fillna(""))
    lx_key = ligamx["date_key"].fillna("") + "_" + ligamx["home_team_norm"].fillna("")
    lx_sin = ligamx[~lx_key.isin(lx_enlazados)]
    print(f"\n  LigaMX partidos sin match  : {len(lx_sin):,}")

    opfd_enlazados = set(partidos_linked["opfd_date_key"].dropna() + "_" +
                         partidos_linked["opfd_home_team_norm"].fillna(""))
    opfd_key = opfd["date_key"].fillna("") + "_" + opfd["home_team_norm"].fillna("")
    opfd_sin = opfd[~opfd_key.isin(opfd_enlazados)]
    print(f"\n  OPFD  partidos sin match   : {len(opfd_sin):,}")


# ╔══════════════════════════════════════════════════════════╗
#  MAIN
# ╚══════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    print("=" * 55)
    print("  RECORD LINKAGE — Cruz Azul Intelligence")
    print("=" * 55)

    # A — Jugadores
    fifa   = pd.read_parquet(os.path.join(CLEAN, "FIFA23",
                             "fifa23_players_mexico_clean.parquet"))
    tm     = pd.read_parquet(os.path.join(CLEAN, "Transfermarkt",
                             "transfermarkt_players_clean.parquet"))
    jugadores_linked = linkear_jugadores()

    # B — Partidos
    ligamx = pd.read_parquet(os.path.join(CLEAN, "LigaMX",
                             "ligamx_clean.parquet"))
    opfd   = pd.read_parquet(os.path.join(CLEAN, "OpenPublicDomain",
                             "opfd_clean.parquet"))
    partidos_linked = linkear_partidos()

    # C — Diagnóstico de no enlazados
    diagnostico_no_enlazados(
        fifa, tm, jugadores_linked,
        ligamx, opfd, partidos_linked
    )

    print("\n" + "=" * 55)
    print("  RESUMEN FINAL")
    print("=" * 55)
    print(f"\n  jugadores_linked : {len(jugadores_linked):>6,} pares")
    print(f"  partidos_linked  : {len(partidos_linked):>6,} pares")
    print(f"\n  Outputs en: {OUT}")

    # Vista rápida de columnas clave
    print("\n  Columnas jugadores_linked (muestra):")
    cols_show = ["jugador", "club_norm", "posicion", "edad",
                 "overall_fifa", "valor_tm_eur", "valor_fifa_eur",
                 "ratio_fifa_tm", "rl_score"]
    print(jugadores_linked[[c for c in cols_show
                            if c in jugadores_linked.columns]].head(5).to_string())

    print("\n  Columnas partidos_linked (muestra):")
    cols_show2 = ["fecha", "temporada", "torneo", "equipo_local",
                  "equipo_visitante", "goles_local", "goles_visitante",
                  "resultado_local", "rl_score"]
    print(partidos_linked[[c for c in cols_show2
                           if c in partidos_linked.columns]].head(5).to_string())
