# RagyApp - Project Instructions

## Development Guidelines

### Running Python Scripts
- **ALWAYS use `uv run` to execute Python scripts**, not plain `python`
- **Use module syntax from project root**: `uv run python -m module.script`
- Examples:
  - `uv run python -m conn_db.test_client` ✓ (not `uv run python conn_db/test_client.py` ✗)
  - `uv run python -m conn_llm.test_with_tools` ✓
- This ensures proper package imports and virtual environment usage
- All modules have `__init__.py` files for proper package structure
- Always run from the project root directory

### Running the API Server
- **Development mode**: `uv run uvicorn ragy_api.main:app --reload --host 0.0.0.0 --port 8000`
- **Production mode**: `uv run uvicorn ragy_api.main:app --workers 4 --host 0.0.0.0 --port 8000`
- **Access documentation**:
  - Interactive Swagger UI: http://localhost:8000/docs
  - Alternative ReDoc: http://localhost:8000/redoc
  - OpenAPI JSON: http://localhost:8000/openapi.json

### Environment Variables
- **All critical configuration variables must be defined in the `.env` file**
- This includes:
  - API keys (e.g., `TAVILY_API_KEY`)
  - Model names (e.g., `HF_EMB_MODEL`, `OLLAMA_EMB_MODEL`)
  - File paths (e.g., `DB_PATH`)
  - Any configurable parameter that might change between environments
- Load using `python-dotenv` with fallback defaults
- Example: `MODEL = os.getenv("HF_EMB_MODEL", "default-model")`

### Code Conventions
- Use best practices in writing code
- Suggest better options if there is a strong recommendation for best practice pattern
- No comments in code unless really necessary - code should be self-explanatory
- Be as short as possible, use minimal code, be concise
- Avoid unnecessary abstractions and wrapper functions
- Simple and direct is better than complex and abstracted
- Add print statements when testing or checking something to show progress and results
- Use tqdm or similar tools for long iterative processes to show progress bars

## Project Structure

- `conn_db/` - Vector database connection (ChromaDB)
- `conn_emb_hugging_face/` - Embedding model connection (Hugging Face sentence-transformers)
- `conn_emb_ollama/` - Alternative embedding (Ollama, requires installation)
- `conn_tavily/` - Tavily search API client
- `conn_bright_data/` - Bright Data API client
- `conn_llm/` - LLM clients (Claude/Ollama)
- `ragy_api/` - FastAPI application (unified services and routers)
  - `services/` - Business logic (search, extract, index, database)
  - `routers/` - REST API endpoints
  - `main.py` - FastAPI application entry point
  - `config.py` - Environment configuration
  - `scheduler.py` - APScheduler for daily updates
- `ragy_cli/` - CLI interface (to be reimplemented as API client)

## Development Todo List

- [x] Create database connection (ChromaDB)
- [x] Create embeddings connection (Hugging Face sentence-transformers)
- [x] Create connection to Tavily (search API)
- [ ] Create connection to Bright Data
- [x] Build the ragy creator (365-day index builder with parallel processing)
- [x] Build the ragy extractor (vector similarity retrieval)
- [x] Connect LLM clients (Claude/Ollama)
- [x] Create FastAPI application with 13 endpoints
  - Web search, data extraction (SSE), index creation (SSE)
  - Database management, system health
  - APScheduler for daily automatic updates
- [ ] Reimplement CLI to use API endpoints
- [x] Create initial CLI interface
