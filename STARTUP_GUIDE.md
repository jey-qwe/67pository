# 🚀 Trinity Context Core - Startup Guide

## Prerequisites

Before starting, ensure you have:
- ✅ Python 3.8+ installed
- ✅ Docker Desktop installed and running
- ✅ Gemini API key (already configured in `.env`)

---

## 📋 Step-by-Step Startup Instructions

### Step 1: Start Qdrant Vector Database

Open a terminal in the project root directory (`c:\Users\guyla\Desktop\Quasar`) and run:

```bash
docker-compose up -d
```

**What this does:**
- Starts Qdrant in detached mode (runs in background)
- Creates persistent storage in `./qdrant_storage`
- Exposes ports 6333 (HTTP) and 6334 (gRPC)

**Verify Qdrant is running:**
```bash
docker ps
```

You should see `trinity_memory` container running.

**Access Qdrant UI:**
Open your browser and go to: http://localhost:6333/dashboard

---

### Step 2: Set Up Python Environment

#### Create and activate virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows PowerShell)
venv\Scripts\activate

# Or if using Command Prompt
venv\Scripts\activate.bat
```

#### Install dependencies:

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI
- Uvicorn
- Pydantic
- Qdrant Client
- Google Generative AI
- Python-dotenv

---

### Step 3: Verify Environment Configuration

Check that your `.env` file has the Gemini API key:

```bash
# View .env file (Windows)
type .env

# Should show:
# GEMINI_API_KEY=AIzaSyCj3DbIKSycyGNI8yWXunniTLOUF07QlZw
```

---

### Step 4: Start the FastAPI Server

From the project root, run:

```bash
# Using Python directly
python src/main.py

# OR using Uvicorn (recommended for development)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 🧪 Testing the API

### 1. Health Check

Open browser or use curl:

```bash
# Browser
http://localhost:8000/ping

# OR curl
curl http://localhost:8000/ping
```

**Expected response:**
```json
{
  "status": "ok",
  "message": "Trinity Context Core is running",
  "version": "0.1.0"
}
```

---

### 2. Access API Documentation

**Swagger UI (Interactive):**
```
http://localhost:8000/docs
```

**ReDoc (Alternative):**
```
http://localhost:8000/redoc
```

---

### 3. Add a Memory Card

Using PowerShell:

```powershell
$body = @{
    content = "User prefers Python for backend development and has expertise in FastAPI"
    tags = @("python", "preference", "backend")
    source = "user"
    importance = 8
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/memory/add" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

Or using curl:

```bash
curl -X POST "http://localhost:8000/api/v1/memory/add" \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"User prefers Python for backend development\",\"tags\":[\"python\",\"preference\"],\"source\":\"user\",\"importance\":8}"
```

---

### 4. Search Memory Cards

Using PowerShell:

```powershell
$searchBody = @{
    query = "What programming languages does the user prefer?"
    limit = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/memory/search" `
    -Method POST `
    -ContentType "application/json" `
    -Body $searchBody
```

Or using curl:

```bash
curl -X POST "http://localhost:8000/api/v1/memory/search" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"What programming languages does the user prefer?\",\"limit\":5}"
```

---

## 📚 Available API Endpoints

All endpoints are prefixed with `/api/v1`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/memory/add` | Add new memory card |
| POST | `/memory/search` | Search cards by semantic similarity |
| GET | `/memory/card/{id}` | Get card by ID |
| GET | `/memory/tags/{tag}` | Get cards by tag |
| GET | `/memory/all` | Get all cards (limit 100) |
| DELETE | `/memory/card/{id}` | Delete card by ID |

---

## 🛑 Stopping the Services

### Stop FastAPI Server:
Press `CTRL+C` in the terminal where it's running.

### Stop Qdrant:

```bash
docker-compose down
```

To stop and remove all data:
```bash
docker-compose down -v
```

---

## 🔧 Troubleshooting

### Issue: "GEMINI_API_KEY not found"
**Solution:** Check `.env` file has the key set correctly.

### Issue: "Connection refused" to Qdrant
**Solution:** 
1. Verify Docker is running: `docker ps`
2. Restart Qdrant: `docker-compose restart`

### Issue: "Rate limit exceeded"
**Solution:** The Gemini client has automatic retry with exponential backoff. Wait a few seconds and try again.

### Issue: Import errors
**Solution:** 
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`

---

## 🎯 Next Steps

- Test the semantic search capabilities
- Add more memory cards with different tags
- Explore the interactive API docs at `/docs`
- Monitor Qdrant collections at http://localhost:6333/dashboard

**Enjoy using Trinity Context Core! 🚀**
