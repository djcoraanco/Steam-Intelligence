# Matriz de Fuentes, Endpoints y Capacidades — Steam Intelligence

Esta matriz documenta el inventario verificado de proveedores y endpoints para la plataforma Steam Intelligence, cumpliendo los criterios de la Fase 0 de la especificación técnica.

---

## 1. Fuentes Activas (MVP)

| Proveedor | Endpoint / Servicio | Auth Requerida | Parámetros Clave | Capacidades Validadas | Rate Limit y Políticas | Estado |
|---|---|---|---|---|---|---|
| **Steamworks Web API** | `https://api.steampowered.com/IStoreService/GetAppList/v1/` | Web API Key (`key`) | `key`, `if_modified_since`, `include_games`, `include_dlc`, `last_appid`, `max_results` (hasta 50,000) | `catalog`, `incremental_sync` | Paginación por cursor `last_appid`. Respetar backoff exponencial. | **active** |
| **Steam Storefront** | `https://store.steampowered.com/api/appdetails` | Pública (sin key) | `appids`, `cc` (código país ISO 3166-1), `l` (idioma) | `metadata`, `prices`, `genres`, `tags`, `screenshots`, `media`, `platforms` | Endpoint público de tienda. Conservador: máx 1 req/1.5s por IP con jitter. Manejar `success=false`. Cachear payloads. | **active** |
| **Steam User Stats** | `https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/` | Pública / Key opcional | `appid` | `current_players` (instantáneo) | Medición puntual instantánea. No serie histórica nativa. Rate limit: 200 req/min con retry backoff. | **active** |
| **Steam User Reviews** | `https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/` | Pública / Key opcional | `appid`, `filter`, `language`, `cursor`, `review_type`, `purchase_type`, `num_per_page` | `reviews_summary`, `review_items`, `positive_ratio` | Paginación estricta por cursor URL encoded (`cursor=*`). No exceder 100 reseñas/pág. Cumplir retención de texto. | **active** |
| **Steam Tags** | Storefront tags vía appdetails y taxonomía oficial | Pública | `appid` | `tags`, `categories`, `tag_ranks` | Mapeo a diccionario interno versionado de taxonomía. | **active** |

---

## 2. Fuentes de Terceros y Expansión PC

| Proveedor | Endpoint / Base URL | Auth Requerida | Capacidades Declaradas | Estado MVP | Términos y Notas de Cumplimiento |
|---|---|---|---|---|---|
| **SteamSpy** | `https://steamspy.com/api.php?request=appdetails&appid={id}` | Pública / API Key para consultas masivas | `owner_estimates`, `average_playtime`, `recent_players` | **disabled** (configurable) | Fuente de estimaciones de terceros. Marcar `data_type = estimated`, `confidence = estimated`. Nunca tratar como ventas exactas. |
| **IGDB** | `https://api.igdb.com/v4/games` | OAuth 2.0 Twitch Client Credentials (`Client-ID`, `Bearer <token>`) | `metadata`, `franchises`, `game_modes`, `themes`, `cross_platform_relations`, `covers` | **planned** | Requiere atribución comercial obligatoria según términos de Twitch/IGDB. Exige renovación periódica de Bearer tokens. |
| **itch.io** | Feeds RSS: `/feed/new.xml`, `/feed/sales.xml`. API: `/api/1/key/...` | API Key de cuenta para API privada; ninguno para RSS | `public_discovery_data`, `developer_games` (con cuenta propia) | **planned** | No asume acceso a ventas privadas de terceros. Solo RSS público o juegos del creador autenticado. |
| **GOG** | Portal desarrolladores / Catálogo público | Según endpoint | `metadata_only`, `prices` | **planned** / metadata_only | No existe API pública oficial completa de métricas de mercado. No realizar scraping no autorizado. |
| **Epic Games Store** | Dev Portal / Catálogo de tienda | Verificación por caso | `metadata_only`, `catalog` | **planned** / unavailable | Epic Online Services (EOS) no equivale a API de ventas de tienda. Sin acuerdo o API pública documentada, permanece desactivada. |
| **PCGamingWiki** | Web API de MediaWiki / Cargo | API pública respetando términos | `technical_specs`, `game_engines`, `compatibility` | **planned** | Datos técnicos y de motor. No usar para demanda comercial. |
| **SteamDB** | `https://steamdb.info/` | No hay API pública libre autorizada para scraping masivo | N/A | **restricted** / manual_only | Prohibido scraping automatizado no autorizado. Si se incorpora un dato manual o vía dataset autorizado, citar como proveedor externo. |

---

## 3. Modelo de Estados de Proveedor y Datos

- **Estados de Proveedor**: `active`, `planned`, `unavailable`, `deprecated`, `disabled`.
- **Estados de Disponibilidad de Métrica**: `available`, `stale`, `unavailable`, `unsupported`, `not_applicable`, `invalid`, `estimated`.
- **Tipos de Dato (`data_type`)**: `official`, `third_party`, `estimated`, `derived`, `user_provided`, `synthetic`.
