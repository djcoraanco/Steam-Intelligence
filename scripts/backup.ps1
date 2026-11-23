# Steam Intelligence - Automated Database Backup Script (PowerShell / Windows VPS)
param(
    [string]$BackupDir = "./backups",
    [int]$RetentionDays = 14
)

$ErrorActionPreference = "Stop"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupPath = Join-Path $BackupDir "steam_intel_backup_$Timestamp.sql"

if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

Write-Host "Starting Steam Intelligence backup at $(Get-Date)..." -ForegroundColor Cyan

# Check if pg_dump is available in PATH or inside docker
if (Get-Command pg_dump -ErrorAction SilentlyContinue) {
    pg_dump -U steam steam_intelligence -f $BackupPath
    Write-Host "Database dumped to $BackupPath" -ForegroundColor Green
} else {
    Write-Host "pg_dump not found in local PATH. Running backup via Docker Compose..." -ForegroundColor Yellow
    docker compose exec -T postgres pg_dump -U steam steam_intelligence > $BackupPath
    Write-Host "Docker database dumped to $BackupPath" -ForegroundColor Green
}

# Retention cleanup
$Cutoff = (Get-Date).AddDays(-$RetentionDays)
Get-ChildItem -Path $BackupDir -Filter "steam_intel_backup_*.sql" | Where-Object { $_.LastWriteTime -lt $Cutoff } | Remove-Item -Force
Write-Host "Backup completed and retention policy enforced ($RetentionDays days)." -ForegroundColor Green
