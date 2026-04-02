# Hugging Face Embedding Setup

## No System Installation Required!

Unlike Ollama, sentence-transformers is a pure Python package that requires **no system-level permissions or installations**.

## How It Works

1. **Automatic Model Download**: On first use, the model (`all-MiniLM-L6-v2`, ~80MB) downloads automatically
2. **User Cache**: Stored in `~/.cache/huggingface/` (your home directory, no permissions needed)
3. **Offline Ready**: After initial download, works completely offline
4. **No Background Services**: No daemons or services to run

## Usage

Just run the test - everything happens automatically:
```bash
uv run python conn_emb/test_client.py
```

First run:
- Downloads model (~80MB, takes 10-30 seconds depending on connection)
- Generates embeddings
- Shows similarity search example

Subsequent runs:
- Uses cached model (instant startup)
- No downloads needed

## Why all-MiniLM-L6-v2?

- **Small**: Only ~80MB (vs 400MB+ for larger models)
- **Fast**: Quick inference, even on CPU
- **Quality**: Good embedding quality for general use
- **Dimensions**: 384-dimensional embeddings (efficient for ChromaDB)
- **Popular**: Widely used, well-tested model

## Configuration

The model name is configured in the `.env` file:
```
EMB_MODEL="all-MiniLM-L6-v2"
```

You can change this to use different models (e.g., `all-mpnet-base-v2` for longer context).

## Technical Details

- **Model**: `all-MiniLM-L6-v2` (configurable via `EMB_MODEL` in `.env`)
- **Embedding Size**: 384 dimensions
- **Context Window**: 256 tokens (~190-200 words, ~1000-1200 characters)
  - ⚠️ **Important**: Text longer than 256 tokens will be automatically truncated
  - For longer context, consider using `all-mpnet-base-v2` (384 tokens, 768 dimensions)
- **Output Format**: `list[float]` (compatible with ChromaDB)
- **Framework**: PyTorch (installed automatically as dependency)
- **License**: Apache 2.0

## Troubleshooting

**First run is slow**: Normal! Model is downloading. Subsequent runs are instant.

**Out of disk space**: Model needs ~200MB total with dependencies. Check `~/.cache/huggingface/`

**Import errors**: Run `uv sync` to install dependencies
