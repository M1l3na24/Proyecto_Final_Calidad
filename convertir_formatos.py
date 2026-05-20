import pandas as pd
import os

BASE = "/Users/milenafer/Desktop/claude/Calidad_PFinal"
RAW  = os.path.join(BASE, "Datos_originales")
OUT  = os.path.join(BASE, "Datos_modificados")

MB50 = 50 * 1024 * 1024  # 50 MB en bytes


def convertir(ruta_csv, carpeta_destino, formato):
    nombre = os.path.splitext(os.path.basename(ruta_csv))[0]
    os.makedirs(carpeta_destino, exist_ok=True)

    df = pd.read_csv(ruta_csv, low_memory=False)
    print(f"    {nombre}: {len(df):,} filas x {len(df.columns)} cols")

    if formato == "json":
        dest = os.path.join(carpeta_destino, f"{nombre}.json")
        df.to_json(dest, orient="records", force_ascii=False, indent=2)

    elif formato == "xlsx":
        dest = os.path.join(carpeta_destino, f"{nombre}.xlsx")
        df.to_excel(dest, index=False, engine="openpyxl")

    elif formato == "txt":
        dest = os.path.join(carpeta_destino, f"{nombre}.txt")
        df.to_csv(dest, index=False, sep="\t", encoding="utf-8")

    print(f"    -> {dest.split('/')[-1]}  ({os.path.getsize(dest)/1024:.1f} KB)")


# ── 1. LigaMX → JSON ──────────────────────────────────────────────────────────
print("\n=== LigaMX → JSON ===")
carpeta_src = os.path.join(RAW, "LigaMX")
carpeta_dst = os.path.join(OUT, "LigaMX")
for f in sorted(os.listdir(carpeta_src)):
    if f.endswith(".csv"):
        convertir(os.path.join(carpeta_src, f), carpeta_dst, "json")

# ── 2. FootballDatafromTransfermarkt → XLSX (saltar >50 MB) ──────────────────
print("\n=== FootballDatafromTransfermarkt → XLSX (se saltan archivos >50 MB) ===")
carpeta_src = os.path.join(RAW, "FootballDatafromTransfermarkt")
carpeta_dst = os.path.join(OUT, "FootballDatafromTransfermarkt")
for f in sorted(os.listdir(carpeta_src)):
    if not f.endswith(".csv"):
        continue
    ruta = os.path.join(carpeta_src, f)
    if os.path.getsize(ruta) > MB50:
        print(f"    SALTADO (>50 MB): {f}")
        continue
    convertir(ruta, carpeta_dst, "xlsx")

# ── 3. FIFA23complete_player_dataset → TXT (saltar male_players.csv) ─────────
print("\n=== FIFA23complete_player_dataset → TXT (se salta male_players.csv) ===")
carpeta_src = os.path.join(RAW, "FIFA23complete_player_dataset")
carpeta_dst = os.path.join(OUT, "FIFA23complete_player_dataset")
SALTAR = {"male_players.csv"}
for f in sorted(os.listdir(carpeta_src)):
    if not f.endswith(".csv"):
        continue
    if f in SALTAR:
        print(f"    SALTADO: {f}")
        continue
    convertir(os.path.join(carpeta_src, f), carpeta_dst, "txt")

print("\nListo. Archivos guardados en Datos_modificados/")
