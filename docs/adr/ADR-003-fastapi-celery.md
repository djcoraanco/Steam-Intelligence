# ADR-003: Arquitectura FastAPI y Celery

## Estado
Aceptado

## Contexto
Las consultas de frontend (lectura de dashboards, métricas de juegos, perfiles) requieren tiempos de respuesta inmediatos (< 200 ms). Por otro lado, la sincronización de catálogo de 100,000+ juegos, el cálculo de métricas agregadas por cohorte, el review mining y la exportación de documentos PDF/PPTX son procesos que pueden tomar minutos u horas.

## Decisión
Separar el ciclo de vida de la API web (FastAPI) de los procesos de ingestión y cómputo asíncrono utilizando Celery con Redis como message broker y result backend. Celery Beat actuará como planificador periódico.

## Consecuencias
- Las peticiones HTTP nunca ejecutan ingestión masiva bloqueante.
- Se configuran colas dedicadas por prioridad (`catalog`, `metadata`, `players_high_priority`, `players_standard`, `reviews`, `prices`, `rankings`, `analytics`, `ai`, `exports`, `maintenance`) para evitar que tareas lentas bloqueen mediciones críticas de alta frecuencia.
- Se implementan Server-Sent Events (SSE) en FastAPI para reportar el progreso de `research_runs` al usuario en tiempo real.
