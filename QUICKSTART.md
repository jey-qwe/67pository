# Trinity Context Core - Quick Start Guide

## Starting the Server

### Option 1: Use run.py (Recommended - Fixes import issues)
```bash
python run.py
```

### Option 2: Use the batch file (Windows)
```bash
start_server.bat
```

### Option 3: Use PowerShell script
```powershell
.\start_server.ps1
```

## Why run.py?

The `run.py` file fixes the **"ModuleNotFoundError: No module named 'src'"** error by:
1. Adding the project root to `sys.path` before importing
2. Then starting uvicorn with the correct module path

## Server Info

- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## After Starting

1. Check http://localhost:8000/ping (should return "pong")
2. Open http://localhost:8000/docs for Swagger UI
3. Run seeding script: `python src/scripts/seed.py`
