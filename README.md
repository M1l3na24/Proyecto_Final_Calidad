# ⚽ Proyecto Final — Calidad y Preprocesamiento de Datos
### Inteligencia Deportiva para Cruz Azul F.C.

**Materia:** Calidad y Preprocesamiento de Datos    
**Profesores:** MCIC Víctor Manuel Corza Vargas · Ayte. Fernando Avitúa Varela  
**Fecha de entrega:** 27 de mayo de 2026

**Equipo:**  
Cruz Mendoza Valentina Ayelen
  
Monroy Villegas Isaac  

Pérez Martínez Ángel Noel 
 
Rivera Hernández Milena Fernanda  

Zamora Antiga Ángel Javier  

---

## Descripción del Proyecto

Este proyecto implementa un pipeline completo de calidad y preprocesamiento de datos sobre información del fútbol mexicano (Liga MX), simulando el rol del Departamento de Inteligencia Deportiva de Cruz Azul F.C.

Se integran **cuatro fuentes heterogéneas** (CSV, JSON, TXT y XLSX) sobre jugadores, partidos y transferencias, se resuelven sus problemas de calidad bajo el framework **DAMA-DMBOK**, y se generan análisis descriptivos, predictivos y prescriptivos que apoyan la toma de decisiones en fichajes, rendimiento y planificación deportiva.

El pipeline atraviesa cinco fases —**integración, perfilado previo, limpieza, perfilado posterior y análisis**— orientadas a resolver cinco problemáticas de negocio concretas del club.

### Objetivo General

Diseñar e implementar un pipeline de calidad y preprocesamiento de datos sobre fútbol mexicano, aplicando el framework DAMA-DMBOK para integrar, limpiar y analizar cuatro fuentes heterogéneas que permitan a Cruz Azul F.C. tomar decisiones más informadas sobre fichajes, rendimiento y planificación deportiva.

---

## Contexto de Negocio

**Cliente:** Departamento de Inteligencia Deportiva — Cruz Azul F.C. (La Máquina Cementera S.A. de C.V.)  
**Sede:** Ciudad de México | **Títulos Liga MX:** 9 | **Participación:** CONCACAF Champions Cup

Cruz Azul busca construir una plataforma de datos integrada para tomar decisiones más competitivas. Su área de scouting consume datos de múltiples fuentes (portales de transferencias, registros históricos de partidos, datasets de videojuegos) que presentan inconsistencias graves: nombres duplicados, métricas incomparables, valores desactualizados y registros fragmentados. Esto genera errores en negociaciones, análisis históricos rotos y decisiones de fichaje sin respaldo objetivo.

> **¿Por qué datos de toda la liga y no solo de Cruz Azul?**  
> La inteligencia deportiva efectiva requiere *benchmarking competitivo*: Cruz Azul necesita saber cuánto vale un jugador respecto al mercado, cómo rinde un prospecto comparado con titulares de otros equipos, y dónde están las oportunidades sub-valoradas en la liga. Los datos completos de Liga MX y Transfermarkt son la base para ese benchmarking.

### Ejemplos de decisiones que se apoyan con datos de toda la liga

| Pregunta de negocio | Datos requeridos |
|---|---|
| ¿Cuánto vale un jugador vs perfiles similares en la liga? | Todos los jugadores de Liga MX |
| ¿Cruz Azul rinde mejor en casa o fuera vs el promedio de la liga? | Todos los partidos de Liga MX |
| ¿Qué mediocampista podríamos fichar por menos de 3M USD? | Liga MX completa + Transfermarkt global |
| ¿Cómo ha evolucionado nuestra plantilla vs América o Rayados? | Ambos clubes en Transfermarkt |
| ¿Qué perfil nos falta según los goles que estamos perdiendo? | Estadísticas completas de la liga |

### 5 Problemáticas de Negocio Identificadas

| # | Problemática | Dimensión de Calidad | Impacto en Cruz Azul |
|---|---|---|---|
| 1 | Inconsistencia en nombres de jugadores entre fuentes ("Jonathan García" / "J. García" / "García J.") | Consistencia | Scouting incorrecto; no se puede cruzar rendimiento real con valor de mercado |
| 2 | Valores de mercado faltantes o desactualizados para jugadores de Liga MX en Transfermarkt (73 de 1,150 jugadores, 6.3%) | Completitud / Oportunidad | Cruz Azul paga de más o negocia por debajo del valor real en transferencias |
| 3 | Duplicación de jugadores naturalizados o con doble nacionalidad | Unicidad | Catálogo inflado; confusión al analizar cupo de extranjeros en la plantilla |
| 4 | Inconsistencia en nombres de equipos entre temporadas (Monarcas Morelia → Mazatlán FC); 51 variantes para 18 equipos | Consistencia / Integridad referencial | Análisis históricos de rivales rotos; tendencias y patrones incorrectos |
| 5 | Métricas de rendimiento incomparables entre fuentes (FIFA usa escala 0–100, Transfermarkt usa euros y goles) | Validez / Comparabilidad | Imposibilidad de comparar candidatos a fichar de forma objetiva y sistémica |

---

## Fuentes de Datos

Bajo un enfoque híbrido de **ingeniería inversa y síntesis controlada**, se partió de cuatro fuentes públicas reales del fútbol profesional y se construyeron cuatro datasets propietarios (en `datos_final/`) introduciendo diversidad de formatos, variaciones de nomenclatura e inyección intencional de anomalías. El objetivo metodológico fue **emular la fragmentación operativa real** del Departamento de Inteligencia Deportiva y poner a prueba el pipeline de calidad.

### Matriz de fuentes generadas

| # | Archivo en `datos_final/` | Formato | Fuente real de referencia | Anomalía principal inyectada |
|---|---|---|---|---|
| 1 | `partidos_historicos_ligamx.csv` | CSV | Liga MX Matches 2016–2024 (Kaggle) | Inconsistencia nominal de equipos por renombres de franquicia |
| 2 | `perfiles_jugadores_historico.json` | JSON anidado | FIFA 23 Complete Player Dataset (Kaggle) | Contracción sintáctica de nombres ("U. Antuna") |
| 3 | `scouting_historico_ligamx.txt` | TXT ancho fijo | football.csv — Liga MX (Open Football Data) | Formato plano legado; divergencias tipográficas en clubes |
| 4 | `valor_mercado_historico.xlsx` | XLSX | Football Data from Transfermarkt (Kaggle) | Valores nulos en cotizaciones; duplicados por naturalización |

### Enlaces de descarga de las fuentes originales

```
1. kaggle.com/datasets/gerardojaimeescareo/ligamx-matches-2016-2022
2. kaggle.com/datasets/stefanoleone992/fifa-23-complete-player-dataset
3. footballcsv.github.io → Mexico / Liga MX → Download .zip
4. kaggle.com/datasets/davidcariboo/player-scores
```

---

## Estructura del Repositorio

```
Proyecto_Final_Calidad/
│
├── datos_final/                               # 4 fuentes heterogéneas de entrada
│   ├── partidos_historicos_ligamx.csv         # Dataset 1 — Partidos (CSV)
│   ├── perfiles_jugadores_historico.json      # Dataset 2 — Jugadores FIFA (JSON anidado)
│   ├── scouting_historico_ligamx.txt          # Dataset 3 — Scouting (TXT ancho fijo)
│   └── valor_mercado_historico.xlsx           # Dataset 4 — Valor de mercado (XLSX)
│
├── datos_master/                              # Modelos canónicos integrados (Parquet, generados, no versionados)
│   ├── master_jugadores.parquet               # 1,150 jugadores · ~38 columnas
│   └── master_partidos.parquet                # 4,080 partidos · 19 columnas (2010–2025)
│
├── notebooks/
│   ├── fusion.ipynb                           # I.   Integración, record linkage y modelo canónico
│   ├── perfilado.ipynb                        # II/IV. Perfilado antes y después (variable MODO)
│   ├── limpieza.ipynb                         # III. Limpieza, outliers, deduplicación e imputación KNN
│   └── analisis.ipynb                         # V.   Análisis descriptivo, predictivo y prescriptivo
│
├── reports/                                   # Reportes HTML de ydata-profiling
│   ├── perfil_antes_Partidos_CSV.html         # Perfilado previo — Dataset 1 (CSV)
│   ├── perfil_antes_Jugadores_JSON.html       # Perfilado previo — Dataset 2 (JSON)
│   ├── perfil_antes_Valor_Mercado_XLSX.html   # Perfilado previo — Dataset 4 (XLSX)
│   ├── perfil_antes_Scouting_TXT.html         # Perfilado previo — Dataset 3 (TXT)
│   ├── perfil_despues_Master_Jugadores.html   # Perfilado posterior — master_jugadores
│   └── perfil_despues_Master_Partidos.html    # Perfilado posterior — master_partidos
│
├── .gitignore
├── Especificación de proyecto de calidad de datos.pdf
├── LICENSE
├── README.md
└── requirements.txt
```

> **Nota:** la carpeta `datos_master/` se genera automáticamente al ejecutar `fusion.ipynb` y `limpieza.ipynb`; no se versiona en el repositorio.

---

## Modelos de Datos Maestros

### `master_jugadores.parquet` — 1,150 registros · ~38 columnas

Modelo canónico de jugadores integrado desde las cuatro fuentes. Cubre temporadas Apertura/Clausura 2010–2024. El `nombre_canonico` se toma de Transfermarkt como fuente de verdad.

| Grupo | Columnas |
|---|---|
| Identificación | `player_id`, `nombre_canonico`, `nombre_key` |
| Trazabilidad record linkage | `nombre_transfermarkt`, `nombre_fifa`, `nombre_football_csv`, `sim_tm_fifa`, `sim_tm_csv` |
| Perfil | `posicion`, `nacionalidad`, `segunda_nacionalidad`, `es_extranjero`, `doble_nacionalidad`, `edad`, `temporada`, `season_year`, `equipo`, `equipo_norm` |
| Atributos FIFA (escala 0–100) | `fifa_overall`, `fifa_pace`, `fifa_shooting`, `fifa_passing`, `fifa_dribbling`, `fifa_defending`, `fifa_physical` |
| Mercado y rendimiento | `valor_mercado_eur`, `transfer_paid_eur`, `goles`, `asistencias`, `partidos`, `g_a_por_90` |
| Partidos | `p_casa`, `goles_casa`, `p_fuera`, `goles_fuera`, `tarj_am`, `tarj_roj` |
| Calidad | `inconsistencias`, `imputado` |

### `master_partidos.parquet` — 4,080 registros · 19 columnas

Modelo canónico de partidos integrado desde los datasets de Liga MX. Cubre de julio 2010 a abril 2025.

| Grupo | Columnas |
|---|---|
| Identificación | `match_id`, `date`, `season`, `season_year`, `half`, `round` |
| Equipos | `home_team_id`, `equipo_local`, `equipo_local_norm`, `away_team_id`, `equipo_visitante`, `equipo_visitante_norm` |
| Resultado | `goles_local`, `goles_visitante`, `goles_local_ht`, `goles_visitante_ht`, `resultado_local` |
| Contexto | `venue`, `involucra_cruz_azul` |

---

## Pipeline del Proyecto

```
[datos_final/ — 4 fuentes heterogéneas: CSV · JSON · TXT · XLSX]
        |
        v
[I. Integración]              → notebooks/fusion.ipynb
  - Estandarización de formatos al modelo canónico
  - Record linkage entre fuentes (similitud Jaro-Winkler / WRatio, umbral 0.75)
  - Deduplicación de jugadores con doble nacionalidad
  - Normalización de nombres de equipo (diccionario de alias)
  - Exportación a datos_master/ (Parquet)
        |
        v
[II. Perfilado previo]        → notebooks/perfilado.ipynb  (MODO = 'ANTES')
  - Estadísticas descriptivas por fuente
  - Detección de nulos, duplicados y tipos de dato
  - Análisis de distribuciones y outliers (IQR)
  - Reporte HTML automático con ydata-profiling → reports/
        |
        v
[III. Limpieza]               → notebooks/limpieza.ipynb
  - Validación de tipos y rangos (clip a límites de dominio)
  - Deduplicación por player_id y clave compuesta de partido
  - Detección y tratamiento de outliers (IQR · cap percentil 99)
  - Imputación de valores faltantes con KNNImputer (k=7 óptimo por RMSE)
        |
        v
[IV. Perfilado posterior]     → notebooks/perfilado.ipynb  (MODO = 'DESPUES')
  - Mismas métricas que el perfilado previo, sobre los masters limpios
  - Comparativa antes vs después de la limpieza
  - Evidencia cuantitativa de mejora en cada dimensión DAMA-DMBOK
        |
        v
[V. Análisis]                 → notebooks/analisis.ipynb
  - Resolución de las 10 preguntas de negocio (dataset maestro)
  - 20 preguntas adicionales (5 por cada dataset original)
  - Análisis descriptivo, predictivo y prescriptivo + visualizaciones
```

---

## Análisis Realizados

El análisis (`analisis.ipynb`) responde **10 preguntas de negocio sobre el dataset maestro** y **20 preguntas sobre los datasets originales** (5 por fuente), clasificadas en descriptivas, predictivas y prescriptivas.

### Análisis Descriptivo
- **P1** — Valor de mercado de jugadores de Cruz Azul vs perfiles similares de la liga (percentiles por posición).
- **P2** — Rendimiento en casa vs fuera (puntos por partido) y comparación con la liga.
- **P3** — Métricas de extranjeros vs nacionales y aprovechamiento del cupo de extranjeros.
- **P4** — Equipos con mayor brecha entre valoración FIFA y valor de mercado real ("talento oculto").

### Análisis Predictivo
- **P5** — Proyección a 2 años del valor total de plantilla (Cruz Azul vs América y Rayados) con series temporales (Holt-Winters / regresión con tendencia).
- **P6** — Probabilidad de transferencia de jugadores (clasificación binaria con **XGBoost**, AUC-ROC).
- **P7** — Valor de mercado esperado según rendimiento y atributos FIFA (**Random Forest Regressor**, RMSE / R²); valida implícitamente la imputación KNN.
- **P8** — Resultado esperado de partidos de Cruz Azul (clasificación multiclase W/D/L con feature engineering).

### Análisis Prescriptivo
- **P9** — Mediocampista que maximiza la relación rendimiento/costo con presupuesto ≤ 3M USD (índice compuesto).
- **P10** — Debilidades tácticas según goles concedidos y perfil de jugador para cubrirlas.

### Preguntas sobre datasets originales (20)
Análisis directos sobre cada fuente: evolución de goles por temporada, ventaja de local por estadio, clasificación de posición táctica con atributos FIFA, predicción de G+A/90, índices de calidad-precio, disciplina por equipo, predicción de tarjeta roja, refuerzos ofensivos para visita, entre otros.

### Resultados destacados
- **97.8%** de los jugadores (1,125 de 1,150) tenían nombre distinto entre fuentes; un *join* exacto habría fallado, justificando el record linkage.
- **147 discrepancias** de nombre resueltas; **100%** de cobertura del nombre canónico desde Transfermarkt.
- **51 → 28** variantes de nombre de equipo en el master (catálogo canónico de 18 equipos activos + franquicias históricas mapeadas).
- **73 valores** de mercado imputados con KNN (k=7); completitud final del **100%** (salvo `segunda_nacionalidad`, nulo legítimo).
- Correlación FIFA overall ↔ valor de mercado de solo **0.443**: los jugadores sub-valorados por Transfermarkt respecto a su rendimiento FIFA son oportunidades de fichaje eficiente.

---

## Tecnologías Utilizadas

| Herramienta | Uso |
|---|---|
| Python 3.10+ | Lenguaje principal |
| pandas | Manipulación de datos |
| numpy | Operaciones numéricas |
| scipy | Estadística y utilidades numéricas |
| matplotlib / seaborn | Visualizaciones |
| scikit-learn | KNNImputer, StandardScaler, Random Forest, métricas de validación |
| xgboost | Clasificación de probabilidad de transferencia (P6) |
| statsmodels | Series temporales (proyección de valor de plantilla, P5) |
| rapidfuzz | Similitud Jaro-Winkler / WRatio para record linkage de nombres |
| ydata-profiling | Reportes HTML automáticos de perfilado |
| pyarrow | Lectura y escritura de archivos Parquet |
| openpyxl | Lectura de archivos XLSX |
| jupyter / ipykernel | Ejecución de notebooks |

### Instalación

```bash
pip install -r requirements.txt
```

---

## Ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/M1l3na24/Proyecto_Final_Calidad.git
cd Proyecto_Final_Calidad

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Asegurarse de que las 4 fuentes estén en datos_final/
#    (ya incluidas en el repositorio)

# 4. Ejecutar el pipeline en orden:
jupyter notebook notebooks/fusion.ipynb       # I.   Integración y record linkage → datos_master/

# En perfilado.ipynb: establecer MODO = 'ANTES'
jupyter notebook notebooks/perfilado.ipynb    # II.  Perfilado previo → reports/

jupyter notebook notebooks/limpieza.ipynb     # III. Limpieza e imputación KNN

# En perfilado.ipynb: establecer MODO = 'DESPUES'
jupyter notebook notebooks/perfilado.ipynb    # IV.  Perfilado posterior → reports/

jupyter notebook notebooks/analisis.ipynb     # V.   Análisis descriptivo, predictivo y prescriptivo
```

---

## Framework de Calidad de Datos

Este proyecto sigue los lineamientos del framework **DAMA-DMBOK** (Data Management Body of Knowledge), enmarcando cada fase dentro de las siguientes dimensiones de calidad:

- **Completitud** — ¿Están todos los datos presentes?
- **Consistencia** — ¿Los datos son coherentes entre sí y entre fuentes?
- **Exactitud** — ¿Los valores reflejan la realidad?
- **Unicidad** — ¿Existen duplicados?
- **Oportunidad / Actualidad** — ¿Los datos están vigentes y disponibles cuando se necesitan?
- **Validez** — ¿Los datos cumplen los formatos, rangos y reglas definidas?

| Dimensión | Problemática asociada | Mecanismo de resolución |
|---|---|---|
| Consistencia | #1 Nombres de jugadores · #4 Nombres de equipos | Record linkage Jaro-Winkler + normalización de texto |
| Completitud / Oportunidad | #2 Valores de mercado faltantes | Imputación KNN (k=7) |
| Unicidad | #3 Jugadores con doble nacionalidad | Deduplicación por `player_id` y consolidación |
| Validez | #5 Escalas incomparables | Conversión de tipos, escalas separadas en el master, tratamiento de outliers |

---

## Referencias

Benz, R. (2024). *football.csv — Mexico Liga MX* [Conjunto de datos]. Open Football Data. https://footballcsv.github.io

Cariboo, D. (2024). *Football data from Transfermarkt* [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/davidcariboo/player-scores

Cruz Azul Fútbol Club. (2024). *Historia*. Sitio Oficial de Cruz Azul F.C. https://cfcruzazul.com/historia/los-inicios/

DAMA International. (2017). *DAMA-DMBOK: Data management body of knowledge* (2nd ed.). Technics Publications.

Escareo, G. J. (2024). *LigaMX matches 2016-2024* [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/gerardojaimeescareo/ligamx-matches-2016-2022

Leone, S. (2023). *FIFA 23 complete player dataset* [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/stefanoleone992/fifa-23-complete-player-dataset

---

*Proyecto Final — Calidad y Preprocesamiento de Datos · Licenciatura en Ciencia de Datos*
