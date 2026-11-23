# Changelog

Todas las modificaciones notables a este proyecto se documentarán en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/)
y el proyecto se adhiere a la Especificación Maestra de Steam Intelligence.

## [1.3.0] - 2026-11-23

### Añadido (Fase 7 — Competitor Analyzer & Review Mining)
- Servicio de análisis de competidores en `backend/app/services/competitor_analyzer.py`:
  - Algoritmo de sugerencia de competidores basado en similitud de Jaccard sobre taxonomías de tags y géneros, proximidad de fecha de lanzamiento y bandas de precio.
  - Registro explícito de razones de competitividad (`tag_overlap`, `genre_overlap`, `mechanic_overlap`, `audience_overlap`, `manual_selection`, `early_access_cohort`).
  - Matriz de comparación directa Head-to-Head (`compare_head_to_head`): precios en USD, CCU observado y picos, reseñas totales, ratios positivos, tags compartidos y diferenciales.
  - Endpoints REST: `GET /api/v1/competitors/suggestions/{game_id}`, `POST /api/v1/competitors/link`, `GET /api/v1/competitors/{game_id}`, `GET /api/v1/competitors/compare/{game_id_a}/{game_id_b}`.
  - Interfaz de usuario **Competitor Analyzer** (`/competitors`): comparador interactivo, matriz visual de solapamiento y lista de sugerencias con vinculación en 1 clic.
- Servicio de minería de reseñas en `backend/app/services/review_mining.py`:
  - Pipeline de clasificación estructurado sobre 15 tópicos canónicos (Master Spec Sección 9.3).
  - Sanitización de texto para neutralizar directivas maliciosas de lenguaje e inyecciones de instrucciones (*prompt injection*).
  - Cálculo estricto de prevalencia con denominador real de la muestra observada ($N$), sin generalizaciones sin respaldo muestral.
  - Cita exacta de IDs de reseña de origen (`source_review_id`) y fragmentos de evidencia.
  - Endpoint REST: `GET /api/v1/reviews-mining/{game_id}`.
  - Interfaz de usuario **Review Mining** (`/reviews-mining`): tarjetas por tópico, barras de proporción de elogios vs quejas, badge de denominador muestral y citas de evidencia.
- Registro de decisión de arquitectura: `docs/adr/ADR-008-competitor-similarity-y-review-mining.md`.

### Añadido (Fase 8 — PC Expansion)
- Conectores y registro de capacidades multi-tienda de PC en `backend/app/services/pc_expansion.py`:
  - `IGDBConnector`: Manejo de autenticación OAuth Client Credentials en Twitch Developer Console, ingestión de metadatos editoriales y cumplimiento estricto del aviso de atribución requerido ("Data provided by IGDB").
  - `ItchConnector`: Ingestión de feeds RSS públicos de descubrimiento (`/feed/new.xml`, `/feed/featured.xml`, `/feed/sales.xml`) distinguiendo datos públicos de datos privados de creadores con autorización OAuth.
  - Conectores `GOGConnector` y `EpicGamesConnector`: Operan en modo `metadata_only` o `unsupported` sin emulación de launcher ni scraping anti-bot, evitando falsas métricas en cero.
  - Servicio de mapeo de identidad `CrossPlatformService` (`game_cross_references`): vinculación multiplataforma con niveles de confianza (`verified`, `high_confidence`, `candidate`, `manual`) y métodos documentados, impidiendo fusiones erróneas de juegos por coincidencia débil de nombre.
  - Endpoints REST: `GET /api/v1/cross-platform/stores`, `GET /api/v1/cross-platform/{game_id}`, `POST /api/v1/cross-platform/link`.
  - Interfaz de usuario **PC Expansion** (`/pc-expansion`): catálogo de storefronts soportados, estados de servicio, capacidades autorizadas y banner de atribución de IGDB.
- Registro de decisión de arquitectura: `docs/adr/ADR-009-pc-expansion-cross-platform-mapping.md`.

### Añadido (Fase 9 — Seasonality & Release Calendar)
- Motor de inteligencia estacional y calendario en `backend/app/services/seasonality.py`:
  - Catálogo de eventos de la industria (`industry_events`): Steam Seasonal Sales (Spring, Summer, Autumn, Scream Fest, Winter), Steam Next Fest (febrero, junio, octubre) con fuentes oficiales documentadas.
  - Analizador de colisiones de lanzamiento (`analyze_launch_collision`): detección de conflictos en ventanas temporales configurables ($\pm 14$ días), cálculo de score de colisión (0 a 100), nivel de riesgo (`low`, `moderate`, `high`, `extreme`) y recomendación de ventanas alternativas despejadas.
  - Análisis por cohortes históricas de lanzamiento (`get_cohort_analysis`): agrupación por año, mes o modalidad Early Access con disclaimer explícito de correlación temporal frente a causalidad.
  - Endpoints REST: `GET /api/v1/seasonality/events`, `GET /api/v1/seasonality/cohorts`, `GET /api/v1/seasonality/launch-collision`.
  - Interfaz de usuario **Seasonality & Calendar** (`/seasonality`): simulador interactivo de colisiones por fecha, avisos de eventos en conflicto, ventanas alternativas despejadas y desglose de cohortes.
- Migración de base de datos Alembic: `backend/alembic/versions/003_phases_7_8_9_schema.py`.
- Registro de decisión de arquitectura: `docs/adr/ADR-010-seasonality-cohorts-y-collision-detection.md`.


### Añadido (Fase 4 — Player and Review History)
- Servicio de series temporales de concurrencia y reseñas en `backend/app/services/player_review_sync.py`:
  - Captura periódica de jugadores concurrentes (`ISteamUserStats/GetNumberOfCurrentPlayers/v1/`) en `player_snapshots`.
  - Ingesta de reseñas (`IUserReviewsService/GetAppReviews/v1/`) con cálculo de `positive_ratio` y `review_delta` en `review_snapshots`.
  - Extracción y retención segura de items de reseña individuales (`review_items`).
  - Endpoints REST: `POST /games/{id}/snapshot-players`, `POST /games/{id}/sync-reviews`, `GET /games/{id}/history`, `POST /games/{id}/watch`, `DELETE /games/{id}/watch`.
  - Interfaz de usuario **Player Analytics** (`/players`): línea de tiempo cronológica, seguimiento de picos CCU y disparador de snapshot bajo demanda.

### Añadido (Fase 5 — Market Analytics & Rollups)
- Motor de analítica determinista en `backend/app/services/analytics_engine.py`:
  - Cálculo de rollups por juego (`game_metric_rollups`): promedio, máximo, mínimo de CCU, recuento de observaciones, delta de reseñas, días de descuento y cobertura de datos (`calculation_version = "analytics-v1"`).
  - Cálculo de rollups por segmento de mercado (`market_segment_rollups`): total de títulos, títulos activos, mediana de precio en centavos (evitando distorsión de juegos AAA), ratio de concentración del Top 1 y lanzamientos recientes.
  - Función determinista de crecimiento con manejo estricto de baselines nulos o en cero (Sección 7.4).
  - Endpoints REST: `GET /api/v1/analytics/rollups/{gp_id}`, `GET /api/v1/analytics/segments`, `POST /api/v1/analytics/compute-rollups`.
  - Interfaz de usuario **Genre Analytics** (`/genres`): tabla de métricas por género, juegos activos, medianas de precio y concentración de mercado.

### Añadido (Fase 6 — Niche Finder Algorithm)
- Algoritmo de detección y puntuación de nichos en `backend/app/services/niche_finder.py`:
  - Implementación estricta de la fórmula maestra de oportunidad (Sección 8.2):
    `Opportunity = 0.30*Demand + 0.25*Growth + 0.20*CompetitiveSpace + 0.15*CommercialFeasibility + 0.10*EvidenceQuality`.
  - Protección contra falsas conclusiones: segmentos sin datos o con muestra insuficiente devuelven `insufficient_data` con limitaciones explícitas sin fabricar scores (Sección 8.3).
  - Asignación de bandas de confianza (`high`, `medium`, `low`) y versionado de algoritmo (`score_version = "niche-v1"`).
  - Endpoints REST: `GET /api/v1/niches`, `POST /api/v1/niches/analyze`, `GET /api/v1/niches/{id}`.
  - Interfaz de usuario **Niche Finder** (`/niches`): ranking visual de oportunidades, desglose con barras de los 5 factores, badges de confianza, advertencias de limitaciones y recálculo instantáneo.

## [1.1.0] - 2026-11-23

### Añadido (Fase 2 — Steam Catalog Ingestion & Checkpointing)
- Servicio de ingestión masiva e incremental de catálogo en `backend/app/services/catalog_sync.py`:
  - Consumo directo del endpoint oficial `IStoreService/GetAppList/v1/`.
  - Paginación basada en cursor `last_appid` con soporte para lotes configurables de hasta 50,000 registros.
  - Almacenamiento y auditoría de payloads originales en `raw_payloads` con hash SHA-256 (`parser_version = "catalog-v1"`).
  - Deduplicación idempotente de títulos y vinculación en `game_platforms` (clave única `platform_id` + `external_id`).
  - Distinción entre juegos completos (`game`) y contenidos adicionales (`dlc`).
  - Persistencia de checkpoints en tabla `ingestion_checkpoints` (migración Alembic `002_ingestion_checkpoints.py`) permitiendo reanudar la ingesta interrumpida sin escaneos duplicados.
- Endpoints de control de catálogo:
  - `POST /api/v1/catalog/sync`: Inicia o reanuda la sincronización de lotes del catálogo.
  - `GET /api/v1/catalog/status`: Consulta el cursor actual, registros totales importados y estado del proceso.

### Añadido (Fase 3 — Metadata and Storefront Normalization)
- Servicio de normalización de datos de tienda en `backend/app/services/metadata_sync.py`:
  - Consumo del endpoint Storefront `/api/appdetails?appids={APP_ID}&cc={COUNTRY_CODE}&l={LANGUAGE}`.
  - Degradación elegante ante fallos (`success=false`, aplicaciones retiradas o bloqueadas regionalmente) registrando estado `unavailable` sin inventar métricas ni asignar precios a cero.
  - Persistencia de precios en unidades menores (centavos) en `price_snapshots` (`regular_price_minor`, `final_price_minor`, `discount_percent`, `currency`, `country_code`).
  - Normalización y mapeo de desarrolladores y editores en `organizations`, `game_developers` y `game_publishers`.
  - Extracción y normalización de taxonomías de tienda en `taxonomy_items` y `game_taxonomies`.
  - Extracción segura de fechas de lanzamiento (`release_date`, `release_date_precision`, `release_status`) y detección de `is_early_access`.
  - Versionado estricto del parser (`parser_version = "storefront-v1"`).
- Integración en tareas asíncronas de Celery (`sync_catalog` y `sync_game_metadata` en `backend/app/workers/tasks.py`).
- Endpoint enriquecido `GET /api/v1/games/{game_id}` y trigger bajo demanda `POST /api/v1/games/{game_id}/sync-metadata`.
- Vistas de Frontend:
  - Nueva pantalla **Game Explorer** (`/games`) con buscador en tiempo real, filtros, tarjetas de catálogo y modal de ficha técnica detallada (precios, desarrolladores, editores, géneros y sincronización manual de metadatos).
  - Panel ampliado en **Data Sources** (`/sources`) con estado del cursor `last_appid`, total de títulos registrados y botón de sincronización de lotes.
- 5 nuevas pruebas unitarias y de integración en `backend/tests/test_catalog_and_metadata.py` (total de 15 tests pasando al 100%).

## [1.0.0] - 2026-11-23

### Añadido (Fase 0 — Discovery y Validación de Fuentes)
- Matriz exhaustiva de fuentes y endpoints en `docs/sources_matrix.md`:
  - Steamworks Web API (`IStoreService/GetAppList/v1/`)
  - Steam Storefront API (`/api/appdetails`)
  - Steam User Stats (`ISteamUserStats/GetNumberOfCurrentPlayers/v1/`)
  - Steam User Reviews (`IUserReviewsService/GetAppReviews/v1/`)
  - Taxonomía y tags de Steam
  - Proveedores de terceros y estado: SteamSpy, IGDB, itch.io, GOG, Epic Games Store, PCGamingWiki y política de SteamDB.
- Architecture Decision Records en `docs/adr/`:
  - `ADR-001`: Steam como fuente primaria.
  - `ADR-002`: PostgreSQL + TimescaleDB como motor unificado relacional y de series de tiempo.
  - `ADR-003`: FastAPI para API REST y Celery con Redis para tareas asíncronas de cómputo/ingesta.
  - `ADR-004`: Snapshots propios e inmutabilidad de observaciones históricas.
  - `ADR-005`: Principio de evidencia antes de IA (cómputos deterministas vs inferencia).
  - `ADR-006`: Generación de exportaciones profesionales como tareas asíncronas.
  - `ADR-007`: Conectores por capacidades y degradación elegante.
- Fixtures de contrato sanitizados para pruebas en `backend/tests/fixtures/`:
  - `steam_applist.json`
  - `steam_appdetails_success.json`
  - `steam_appdetails_empty.json`
  - `steam_numberofcurrentplayers.json`
  - `steam_reviews.json`
  - `steamspy_appdetails.json`
  - `igdb_games.json`

### Añadido (Fase 1 — Foundation)
- Estructura monorepo con configuración Docker Compose (`docker-compose.yml`, `.env.example`).
- Backend FastAPI en `backend/app/`:
  - Modelos relacionales SQLAlchemy 2.x completos (Catálogo, Fuentes, Snapshots, Rollups, Investigación, Usuarios, Auditoría).
  - Configuración y migración inicial Alembic (`001_initial_schema.py`) verificada con éxito.
  - Sistema de seguridad con autenticación JWT, hashing moderno de contraseñas y control de roles (`owner`, `admin`, `analyst`, `viewer`).
  - Auto-bootstrap del primer usuario registrado como `owner`.
  - Conectores `SteamConnector` y registry `CONNECTORS_METADATA` con políticas de rate limiting y contratos documentados.
  - Endpoints REST `/api/v1/health`, `/api/v1/ready`, `/api/v1/auth`, `/api/v1/dashboard/overview`, `/api/v1/sources`.
  - Configuración de Celery con 11 colas dedicadas por prioridad y Celery Beat schedule.
  - 10 pruebas unitarias y de integración pasando al 100% en pytest (`test_health.py`, `test_auth.py`, `test_connectors_contracts.py`).
- Frontend Next.js + TypeScript + Tailwind CSS en `frontend/src/`:
  - Tema oscuro profesional (grafito/azul con acentos cian).
  - Barra lateral con las 16 secciones funcionales requeridas.
  - Dashboard de visión general (`Overview`) con tarjetas de métricas, indicadores de procedencia y frescura, tabla de juegos y estado de conectores.
  - Pantalla de inicio de sesión y registro de propietario (`/login`).
  - Vista de gestión y pruebas de conectores (`/sources`).
