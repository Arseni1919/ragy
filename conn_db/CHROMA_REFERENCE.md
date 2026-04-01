# ChromaDB Reference Guide

## Overview

ChromaDB is an open-source **embedded vector database** that:
- Runs in your Python process (no separate server needed)
- Stores vectors + metadata + original text
- Provides built-in similarity search using cosine distance
- Offers persistent storage on disk

## Full CRUD Operations

### CREATE
```python
collection.add(
    documents=["text1", "text2"],
    embeddings=[[0.1, 0.2], [0.3, 0.4]],
    metadatas=[{"key": "value"}, {"key": "value"}],
    ids=["id1", "id2"]
)
```

### READ

**Get all documents:**
```python
all_docs = collection.get()
```

**Get by IDs:**
```python
docs = collection.get(ids=["id1", "id2"])
```

**Get with filter:**
```python
docs = collection.get(where={"topic": "animals"})
```

**Vector similarity search:**
```python
results = collection.query(
    query_embeddings=[[0.1, 0.2, 0.3]],
    n_results=5
)
```

**Count documents:**
```python
count = collection.count()
```

### UPDATE
```python
# Update everything
collection.update(
    ids=["id1"],
    documents=["new text"],
    embeddings=[[0.5, 0.6]],
    metadatas=[{"updated": True}]
)

# Update only metadata
collection.update(
    ids=["id1"],
    metadatas=[{"score": 10}]
)
```

### DELETE

**Delete by ID:**
```python
collection.delete(ids=["id1", "id2"])
```

**Delete by filter:**
```python
collection.delete(where={"source": "news"})
```

## SQL-like Filtering

| SQL Operator | ChromaDB Syntax | Example |
|--------------|-----------------|---------|
| `WHERE x = y` | `{"x": "y"}` | `{"topic": "animals"}` |
| `WHERE x != y` | `{"x": {"$ne": y}}` | `{"topic": {"$ne": "animals"}}` |
| `WHERE x > y` | `{"x": {"$gt": y}}` | `{"score": {"$gt": 8}}` |
| `WHERE x >= y` | `{"x": {"$gte": y}}` | `{"score": {"$gte": 10}}` |
| `WHERE x < y` | `{"x": {"$lt": y}}` | `{"score": {"$lt": 5}}` |
| `WHERE x <= y` | `{"x": {"$lte": y}}` | `{"score": {"$lte": 8}}` |
| `WHERE x IN (...)` | `{"x": {"$in": [...]}}` | `{"source": {"$in": ["blog", "article"]}}` |
| `WHERE x NOT IN (...)` | `{"x": {"$nin": [...]}}` | `{"topic": {"$nin": ["animals"]}}` |
| `WHERE a AND b` | `{"$and": [{a}, {b}]}` | `{"$and": [{"topic": "animals"}, {"score": {"$gte": 10}}]}` |
| `WHERE a OR b` | `{"$or": [{a}, {b}]}` | `{"$or": [{"topic": "animals"}, {"score": {"$gt": 9}}]}` |

## Filter Operators Reference

- **`$eq`** - equals (default, can be omitted)
- **`$ne`** - not equals
- **`$gt`** - greater than
- **`$gte`** - greater than or equal
- **`$lt`** - less than
- **`$lte`** - less than or equal
- **`$in`** - value in list
- **`$nin`** - value not in list
- **`$and`** - logical AND
- **`$or`** - logical OR

## Vector Similarity Search

### Basic query
```python
results = collection.query(
    query_embeddings=[[0.1, 0.2, 0.3]],
    n_results=5  # Top 5 most similar
)
```

### Query with metadata filter
```python
# Find similar documents that match metadata criteria
results = collection.query(
    query_embeddings=[[0.1, 0.2, 0.3]],
    n_results=5,
    where={"topic": "animals"}
)
```

### Query with date range
```python
# SQL: SELECT * FROM ... WHERE date BETWEEN ... ORDER BY similarity
results = collection.query(
    query_embeddings=[[0.1, 0.2, 0.3]],
    n_results=10,
    where={
        "$and": [
            {"date": {"$gte": "2025-01-01"}},
            {"date": {"$lte": "2025-01-31"}}
        ]
    }
)
```

## Vector Dimensions

- **All vectors in a collection must have the same dimensionality**
- Vectors are always **1D arrays**: `[num1, num2, ..., numN]`
- The "dimension" refers to the array length, not structure

### Common Embedding Model Dimensions
- `sentence-transformers/all-MiniLM-L6-v2`: **384D**
- `text-embedding-ada-002` (OpenAI): **1536D**
- `text-embedding-3-small` (OpenAI): **512D or 1536D**

### Example
```python
# 3D vector (for demo)
[0.1, 0.2, 0.3]

# 384D vector (realistic)
[0.1, 0.2, 0.3, ..., 0.384]  # 384 numbers total
```

## RagyApp Use Cases

### Store daily search results
```python
collection.add(
    documents=["search result text for 2025-04-01"],
    embeddings=[[0.1, 0.2, ..., 0.384]],  # From embedding model
    metadatas=[{
        "date": "2025-04-01",
        "query": "What is the most popular film today?",
        "source": "bright_data"
    }],
    ids=["day_2025-04-01"]
)
```

### Find relevant days for a question
```python
# User asks: "What were the popular films in January?"
results = collection.query(
    query_embeddings=question_embedding,  # Embed user's question
    n_results=10,
    where={
        "$and": [
            {"date": {"$gte": "2025-01-01"}},
            {"date": {"$lte": "2025-01-31"}}
        ]
    }
)
```

### Find similar days across the year
```python
# Find all days similar to a specific event
results = collection.query(
    query_embeddings=event_embedding,
    n_results=30  # Top 30 most similar days
)
```

## Collection Management

### Create or get collection
```python
collection = client.get_or_create_collection(name="my_collection")
```

### Create new collection (fails if exists)
```python
collection = client.create_collection(name="my_collection")
```

### Delete collection
```python
client.delete_collection(name="my_collection")
```

### List all collections
```python
collections = client.list_collections()
```

## Client Types

### In-memory (temporary, for testing)
```python
client = chromadb.Client()
```

### Persistent (saves to disk)
```python
client = chromadb.PersistentClient(path="./chroma_data")
```

## Best Practices for RagyApp

1. **Use meaningful IDs**: `day_2025-04-01` instead of `doc1`
2. **Store comprehensive metadata**: date, query, source, timestamp
3. **Keep original text**: Store full search results in `documents`
4. **Use date filtering**: Narrow searches to relevant time periods
5. **Batch operations**: Add multiple documents at once for efficiency
6. **Consistent dimensions**: All embeddings from same model = same dimensions
