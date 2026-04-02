# RagyApp - Project Instructions

## Development Guidelines

### Running Python Scripts
- **ALWAYS use `uv run` to execute Python scripts**, not plain `python`
- Example: `uv run python script.py` or `uv run python -m module`
- This ensures the correct virtual environment and dependencies are used

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
- `ragy_creator/` - Indexing orchestrator (365-day construction)
- `ragy_extractor/` - RAG retrieval logic (finding relevant days)
- `conn_llm/` - LLM clients (Claude/Ollama)
- `ragy_ui/` - CLI interface

## Development Todo List

- [x] Create database connection (ChromaDB)
- [x] Create embeddings connection (Hugging Face sentence-transformers)
- [x] Create connection to Tavily (search API)
- [ ] Create connection to Bright Data
- [x] Build the ragy creator (365-day index builder with parallel processing)
- [x] Build the ragy extractor (vector similarity retrieval)
- [ ] Connect LLM clients
- [ ] Create UI interface
