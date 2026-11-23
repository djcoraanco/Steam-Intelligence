# Steam Intelligence

Plataforma privada, self-hosted, de inteligencia de mercado para videojuegos de PC. Recopila datos públicos y autorizados, mantiene un historial propio mediante snapshots inmutables, analiza demanda y competencia, y genera informes auditables antes de invertir en el desarrollo de un videojuego.

---

## Arquitectura

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS (Tema oscuro profesional grafito/azul/cian).
- **Backend API**: Python 3.12+ con FastAPI.
- **Base de Datos**: PostgreSQL 16 con TimescaleDB para series temporales y rollups.
- **Colas y Tareas**: Redis 7 + Celery Workers y Celery Beat Scheduler con 11 colas por prioridad.
- **ORM & Migraciones**: SQLAlchemy 2.0 y Alembic.
- **Contratos & Validación**: Pydantic v2.

---

## Inicio Rápido (Desarrollo Local)

### 1. Variables de Entorno

```bash
cp .env.example .env
```

### 2. Backend

```bash
cd backend
python -m venv .venv
# Activar entorno (Windows: .venv\Scripts\activate, Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
alembic upgrade head
python -m pytest
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

La aplicación web estará accesible en `http://localhost:3000` y la API en `http://localhost:8000`.

---

## Despliegue con Docker Compose (Self-Hosted)

Para producción en VPS con Docker:

```bash
docker compose up -d --build
```

Servicios levantados:
- `frontend`: Puerto 3000
- `api`: Puerto 8000
- `postgres`: Puerto interno 5432 (TimescaleDB)
- `redis`: Puerto interno 6379
- `worker`: Celery workers (colas de catalog, players, reviews, etc.)
- `scheduler`: Celery Beat

---

## Documentación y Decisiones Arquitectónicas (ADRs)

- [Matriz de Fuentes y Endpoints](docs/sources_matrix.md)
- [ADR-001: Steam como fuente primaria](docs/adr/ADR-001-steam-como-fuente-primaria.md)
- [ADR-002: PostgreSQL + TimescaleDB](docs/adr/ADR-002-postgresql-timescaledb.md)
- [ADR-003: FastAPI + Celery](docs/adr/ADR-003-fastapi-celery.md)
- [ADR-004: Snapshots propios](docs/adr/ADR-004-snapshots-propios.md)
- [ADR-005: Principio de evidencia antes de IA](docs/adr/ADR-005-evidencia-antes-de-ia.md)
- [ADR-006: Exportaciones como jobs](docs/adr/ADR-006-exportaciones-como-jobs.md)
- [ADR-007: Conectores por capacidades](docs/adr/ADR-007-conectores-por-capacidades.md)
