@echo off
title RAG System Launcher
echo ========================================
echo   RAG Knowledge Base System
echo ========================================
echo.

cd /d "%~dp0"

echo Starting Backend (port 8000)...
start "RAG-Backend" /min cmd /c "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo Starting Frontend (port 5173)...
start "RAG-Frontend" /min cmd /c "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   System started!
echo.
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo   Admin:    admin / 123456
echo.
echo   Close the minimized CMD windows
echo   to stop the services.
echo ========================================
pause
