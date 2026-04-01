# RagyApp - Project Instructions

## Development Guidelines

### Running Python Scripts
- **ALWAYS use `uv run` to execute Python scripts**, not plain `python`
- Example: `uv run python script.py` or `uv run python -m module`
- This ensures the correct virtual environment and dependencies are used

## Project Structure

- `conn_db/` - Vector database connection (ChromaDB)
- `conn_emb/` - Embedding model connection
- `conn_bright_data/` - Bright Data API client
- `ragy_creator/` - Indexing orchestrator (365-day construction)
- `ragy_extractor/` - RAG retrieval logic (finding relevant days)
- `conn_llm/` - LLM clients (Claude/Ollama)
- `ragy_ui/` - CLI interface

## Development Todo List

- [ ] Create database connection (ChromaDB)
- [ ] Create embeddings connection
- [ ] Create connection to Bright Data
- [ ] Build the ragy creator
- [ ] Build the ragy extractor
- [ ] Connect LLM clients
- [ ] Create UI interface
