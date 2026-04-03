# RagyApp

A FastAPI-based RAG (Retrieval Augmented Generation) application that builds a 365-day vector database from daily search queries and enables semantic retrieval of temporal data.

## Features

- **13 REST API Endpoints** for web search, data extraction, and index management
- **Server-Sent Events (SSE)** streaming for long-running operations
- **Automatic Daily Updates** via APScheduler
- **Vector Similarity Search** using ChromaDB and sentence-transformers
- **Parallel Processing** for fast index creation (configurable concurrency)
- **Interactive API Documentation** with Swagger UI

## Quick Start

### 1. Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd RagyApp
uv sync
```

### 3. Configuration

Create a `.env` file in the project root with your API keys:

```bash
# Required
TAVILY_API_KEY="your-tavily-api-key"
GEMINI_API_KEY="your-gemini-api-key"

# Optional (defaults shown)
HF_EMB_MODEL="all-MiniLM-L6-v2"
DB_PATH="./ragy_db"
RAGY_MAX_CONCURRENT=10
API_HOST="0.0.0.0"
API_PORT=8000
SCHEDULER_ENABLED=true
SCHEDULER_HOUR=2
SCHEDULER_TIMEZONE="UTC"
```

### 4. Run the API

**Development mode** (with auto-reload):
```bash
uv run uvicorn ragy_api.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode** (with multiple workers):
```bash
uv run uvicorn ragy_api.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### 5. Access Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/system/health

## API Endpoints

### Search
- `POST /api/v1/search/web` - Execute Tavily web search

### Data Extraction
- `GET /api/v1/extract/collections` - List all collections
- `POST /api/v1/extract/data` - Extract relevant days (SSE streaming)

### Index Creation
- `POST /api/v1/index/create` - Create 365-day index (SSE streaming)
- `GET /api/v1/index/status/{name}` - Get collection status

### Database Management
- `GET /api/v1/database/content` - Show all collections
- `GET /api/v1/database/collection/{name}` - Get collection details
- `DELETE /api/v1/database/collection/{name}` - Delete collection

### System
- `GET /api/v1/system/health` - Health check
- `GET /api/v1/system/embedding/info` - Embedding model info
- `POST /api/v1/system/embedding/encode` - Encode text to vector
- `GET /api/v1/system/scheduler/jobs` - List scheduled jobs
- `POST /api/v1/system/scheduler/trigger` - Trigger manual update

## Usage Examples

### Create an Index

```bash
curl -N -X POST http://localhost:8000/api/v1/index/create \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence news",
    "collection_name": "ai_news",
    "save_full_data": true,
    "num_days": 365
  }'
```

### Search for Relevant Data

```bash
curl -X POST http://localhost:8000/api/v1/extract/data \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning breakthroughs",
    "collection_name": "ai_news",
    "top_k": 5
  }'
```

### Web Search

```bash
curl -X POST http://localhost:8000/api/v1/search/web \
  -H "Content-Type: application/json" \
  -d '{"query": "Python programming"}'
```

### Check Health

```bash
curl http://localhost:8000/api/v1/system/health
```

## Python Client Example

```python
import requests

# Create index with streaming progress
with requests.post(
    "http://localhost:8000/api/v1/index/create",
    json={
        "query": "climate change",
        "collection_name": "climate_db",
        "save_full_data": True,
        "num_days": 30
    },
    stream=True
) as response:
    for line in response.iter_lines():
        if line:
            print(line.decode())

# Extract relevant data
response = requests.post(
    "http://localhost:8000/api/v1/extract/data",
    json={
        "query": "renewable energy solutions",
        "collection_name": "climate_db",
        "top_k": 10
    }
)
print(response.json())
```

## Project Structure

```
ragy_api/
├── main.py                # FastAPI application entry point
├── config.py              # Environment configuration
├── models.py              # Pydantic request/response models
├── dependencies.py        # Singleton clients
├── scheduler.py           # APScheduler for daily updates
├── services/              # Business logic
│   ├── search_service.py
│   ├── index_service.py
│   ├── extract_service.py
│   └── database_service.py
└── routers/               # API endpoints
    ├── search.py
    ├── extract.py
    ├── index.py
    ├── database.py
    └── system.py
```

## Automatic Updates

The API includes an APScheduler that runs daily at 2 AM UTC (configurable) to automatically update all collections with yesterday's data. You can also trigger manual updates:

```bash
curl -X POST http://localhost:8000/api/v1/system/scheduler/trigger \
  -H "Content-Type: application/json" \
  -d '{"collection_name": "your_collection"}'
```

## Development

See [CLAUDE.md](CLAUDE.md) for development guidelines and conventions.
