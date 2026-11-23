# Steam Intelligence

Plataforma privada, self-hosted, de inteligencia de mercado para videojuegos de PC basada en la **Especificación Maestra de Producto y Arquitectura v1.0**.

Recopila datos públicos y autorizados de plataformas de PC (Steam, IGDB, itch.io, GOG, Epic Games Store), mantiene un historial propio mediante snapshots inmutables, analiza demanda y competencia sin falsas precisiones, detecta nichos de oportunidad mediante algoritmos ponderados y genera informes de nivel directivo en múltiples formatos (PDF, PPTX, XLSX, CSV, JSON).

---

## Arquitectura y Stack Tecnológico

```
  +------------------------------------------------------------------+
  |              Frontend: Next.js 14 + Tailwind CSS                 |
  |         16 Vistas Operativas · Dashboard · Tema Grafito          |
  +---------------------------------+--------------------------------+
                                    | REST API / Auth JWT
  +---------------------------------v--------------------------------+
  |              Backend API: FastAPI (Python 3.12+)                 |
  |  Validación Pydantic v2 · ORM SQLAlchemy 2.0 · Migraciones Alembic|
  +--------+------------------------+-----------------------+--------+
           |                        |                       |
  +--------v-------+       +--------v-------+      +--------v--------+
  |  PostgreSQL 16 |       |  Redis 7       |      |  Exports Engine |
  |  TimescaleDB   |       |  Celery Beat   |      |  ReportLab (PDF)|
  |  Series Snapshots      |  11 Colas      |      |  python-pptx    |
  |  Rollups & Niches      |  Workers Asinc |      |  openpyxl (XLSX)|
  +----------------+       +----------------+      +-----------------+
```

- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS + Lucide Icons.
- **Backend**: FastAPI con Pydantic v2 y SQLAlchemy 2.0.
- **Base de Datos Relacional y Series Temporales**: PostgreSQL 16 con extensión TimescaleDB.
- **Colas y Trabajos en Segundo Plano**: Redis 7 + Celery Workers + Celery Beat.
- **Capa de Investigación con IA**: Herramientas tipadas internas, mitigación contra prompt-injection y generación estructurada evidence-first (Sección 12.4).
- **Motor de Exportaciones**:
  - **PDF**: Documentos vectoriales reproducibles con ReportLab, numeración de página y texto seleccionable.
  - **PPTX**: Presentaciones 16:9 widescreen profesionales con tema oscuro mediante `python-pptx`.
  - **XLSX**: Hojas de cálculo multilibro con `openpyxl`.
  - **CSV / JSON**: Volcados tabulares y reproducibilidad de datos.

---

## Cobertura de Fases del Proyecto

| Fase | Título | Estado | Componentes Clave |
|---|---|---|---|
| **Fase 0** | Discovery & Sources Matrix | ✅ Completado | Matriz de proveedores, cuotas, ToS, fixtures y ADRs iniciales |
| **Fase 1** | Foundation | ✅ Completado | Monorepo, Docker Compose, Postgres, Alembic, Auth JWT con roles (Owner, Admin, Analyst, Viewer) |
| **Fase 2** | Steam Catalog Sync | ✅ Completado | `IStoreService/GetAppList/v1`, cursor checkpointing, deduplicación y `raw_payloads` SHA-256 |
| **Fase 3** | Storefront Metadata & Pricing | ✅ Completado | `appdetails`, normalización en centavos minor, taxonomías y degradación elegante |
| **Fase 4** | Player & Review History | ✅ Completado | `GetNumberOfCurrentPlayers` (CCU), `GetAppReviews`, positive ratio y retención de `review_items` |
| **Fase 5** | Market Analytics & Rollups | ✅ Completado | `game_metric_rollups`, `market_segment_rollups`, mediana de precio e índice de concentración HHI |
| **Fase 6** | Niche Finder Algorithm | ✅ Completado | Fórmula oficial ($0.30 D + 0.25 G + 0.20 CS + 0.15 CF + 0.10 EQ$), bandas de confianza y guardarraíles |
| **Fase 7** | Competitor & Review Mining | ✅ Completado | Similitud Jaccard, Head-to-Head matrix, minería sobre 15 tópicos con denominador muestral y citas de IDs |
| **Fase 8** | PC Expansion | ✅ Completado | Conectores IGDB (Twitch OAuth + atribución), itch.io (RSS público), GOG y Epic (metadata_only) |
| **Fase 9** | Seasonality & Release Calendar | ✅ Completado | Detección de colisiones de lanzamiento, calendario de eventos Steam (Next Fest, Sales) y cohortes |
| **Fase 10** | AI & Report Exports | ✅ Completado | Capa AI Analyst con herramientas tipadas, exportador multiformato (PDF, PPTX, XLSX, CSV, JSON) |
| **Fase 11** | Production Hardening | ✅ Completado | Backups automatizados, prueba de restauración, métricas `/metrics`, redes aisladas y checklist |

---

## Despliegue en Producción (Docker Compose)

### 1. Preparar Entorno

```bash
cp .env.example .env
# Configura contraseñas seguras, JWT_SECRET y llaves opcionales (STEAM_WEB_API_KEY, IGDB, etc.)
```

### 2. Iniciar Servicios

```bash
docker compose up -d --build
```

Topología de redes y puertos:
- `http://localhost:3000`: Frontend Next.js (Red `public_proxy`)
- `http://localhost:8000`: API REST FastAPI y documentación Swagger (Red `public_proxy`)
- Red `internal`: PostgreSQL (5432) y Redis (6379) no expuestos a Internet.

### 3. Verificar Salud del Sistema

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/ready
curl http://localhost:8000/api/v1/metrics
```

---

## Estrategia de Backups y Recuperación ante Desastres

Para cumplir los objetivos operativos (**RPO < 24h** y **RTO < 4h**):

### Script de Backup Automático
- **Linux / VPS**:
  ```bash
  chmod +x scripts/backup.sh
  ./scripts/backup.sh
  ```
- **Windows / PowerShell**:
  ```powershell
  .\scripts\backup.ps1
  ```
Los backups se guardan en `./backups/` con compresión `.sql.gz` y retención automática de 14 días.

### Prueba de Restauración Automatizada
Ejecutar la suite de validación de esquema y restauración:
```bash
python scripts/restore_test.py
```

---

## Ejecución de Pruebas Automatizadas

El proyecto cuenta con una cobertura integral de pruebas unitarias, de integración y de contratos:

```bash
cd backend
python -m pytest
```

*Resultado actual:* **39 tests pasando al 100%**.

---

## Architecture Decision Records (ADRs)

Todas las decisiones críticas de arquitectura están documentadas en `docs/adr/`:

- [ADR-001: Steam como fuente primaria](docs/adr/ADR-001-steam-como-fuente-primaria.md)
- [ADR-002: PostgreSQL y TimescaleDB para series temporales](docs/adr/ADR-002-postgresql-timescaledb.md)
- [ADR-003: FastAPI y Celery para tareas asíncronas](docs/adr/ADR-003-fastapi-celery.md)
- [ADR-004: Recopilación de snapshots propios desde el primer día](docs/adr/ADR-004-snapshots-propios.md)
- [ADR-005: Principio de evidencia antes de la capa de IA](docs/adr/ADR-005-evidencia-antes-de-ia.md)
- [ADR-006: Exportaciones como trabajos en background](docs/adr/ADR-006-exportaciones-como-jobs.md)
- [ADR-007: Conectores por capacidades y estados de disponibilidad](docs/adr/ADR-007-conectores-por-capacidades.md)
- [ADR-008: Competitor Similarity y Minería de Reseñas sin Sesgo](docs/adr/ADR-008-competitor-similarity-y-review-mining.md)
- [ADR-009: Expansión PC, Conectores por Capacidades y Mapeo Cross-Platform](docs/adr/ADR-009-pc-expansion-cross-platform-mapping.md)
- [ADR-010: Inteligencia de Estacionalidad, Cohortes y Detección de Colisión](docs/adr/ADR-010-seasonality-cohorts-y-collision-detection.md)
- [ADR-011: Motor de Exportaciones Multiformato y Capa de Investigación con IA](docs/adr/ADR-011-motor-de-exportaciones-multiformato-y-ai-analyst.md)
- [ADR-012: Hardening de Producción, Estrategia de Backups y Observabilidad](docs/adr/ADR-012-hardening-de-produccion-backups-y-observabilidad.md)

---

## Licencia y Principios de Cumplimiento

Este software respeta los Términos de Servicio de Valve Steamworks, Twitch/IGDB, itch.io, GOG y Epic Games. No realiza scraping agresivo, no elude controles anti-bot ni presenta datos privados de terceros como si fueran públicos.
