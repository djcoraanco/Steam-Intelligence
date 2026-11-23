# ADR-002: PostgreSQL con TimescaleDB

## Estado
Aceptado

## Contexto
El sistema requiere almacenar entidades relacionales complejas (juegos, plataformas, desarrolladores, taxonomías, usuarios, permisos, proyectos de investigación) y a la vez millones de mediciones cronológicas continuas de alta frecuencia (snapshots de jugadores concurrentes cada 15-30 min, precios, reseñas, rankings).

## Decisión
Utilizar PostgreSQL 16 con la extensión TimescaleDB integrada como motor unificado de persistencia.

## Consecuencias
- **Positivas**: Un único motor relacional con soporte ACID, consultas SQL estándar, JSONB para payloads crudos, y hypertables optimizadas para series de tiempo, compresión y rollups analíticos continuos.
- **Negativas/Limitaciones**: Requiere verificar la versión de TimescaleDB y habilitar la extensión en la base de datos de producción (`CREATE EXTENSION IF NOT EXISTS timescaledb;`).
- **Compatibilidad**: Para entornos de desarrollo local o testing rápido unitario sin contenedor TimescaleDB activo, el ORM SQLAlchemy debe modelar tablas estándar compatibles que TimescaleDB convierte en hypertables en migración de producción.
