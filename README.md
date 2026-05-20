# ⚽ Proyecto Final — Calidad y Preprocesamiento de Datos
### Inteligencia Deportiva para Cruz Azul F.C.

> **Materia:** Calidad y Preprocesamiento de Datos  
> **Programa:** Licenciatura en Ciencia de Datos  
> **Profesores:** MCIC Víctor Manuel Corza Vargas · MCIC Fernando Avitúa Varela  
> **Fecha de entrega:** 27 de mayo de 2025

> **Equipo:**  
> Cruz Mendoza Valentina Ayelen  
> Monroy Villegas Isaac  
> Pérez Martínez Ángel Noel  
> Rivera Hernández Milena Fernanda  
> Zamora Antiga Ángel Javier  

---

## 📋 Descripción del Proyecto

Este proyecto aplica un pipeline completo de **calidad y preprocesamiento de datos** sobre información del fútbol mexicano (Liga MX), simulando el rol de un equipo de **inteligencia deportiva** para **Cruz Azul F.C.**

Los datos utilizados cubren la **Liga MX completa y el mercado global de jugadores**, ya que Cruz Azul necesita compararse contra sus rivales, analizar el mercado de transferencias y detectar talento en toda la liga para tomar mejores decisiones que su competencia. El objetivo es integrar múltiples fuentes heterogéneas sobre jugadores, partidos y transferencias, resolver sus problemas de calidad, y generar análisis que apoyen la **toma de decisiones en fichajes, rendimiento y planificación deportiva**.

---

## 🏢 Contexto de Negocio

**Cliente:** Departamento de Inteligencia Deportiva — Cruz Azul F.C. (La Máquina Cementera S.A. de C.V.)  
**Sede:** Ciudad de México | **Títulos Liga MX:** 9 | **Participación:** CONCACAF Champions Cup

Cruz Azul busca construir una plataforma de datos integrada para tomar decisiones más competitivas. Actualmente, su área de scouting consume datos de múltiples fuentes (videojuegos, portales de transferencias, registros históricos de partidos) que presentan inconsistencias graves: nombres duplicados, métricas incomparables, valores desactualizados y registros fragmentados. Esto genera errores en negociaciones, análisis históricos rotos y decisiones de fichaje sin respaldo objetivo.

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

## 📦 Fuentes de Datos

| # | Dataset | Fuente | Formato | Descripción |
|---|---|---|---|---|
| 1 | Liga MX Matches 2016–2024 | Kaggle | CSV | Partidos, resultados, equipos y temporadas Apertura/Clausura de toda la liga |
| 2 | FIFA 23 Complete Player Dataset | Kaggle | CSV | +19,000 jugadores con 110 atributos, incluyendo todos los jugadores de Liga MX |
| 3 | Football Data from Transfermarkt | Kaggle | CSV | Valor de mercado, transferencias, lesiones y estadísticas reales por temporada |
| 4 | football.csv — Liga MX | footballcsv.github.io | CSV | Resultados históricos de partidos de la Liga MX en dominio público |

### Links de descarga

```
1. kaggle.com/datasets/gerardojaimeescareo/ligamx-matches-2016-2022
2. kaggle.com/datasets/stefanoleone992/fifa-23-complete-player-dataset
3. kaggle.com/datasets/davidcariboo/player-scores
4. footballcsv.github.io → Mexico / Liga MX → Download .zip
```

> **Nota:** Los archivos de datos no están incluidos en el repositorio por su tamaño.  
> Descarga cada dataset desde los links anteriores y colócalos en la carpeta `data/raw/`.

---

## 🗂️ Estructura del Repositorio

```
proyecto-cruzazul-calidad/
│
├── data/
│   ├── raw/                        # Datos originales sin modificar (no versionados)
│   │   ├── ligamx_matches.csv
│   │   ├── fifa23_players.csv
│   │   ├── transfermarkt_players.csv
│   │   └── footballcsv_ligamx.csv
│   ├── processed/                  # Datos limpios y transformados
│   └── master/                     # Datos maestros fusionados (.parquet)
│
├── notebooks/
│   ├── perfilado.ipynb             # Perfilado antes y después de la limpieza
│   ├── limpieza.py                 # Limpieza: outliers, patrones, completitud
│   ├── fusion.ipynb                # Integración, record linkage y modelo canónico
│   └── analisis.py                 # Análisis descriptivo, predictivo y prescriptivo
│
├── reports/
│   ├── reporte_perfilado.pdf
│   ├── reporte_limpieza.pdf
│   ├── reporte_maestros.pdf
│   └── reporte_preprocesamiento.pdf
│
├── .gitignore                      # Excluye data/raw/ y data/master/ del repositorio
├── README.md
└── requirements.txt
```

---

## 🔬 Pipeline del Proyecto

```
[Fuentes de datos — Liga MX completa + mercado global]
        │
        ▼
[I. Integración]              → fusion.ipynb
  - Estandarización de todas las fuentes a formato CSV/Parquet
  - Integración formal de las bases
  - Record linkage y deduplicación entre fuentes
  - Definición del modelo canónico de jugador y partido
        │
        ▼
[II. Perfilado previo]        → perfilado.ipynb
  - Estadísticas descriptivas por fuente
  - Detección de nulos, duplicados y tipos de dato
  - Análisis de distribuciones y outliers
  - Documentación del estado inicial de calidad
        │
        ▼
[III. Limpieza]               → limpieza.py
  - Completar datos faltantes
  - Eliminar / tratar outliers
  - Estandarizar nombres, fechas y unidades
  - Forzar patrones (nacionalidades, posiciones, nombres)
        │
        ▼
[IV. Perfilado posterior]     → perfilado.ipynb
  - Mismas métricas que el perfilado previo
  - Comparativa antes vs después de la limpieza
  - Evidencia cuantitativa de mejora en calidad
        │
        ▼
[V. Análisis]                 → analisis.py
  - Resolución de las 5 problemáticas de Cruz Azul
  - 10 consultas multi-fuente (benchmarking vs rivales)
  - 5 consultas por fuente
  - Visualizaciones comparativas
```

---

## 📊 Análisis Realizados

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

## 🛠️ Tecnologías Utilizadas

| Herramienta | Uso |
|---|---|
| Python 3.10+ | Lenguaje principal |
| pandas | Manipulación de datos |
| numpy | Operaciones numéricas |
| matplotlib / seaborn / plotly | Visualizaciones |
| recordlinkage | Deduplicación y record linkage |
| scikit-learn | Preprocesamiento y modelos |
| jupyter | Notebooks interactivos |
| rapidfuzz | Matching de nombres aproximado |
| pyarrow | Lectura y escritura de archivos Parquet |

### Instalación

```bash
pip install -r requirements.txt
```

```
# requirements.txt
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
plotly>=5.10.0
recordlinkage>=0.15
scikit-learn>=1.1.0
jupyter>=1.0.0
rapidfuzz>=2.13.0
openpyxl>=3.0.10
pyarrow>=12.0.0
```

---

## ▶️ Ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-equipo/proyecto-cruzazul-calidad.git
cd proyecto-cruzazul-calidad

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Descargar los datasets y colocarlos en data/raw/
#    (ver links en la sección Fuentes de Datos)

# 4. Ejecutar el pipeline en orden:
jupyter notebook notebooks/fusion.ipynb       # I. Integración
jupyter notebook notebooks/perfilado.ipynb    # II. Perfilado previo
python notebooks/limpieza.py                  # III. Limpieza
#    (volver a perfilado.ipynb para IV. Perfilado posterior)
python notebooks/analisis.py                  # V. Análisis
```

---

## 👥 Equipo

| Nombre | Contribución principal |
|---|---|
| Cruz Mendoza Valentina Ayelen | Perfilado de datos |
| Monroy Villegas Isaac | Limpieza y estandarización |
| Pérez Martínez Ángel Noel | Record linkage y fusión |
| Rivera Hernández Milena Fernanda | Análisis y visualizaciones |
| Zamora Antiga Ángel Javier | Reporte y presentación |

---

## 📚 Framework de Calidad de Datos

Este proyecto sigue los lineamientos del framework **DAMA-DMBOK** (Data Management Body of Knowledge), enmarcando cada fase dentro de las dimensiones de calidad:

- **Completitud** — ¿Están todos los datos presentes?
- **Consistencia** — ¿Los datos son coherentes entre fuentes?
- **Exactitud** — ¿Los valores reflejan la realidad?
- **Unicidad** — ¿Existen duplicados?
- **Actualidad** — ¿Los datos están vigentes?
- **Validez** — ¿Los datos cumplen los formatos y reglas definidas?

---

## 📖 Referencias

Benz, R. (2024). *football.csv — Mexico Liga MX* [Conjunto de datos]. Open Football Data. https://footballcsv.github.io

Cariboo, D. (2024). *Football data from Transfermarkt* [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/davidcariboo/player-scores

DAMA International. (2017). *DAMA-DMBOK: Data management body of knowledge* (2nd ed.). Technics Publications.

Escareo, G. J. (2024). *LigaMX matches 2016-2024* [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/gerardojaimeescareo/ligamx-matches-2016-2022

Leone, S. (2023). *FIFA 23 complete player dataset* [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/stefanoleone992/fifa-23-complete-player-dataset

---

*Proyecto Final — Calidad y Preprocesamiento de Datos · Licenciatura en Ciencia de Datos*
