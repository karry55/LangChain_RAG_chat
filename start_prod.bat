@echo off
title RAG System - Production Mode
echo ========================================
echo   RAG Production Mode (4 Workers)
echo ========================================
echo.

cd /d "%~dp0"

echo Starting Backend with 4 workers (port 8000)...
start "RAG-Backend-Prod" cmd /c "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level warning"

echo Starting Frontend (port 5173)...
start "RAG-Frontend" cmd /c "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   Production mode started!
echo   Backend: 4 workers on port 8000
echo   Frontend: http://localhost:5173
echo ========================================
pause
