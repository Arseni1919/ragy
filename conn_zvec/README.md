# zvec Vector Database Wrapper

This module provides a ChromaDB-compatible wrapper for zvec, allowing seamless switching between vector database backends.

## Overview

The wrapper implements the same interface as ChromaDB's `PersistentClient`, enabling drop-in replacement without modifying application code.

## Architecture

### ZvecCollection Class

Wraps zvec's Collection object to match ChromaDB's interface:

**Methods:**
- `add(ids, documents, embeddings, metadatas)` - Insert documents
- `get(ids=None, limit=None, include=[], where=None)` - Retrieve documents
- `query(query_embeddings, n_results, include=[])` - Vector similarity search
- `count()` - Get document count

**Key Implementation Details:**
- Documents are stored in `fields['_content']`
- Metadata is stored in zvec's native `fields` dictionary
- Query responses are converted to ChromaDB's nested list format:
  ```python
  {
      'ids': [['id1', 'id2', ...]],       # Double-nested
      'documents': [['doc1', 'doc2', ...]],
      'metadatas': [[{}, {}, ...]],
      'distances': [[0.5, 0.6, ...]]
  }
  ```
- zvec scores (higher = more similar) are converted to ChromaDB distances (lower = more similar)

### ZvecClient Class

Manages collections and matches ChromaDB's client interface:

**Methods:**
- `get_or_create_collection(name)` - Get existing or create new collection
- `get_collection(name)` - Get existing collection (raises ValueError if not found)
- `list_collections()` - List all collections
- `delete_collection(name)` - Delete a collection

## Usage

```python
from conn_zvec.client import client

# Create or get collection
collection = client.get_or_create_collection("my_collection")

# Add documents
collection.add(
    ids=["doc1", "doc2"],
    documents=["First doc", "Second doc"],
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],  # 768-dim vectors
    metadatas=[{"date": "2024-01-01"}, {"date": "2024-01-02"}]
)

# Query similar documents
results = collection.query(
    query_embeddings=[[0.15, 0.25, ...]],
    n_results=10,
    include=["documents", "metadatas", "distances"]
)

# Access results (nested lists like ChromaDB)
for doc, meta, dist in zip(
    results['documents'][0],
    results['metadatas'][0],
    results['distances'][0]
):
    print(f"Doc: {doc}, Score: {1/(1+dist)}")
```

## Configuration

Set database path via environment variable:
```bash
export DB_PATH="./ragy_db"
```

Embedding dimension is fixed at 768 (google/embeddinggemma-300m).

## Testing

Run comprehensive tests:
```bash
uv run python -m conn_zvec.test_client
```

Tests verify:
- ✅ Collection creation
- ✅ Document insertion with metadata
- ✅ Document counting
- ✅ Document retrieval (all, by ID, with limit)
- ✅ Vector similarity search
- ✅ **Critical: Nested list response format**
- ✅ Metadata round-trip
- ✅ Collection listing
- ✅ Collection deletion
- ✅ Error handling

## Limitations

- `where` filtering not yet implemented
- zvec schema requires fixed embedding dimensions (768)
- `count()` may be approximate depending on zvec's stats implementation
- `get()` without IDs uses workaround query with random vector

## Migration from ChromaDB

This wrapper enables seamless migration:

1. Install zvec: `uv sync`
2. Set `DB_PROVIDER="zvec"` in `.env`
3. All existing code works unchanged

Data can be migrated using the `migrate_data.py` script in the project root.
