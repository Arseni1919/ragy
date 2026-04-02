# Ollama Embedding Setup

## Prerequisites

### 1. Install Ollama
Download and install Ollama from: https://ollama.ai/download

### 2. Start Ollama
Ollama typically runs automatically after installation. If not:
```bash
ollama serve
```

### 3. Pull the Embedding Model
```bash
ollama pull nomic-embed-text
```

## Configuration

The model name is configured in the `.env` file:
```
OLLAMA_EMB_MODEL="nomic-embed-text"
```

You can change this to use different Ollama embedding models.

## Why nomic-embed-text?

- **Local**: Runs entirely on your machine, no API keys needed
- **Efficient**: 137M parameters, fast inference
- **Quality**: Good embedding quality for general-purpose use
- **Dimension**: Produces 768-dimensional embeddings
- **Context Window**: 8192 tokens (much larger than Hugging Face models)
- **Compatible**: Works seamlessly with ChromaDB vector storage

## Testing

After setup, test the connection:
```bash
uv run python conn_emb_ollama/test_client.py
```

You should see:
- Embedding dimensions (768)
- Sample embedding values
- Success confirmation

## Troubleshooting

**Error: "Failed to get embedding"**
- Ensure Ollama is running: `ollama list` should work
- Ensure model is pulled: `ollama pull nomic-embed-text`
- Check Ollama is on default port: http://localhost:11434

**Slow first run**
- First embedding generation may be slower as model loads into memory
- Subsequent calls will be much faster
