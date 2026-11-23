# ADR-006: Generación de Exportaciones como Tareas Asíncronas

## Estado
Aceptado

## Contexto
Los informes ejecutivos profesionales en PDF (con ReportLab y gráficos vectoriales) y presentaciones en PPTX (con python-pptx y temas oscuros) pueden requerir procesar miles de registros y tardar entre 5 y 45 segundos en compilarse. Mantener estas peticiones dentro del ciclo de vida HTTP síncrono causaría bloqueos de workers de API y timeouts en reverse proxies (Nginx / Cloudflare).

## Decisión
Las exportaciones de informes se gestionan como jobs asíncronos (`POST /api/v1/reports/{id}/export` -> `export_id` -> worker de Celery en cola `exports` -> persistencia en volumen privado `/app/exports` -> notificación de finalización -> descarga autorizada `GET /api/v1/exports/{id}`).

## Consecuencias
- La API permanece ágil y no sufre bloqueos ni timeouts.
- Los archivos exportados se guardan con política de retención automática (30 días por defecto) y control de acceso por roles.
