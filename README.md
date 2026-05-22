# ⚽ Proyecto Final — Calidad y Preprocesamiento de Datos
### Inteligencia Deportiva para Cruz Azul F.C.

**Materia:** Calidad y Preprocesamiento de Datos    
**Profesores:** MCIC Víctor Manuel Corza Vargas · MCIC Fernando Avitúa Varela  
**Fecha de entrega:** 27 de mayo de 2025

**Equipo:**  
Cruz Mendoza Valentina Ayelen
  
Monroy Villegas Isaac  

Pérez Martínez Ángel Noel 
 
Rivera Hernández Milena Fernanda  

Zamora Antiga Ángel Javier  

---

## Descripción del Proyecto

Este proyecto aplica un pipeline completo de calidad y preprocesamiento de datos sobre información del fútbol mexicano (Liga MX), simulando el rol de un equipo de inteligencia deportiva para Cruz Azul F.C.

Los datos utilizados cubren la Liga MX completa y el mercado global de jugadores. El objetivo es integrar múltiples fuentes heterogéneas sobre jugadores, partidos y transferencias, resolver sus problemas de calidad, y generar análisis que apoyen la toma de decisiones en fichajes, rendimiento y planificación deportiva.

---

## Contexto de Negocio

**Cliente:** Departamento de Inteligencia Deportiva — Cruz Azul F.C. (La Máquina Cementera S.A. de C.V.)  
**Sede:** Ciudad de México | **Títulos Liga MX:** 9 | **Participación:** CONCACAF Champions Cup

Cruz Azul busca construir una plataforma de datos integrada para tomar decisiones más competitivas. Su área de scouting consume datos de múltiples fuentes (portales de transferencias, registros históricos de partidos) que presentan inconsistencias graves: nombres duplicados, métricas incomparables, valores desactualizados y registros fragmentados. Esto genera errores en negociaciones, análisis históricos rotos y decisiones de fichaje sin respaldo objetivo.

> **¿Por qué datos de toda la liga y no solo de Cruz Azul?**  
> Cruz Azul necesita saber cuánto vale un jugador respecto al mercado, cómo rinde un prospecto comparado con titulares de otros equipos, y dónde están las oportunidades sub-valoradas en la liga. Los datos completos de Liga MX y Transfermarkt son la base para ese benchmarking competitivo.

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
| 1 | Inconsistencia en nombres de jugadores entre fuentes ("Uriel Antuna" vs "U. Antuna" vs "Antuna U.") | Consistencia | Scouting incorrecto; no se puede cruzar rendimiento real con valor de mercado |
| 2 | Valores de mercado faltantes o desactualizados para jugadores de Liga MX en Transfermarkt | Completitud / Actualidad | Cruz Azul paga de más o negocia por debajo del valor real en transferencias |
| 3 | Duplicación de jugadores naturalizados o con doble nacionalidad | Unicidad | Catálogo inflado; confusión al analizar cupo de extranjeros en la plantilla |
| 4 | Inconsistencia en nombres de equipos entre temporadas (ej. Monarcas Morelia → Mazatlán FC) | Consistencia / Integridad referencial | Análisis históricos de rivales rotos; tendencias y patrones incorrectos |
| 5 | Métricas de rendimiento incomparables entre fuentes (FIFA usa escala 0–100, Transfermarkt usa euros y goles) | Precisión / Comparabilidad | Imposibilidad de comparar candidatos a fichar de forma objetiva y sistémica |

---

## Fuentes de Datos

Los datos originales no están incluidos en el repositorio por su tamaño. Puedes descargarlos desde las ligas que vienen más abajo. Nosotros hicimos una generación sintética de los datasets dentro de datos_final/ basándonos en los originales para tener más inconsistencias intencionalmente. Pero los originales se listan a continuación: 

| # | Dataset | Fuente | Formato | Descripción |
|---|---|---|---|---|
| 1 | Liga MX Matches 2016–2024 | Kaggle | CSV | Partidos, resultados, equipos y temporadas de toda la liga |
| 2 | FIFA 23 Complete Player Dataset | Kaggle | CSV | +19,000 jugadores con 110 atributos, incluyendo todos los de Liga MX |
| 3 | Football Data from Transfermarkt | Kaggle | CSV | Valor de mercado, transferencias, lesiones y estadísticas reales por temporada |
| 4 | football.csv — Liga MX | footballcsv.github.io | CSV | Resultados históricos de partidos de Liga MX en dominio público |

### Enlaces de descarga

```
1. kaggle.com/datasets/gerardojaimeescareo/ligamx-matches-2016-2022
2. kaggle.com/datasets/stefanoleone992/fifa-23-complete-player-dataset
3. kaggle.com/datasets/davidcariboo/player-scores
4. footballcsv.github.io → Mexico / Liga MX → Download .zip
```

---

## Estructura del Repositorio

```
Proyecto_Final_Calidad/
│
├── datos_master/                              # Modelos canónicos integrados (Parquet, no versionados)
│   ├── master_jugadores.parquet               # 1,150 jugadores · 39 columnas
│   └── master_partidos.parquet                # 4,080 partidos · 19 columnas (2010–2025)
│
├── notebooks/
│   └── fusion.ipynb                           # I. Integración, record linkage y modelo canónico
│
├── reports/                                   # Reportes HTML de ydata-profiling
│   ├── perfil_antes_Partidos_CSV.html         # Perfilado previo — Dataset 1 (CSV)
│   ├── perfil_antes_Jugadores_JSON.html       # Perfilado previo — Dataset 2 (JSON)
│   ├── perfil_antes_Valor_Mercado_XLSX.html   # Perfilado previo — Dataset 3 (XLSX)
│   ├── perfil_antes_Scouting_TXT.html         # Perfilado previo — Dataset 4 (TXT)
│   ├── perfil_despues_Master_Jugadores.html   # Perfilado posterior — master_jugadores
│   └── perfil_despues_Master_Partidos.html    # Perfilado posterior — master_partidos
│
├── convertir_formatos.py                      # Script auxiliar de conversión de formatos de entrada
├── limpieza.ipynb                             # III. Limpieza, outliers, deduplicación e imputación KNN
├── perfilado.ipynb                            # II/IV. Perfilado antes y después de limpieza (MODO variable)
├── .gitignore
├── Especificación de proyecto de calidad de datos.pdf
├── LICENSE
├── README.md
└── requirements.txt
```


---

## Modelos de Datos Maestros

### master_jugadores.parquet — 1,150 registros · 39 columnas

Modelo canónico de jugadores integrado desde las cuatro fuentes. Cubre temporadas Apertura/Clausura 2010–2024.

| Grupo | Columnas |
|---|---|
| Identificación | `player_id`, `nombre_canonico`, `nombre_key`, `nombre_transfermarkt`, `nombre_fifa`, `nombre_football_csv` |
| Similitud record linkage | `sim_tm_fifa`, `sim_tm_csv` |
| Perfil | `posicion`, `nacionalidad`, `segunda_nacionalidad`, `es_extranjero`, `doble_nacionalidad`, `edad`, `temporada`, `season_year`, `equipo`, `equipo_norm` |
| Atributos FIFA | `fifa_overall`, `fifa_pace`, `fifa_shooting`, `fifa_passing`, `fifa_dribbling`, `fifa_defending`, `fifa_physical` |
| Mercado y rendimiento | `valor_mercado_eur`, `transfer_paid_eur`, `goles`, `asistencias`, `partidos`, `g_a_por_90` |
| Partidos | `p_casa`, `goles_casa`, `p_fuera`, `goles_fuera`, `tarj_am`, `tarj_roj` |
| Calidad | `inconsistencias`, `imputado` |

### master_partidos.parquet — 4,080 registros · 19 columnas

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
[datos_final/ — 4 fuentes heterogéneas: CSV · JSON · XLSX · TXT]
        |
        v
[I. Integración]              → notebooks/fusion.ipynb
  - Estandarización de formatos al modelo canónico
  - Record linkage entre fuentes (similitud Jaro-Winkler, umbral 0.75)
  - Deduplicación y resolución de inconsistencias de nombres
  - Exportación a datos_master/ (Parquet)
        |
        v
[II. Perfilado previo]        → perfilado.ipynb  (MODO = 'ANTES')
  - Estadísticas descriptivas por fuente
  - Detección de nulos, duplicados y tipos de dato
  - Análisis de distribuciones y outliers
  - Reporte HTML automático con ydata-profiling
        |
        v
[III. Limpieza]               → limpieza.ipynb
  - Validación de tipos y rangos
  - Deduplicación por player_id y match_id
  - Detección y tratamiento de outliers (IQR · cap percentil 99)
  - Imputación de valores faltantes con KNN Imputer (k óptimo por RMSE)
  - Exportación de datasets limpios a datos_master/
        |
        v
[IV. Perfilado posterior]     → perfilado.ipynb  (MODO = 'DESPUES')
  - Mismas métricas que el perfilado previo
  - Comparativa antes vs después de la limpieza
  - Evidencia cuantitativa de mejora en calidad
        |
        v
[V. Análisis]                 → (pendiente)
  - Resolución de las 5 problemáticas de Cruz Azul
  - Análisis descriptivo, predictivo y prescriptivo
  - Visualizaciones comparativas
```

---

## Análisis Realizados

### Análisis Descriptivo
- Distribución y comparativa de valores de mercado: Cruz Azul vs América, Chivas y Rayados
- Rendimiento histórico de Cruz Azul por temporada (Apertura vs Clausura) y vs promedio de la liga
- Nacionalidades y cupo de extranjeros en Cruz Azul vs resto de equipos

### Análisis Predictivo
- Predicción del valor de mercado de un jugador en función de sus atributos FIFA + estadísticas reales
- Clasificación de jugadores de la liga con mayor probabilidad de transferencia y que encajan en el perfil de Cruz Azul

### Análisis Prescriptivo
- Recomendación de jugadores para fichar por posición y presupuesto, priorizando candidatos sub-valorados por Transfermarkt respecto a su rendimiento real
- Detección de debilidades tácticas de Cruz Azul basadas en estadísticas de goles concedidos y asistencias rivales

---

## Tecnologías Utilizadas

| Herramienta | Uso |
|---|---|
| Python 3.10+ | Lenguaje principal |
| pandas | Manipulación de datos |
| numpy | Operaciones numéricas |
| matplotlib / seaborn / plotly | Visualizaciones |
| scikit-learn | KNNImputer, StandardScaler, métricas de validación |
| recordlinkage | Record linkage entre fuentes |
| rapidfuzz | Similitud Jaro-Winkler para matching de nombres |
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

# 3. Descargar los datasets y colocarlos en datos_final/
#    (ver enlaces en la sección Fuentes de Datos)

# 4. Ejecutar el pipeline en orden:
jupyter notebook notebooks/fusion.ipynb   # I.   Integración y record linkage

# En perfilado.ipynb: establecer MODO = 'ANTES'
jupyter notebook perfilado.ipynb          # II.  Perfilado previo

jupyter notebook limpieza.ipynb           # III. Limpieza e imputación KNN

# En perfilado.ipynb: establecer MODO = 'DESPUES'
jupyter notebook perfilado.ipynb          # IV.  Perfilado posterior
```

---

## Framework de Calidad de Datos

Este proyecto sigue los lineamientos del framework DAMA-DMBOK (Data Management Body of Knowledge), enmarcando cada fase dentro de las siguientes dimensiones de calidad:

- **Completitud** — ¿Están todos los datos presentes?
- **Consistencia** — ¿Los datos son coherentes entre fuentes?
- **Exactitud** — ¿Los valores reflejan la realidad?
- **Unicidad** — ¿Existen duplicados?
- **Actualidad** — ¿Los datos están vigentes?
- **Validez** — ¿Los datos cumplen los formatos y reglas definidas?

---

## Referencias

Benz, R. (2024). *football.csv — Mexico Liga MX* [Conjunto de datos]. Open Football Data. https://footballcsv.github.io

Cariboo, D. (2024). *Football data from Transfermarkt* [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/davidcariboo/player-scores

DAMA International. (2017). *DAMA-DMBOK: Data management body of knowledge* (2nd ed.). Technics Publications.

Escareo, G. J. (2024). *LigaMX matches 2016-2024* [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/gerardojaimeescareo/ligamx-matches-2016-2022

Leone, S. (2023). *FIFA 23 complete player dataset* [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/stefanoleone992/fifa-23-complete-player-dataset

---

*Proyecto Final — Calidad y Preprocesamiento de Datos · Licenciatura en Ciencia de Datos*
