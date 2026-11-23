# Steam Intelligence - PowerShell Local Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       STEAM INTELLIGENCE - LOCAL LAUNCHER" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$RootPath = $PSScriptRoot

Write-Host "[1/2] Iniciando Backend API (FastAPI en http://127.0.0.1:8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$RootPath\backend'; & .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

Write-Host "[2/2] Iniciando Frontend (Next.js en http://localhost:3000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$RootPath\frontend'; npm run dev"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "  Plataforma iniciada con exito:" -ForegroundColor Green
Write-Host "  - Panel Web:     http://localhost:3000" -ForegroundColor Green
Write-Host "  - API Swagger:   http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""
