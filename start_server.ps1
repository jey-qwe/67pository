# Trinity Context Core - Server Startup Script
# This script properly sets up the Python path and starts the FastAPI server

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Trinity Context Core - Starting Server" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[INFO] Starting FastAPI server..." -ForegroundColor Yellow
Write-Host ""

# Start the server using run.py
python run.py

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Server stopped" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
