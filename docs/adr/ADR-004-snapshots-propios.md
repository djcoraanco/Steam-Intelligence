# ADR-004: Snapshots Propios e Inmutabilidad Histórica

## Estado
Aceptado

## Contexto
Las APIs oficiales como Steam `GetNumberOfCurrentPlayers` sólo entregan el valor del instante presente en que se invoca la petición. Steam no ofrece un endpoint oficial público con la serie temporal granular de jugadores de meses o años pasados. 

## Decisión
Steam Intelligence construirá y mantendrá su propio historial inmutable mediante snapshots periódicos (`player_snapshots`, `price_snapshots`, `review_snapshots`, `ranking_snapshots`). Cada snapshot almacena `observed_at`, `source_id`, `data_type`, `quality_score`, y una referencia al payload crudo (`raw_payload_id`). Nunca se sobrescribirán ni borrarán observaciones pasadas al actualizar el catálogo.

## Consecuencias
- La precisión y profundidad del historial comienza desde la primera fecha de ingesta.
- Los datos históricos son propiedad del usuario y residen en su propia base de datos (local-first/self-hosted).
- Se requiere una política explícita de agregación (rollups horarios/diarios) y retención para optimizar el almacenamiento a largo plazo.
