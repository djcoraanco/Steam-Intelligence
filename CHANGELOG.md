# Changelog

Todas las modificaciones notables a este proyecto se documentarán en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/)
y el proyecto se adhiere a la Especificación Maestra de Steam Intelligence.

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
