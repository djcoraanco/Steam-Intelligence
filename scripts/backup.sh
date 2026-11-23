#!/usr/bin/env bash
# Steam Intelligence - Automated Database Backup Script (Linux / Production VPS)
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/steam_intel_backup_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "[INFO] Starting Steam Intelligence backup at $(date)..."

if command -v docker >/dev/null 2>&1 && docker compose ps postgres >/dev/null 2>&1; then
    docker compose exec -T postgres pg_dump -U steam steam_intelligence | gzip > "${BACKUP_FILE}"
    echo "[INFO] Backup generated via Docker: ${BACKUP_FILE}"
else
    pg_dump -U "${DB_USER:-steam}" "${DB_NAME:-steam_intelligence}" | gzip > "${BACKUP_FILE}"
    echo "[INFO] Backup generated locally: ${BACKUP_FILE}"
fi

# Retention policy
find "${BACKUP_DIR}" -name "steam_intel_backup_*.sql.gz" -mtime +"${RETENTION_DAYS}" -delete
echo "[INFO] Backup completed and old backups cleaned (> ${RETENTION_DAYS} days)."
