@echo off
REM Trinity Context Core - Server Startup Script (Windows CMD)
REM This script properly sets up the Python path and starts the FastAPI server

echo ============================================================
echo Trinity Context Core - Starting Server
echo ============================================================
echo.

REM Set the PYTHONPATH to include the project root
set PYTHONPATH=%~dp0

echo [INFO] Starting FastAPI server...
echo.

REM Start the server using run.py
python run.py

echo.
echo ============================================================
echo Server stopped
echo ============================================================
