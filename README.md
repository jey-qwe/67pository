# Trinity Context Core

A FastAPI-based semantic memory system using **Qdrant** vector database and **Google Gemini** embeddings for intelligent context management.

## 🌟 Features

- ✅ **Semantic Memory Storage** - Store and retrieve context cards using vector embeddings
- ✅ **Google Gemini Integration** - Automatic embedding generation with text-embedding-004
- ✅ **Qdrant Vector Database** - High-performance similarity search with cosine distance
- ✅ **RESTful API** - Full CRUD operations via FastAPI
- ✅ **Tag-based Filtering** - Organize memories with custom tags
- ✅ **Importance Weighting** - Prioritize memories by importance (1-10)
- ✅ **Docker Support** - Easy deployment with docker-compose

## 📁 Project Structure

```
Trinity Context Core/
├── src/
│   ├── core/              # Global settings and configs
│   │   ├── config.py      # Centralized configuration
│   │   └── gemini_client.py  # Gemini API integration
│   ├── memory/            # Memory management logic
│   │   ├── schemas.py     # Pydantic data models
│   │   └── service.py     # MemoryService (Qdrant integration)
│   ├── api/               # FastAPI endpoints
│   │   └── routes.py      # API routes
│   └── main.py            # Application entry point
├── data/                  # Local storage
├── qdrant_storage/        # Qdrant persistent data (created by Docker)
├── docker-compose.yml     # Qdrant container configuration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (DO NOT COMMIT)
├── .env.example           # Environment template
└── STARTUP_GUIDE.md       # Detailed startup instructions
```

## 🚀 Quick Start

### 1. Start Qdrant Database

```bash
docker-compose up -d
```

### 2. Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Configure Environment

Ensure `.env` has your Gemini API key:
```
GEMINI_API_KEY=your_key_here
```

### 4. Run the Server

```bash
python src/main.py
# OR
uvicorn src.main:app --reload
```

Server runs at: **http://localhost:8000**

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/ping

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/memory/add` | Add new memory card |
| POST | `/api/v1/memory/search` | Semantic search |
| GET | `/api/v1/memory/card/{id}` | Get card by ID |
| GET | `/api/v1/memory/tags/{tag}` | Filter by tag |
| GET | `/api/v1/memory/all` | Get all cards |
| DELETE | `/api/v1/memory/card/{id}` | Delete card |

## 🧪 Example Usage

### Add a Memory Card

```bash
curl -X POST "http://localhost:8000/api/v1/memory/add" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "User prefers Python for backend development",
    "tags": ["python", "preference"],
    "source": "user",
    "importance": 8
  }'
```

### Search Memories

```bash
curl -X POST "http://localhost:8000/api/v1/memory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What languages does user prefer?",
    "limit": 5
  }'
```

## 🛠️ Technology Stack

- **Backend**: FastAPI, Uvicorn
- **Vector DB**: Qdrant (Docker)
- **Embeddings**: Google Gemini (text-embedding-004, 768 dimensions)
- **Data Validation**: Pydantic
- **Environment**: Python-dotenv

## 📖 Detailed Documentation

See [STARTUP_GUIDE.md](STARTUP_GUIDE.md) for comprehensive setup instructions and troubleshooting.

## 🔒 Security Notes

- **Never commit `.env`** - Contains API keys
- Qdrant runs locally without authentication by default
- For production, configure Qdrant API key in `.env`

## 🎯 Next Steps

- Integrate with frontend applications
- Add user authentication
- Implement memory consolidation strategies
- Add support for multiple memory collections
- Deploy to production environment

---

**Trinity Context Core** - Semantic memory for intelligent systems 🧠✨
