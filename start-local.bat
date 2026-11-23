@echo off
title Steam Intelligence - Local Launcher
echo ========================================================
echo        STEAM INTELLIGENCE - LOCAL LAUNCHER
echo ========================================================
echo.

echo [1/2] Iniciando Backend API (FastAPI en http://127.0.0.1:8000)...
start "Steam Intelligence - Backend API" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo [2/2] Iniciando Frontend (Next.js en http://localhost:3000)...
start "Steam Intelligence - Frontend UI" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================================
echo   Plataforma iniciada con exito:
echo   - Panel Web:     http://localhost:3000
echo   - API Swagger:   http://127.0.0.1:8000/docs
echo ========================================================
echo.
pause
