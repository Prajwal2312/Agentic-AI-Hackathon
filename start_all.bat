@echo off
title PRIVESCAN AI - Launcher
echo ========================================================
echo   Launching PRIVESCAN AI Multi-Agent Compliance System
echo ========================================================
echo.
echo Starting Backend API (FastAPI on http://localhost:8000)...
start "PRIVESCAN Backend API" cmd /k "powershell -ExecutionPolicy Bypass -File .\start_backend.ps1"

timeout /t 3 /nobreak >nul

echo Starting Frontend UI (Next.js on http://localhost:3000)...
start "PRIVESCAN Frontend UI" cmd /k "powershell -ExecutionPolicy Bypass -File .\start_frontend.ps1"

echo.
echo Both servers launched in separate windows!
echo Frontend: http://localhost:3000
echo Backend API Docs: http://localhost:8000/docs
echo ========================================================
