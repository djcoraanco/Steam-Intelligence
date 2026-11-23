# ADR-012: Hardening de Producción, Estrategia de Backups y Observabilidad

## Estado
Aceptado

## Contexto
Steam Intelligence es una plataforma self-hosted destinada a funcionar de forma desatendida y continua en servidores VPS o locales (Master Spec Sección 16, 17 y 18). Se requiere:
1. Asegurar la persistencia de datos históricos ante fallos mediante políticas de backup verificables (RPO < 24h, RTO < 4h).
2. Proteger secretos y credenciales (evitar que tokens o contraseñas se registren en logs o queden expuestos).
3. Configurar topología Docker segura con redes privadas aisladas (DB y Redis nunca expuestos a Internet).
4. Proporcionar métricas operativas de salud y telemetría de ingesta.

## Decisión
1. **Redes y Contenedores**:
   - Red `internal`: PostgreSQL, Redis y Celery Workers operan sin mapeo de puertos públicos al host.
   - Red `public_proxy`: Exclusiva para la API FastAPI y Frontend Next.js.
2. **Backups Automatizados**:
   - Scripts `scripts/backup.ps1` (Windows) y `scripts/backup.sh` (Linux) con rotación y retención de 14 días.
   - Script de prueba de restauración automatizada (`scripts/restore_test.py`) que valida la integridad de las 13 tablas relacionales maestras.
3. **Observabilidad y Seguridad**:
   - `structlog` configurado con filtro de secretos y claves sensibles.
   - Endpoints `/api/v1/health`, `/api/v1/ready` y `/api/v1/metrics` para monitorización operativa continua.

## Consecuencias
- **Positivas**: Operación autónoma segura y resiliente; aislamiento de red; trazabilidad de errores; recuperación probada ante desastres.
- **Limitaciones**: Requiere configurar tareas programadas (cron o Windows Task Scheduler) para la ejecución periódica de backups en el host.
