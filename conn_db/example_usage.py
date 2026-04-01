"""
Comprehensive ChromaDB example - demonstrates all CRUD operations and filtering.

This example shows:
1. CREATE - Adding documents
2. READ - Retrieving and querying documents
3. UPDATE - Modifying existing documents
4. DELETE - Removing documents
5. Advanced filtering (SQL-like operations)
6. Vector dimensions
"""

import chromadb


def print_section(title):
    """Helper to print section headers"""
    print(f"\n{'='*60}")
    print(f"=== {title}")
    print('='*60)


def run_example():
    # Setup: Create client and collection
    client = chromadb.PersistentClient(path="./chroma_data")

    # Delete collection if exists (for clean demo)
    try:
        client.delete_collection(name="example_collection")
    except:
        pass

    collection = client.create_collection(name="example_collection")

    # ========================================
    # CREATE - Adding documents
    # ========================================
    print_section("CREATE - Adding Documents")

    collection.add(
        documents=[
            "The cat sat on the mat",
            "The dog played in the park",
            "Python is a programming language",
            "JavaScript powers the web",
            "The elephant is the largest land animal"
        ],
        embeddings=[
            [0.1, 0.2, 0.3],  # Similar to doc2
            [0.2, 0.1, 0.3],  # Similar to doc1
            [0.9, 0.8, 0.7],  # Similar to doc4
            [0.85, 0.75, 0.65],  # Similar to doc3
            [0.15, 0.25, 0.35]  # Similar to doc1 & doc2
        ],
        metadatas=[
            {"date": "2025-01-01", "topic": "animals", "score": 10, "source": "blog"},
            {"date": "2025-01-02", "topic": "animals", "score": 8, "source": "news"},
            {"date": "2025-01-03", "topic": "technology", "score": 9, "source": "blog"},
            {"date": "2025-01-04", "topic": "technology", "score": 7, "source": "news"},
            {"date": "2025-01-05", "topic": "animals", "score": 10, "source": "article"}
        ],
        ids=["doc1", "doc2", "doc3", "doc4", "doc5"]
    )
    print(f"✓ Added 5 documents")
    print(f"✓ Collection count: {collection.count()}")

    # ========================================
    # READ - Retrieving documents
    # ========================================
    print_section("READ - Get All Documents")

    all_docs = collection.get()
    print(f"Total documents: {len(all_docs['ids'])}")
    print(f"IDs: {all_docs['ids']}")

    print_section("READ - Get by IDs")
    specific_docs = collection.get(ids=["doc1", "doc3"])
    print(f"Documents: {specific_docs['documents']}")
    print(f"Metadata: {specific_docs['metadatas']}")

    print_section("READ - Get with Metadata Filter")
    # SQL equivalent: SELECT * FROM collection WHERE topic = 'animals'
    animals_only = collection.get(
        where={"topic": "animals"}
    )
    print(f"Animals documents: {animals_only['documents']}")
    print(f"Count: {len(animals_only['ids'])}")

    # ========================================
    # QUERY - Similarity Search
    # ========================================
    print_section("QUERY - Vector Similarity Search")

    results = collection.query(
        query_embeddings=[[0.15, 0.15, 0.3]],
        n_results=3
    )
    print(f"Top 3 similar documents:")
    for i, (doc, dist, meta) in enumerate(zip(
        results['documents'][0],
        results['distances'][0],
        results['metadatas'][0]
    )):
        print(f"  {i+1}. {doc[:30]}... (distance: {dist:.4f}, topic: {meta['topic']})")

    # ========================================
    # FILTERING - SQL-like operations
    # ========================================
    print_section("FILTER - Equality (WHERE topic = 'technology')")
    tech_docs = collection.get(
        where={"topic": "technology"}
    )
    print(f"Found {len(tech_docs['ids'])} tech documents")

    print_section("FILTER - Greater Than (WHERE score > 8)")
    # SQL: SELECT * FROM collection WHERE score > 8
    high_score = collection.get(
        where={"score": {"$gt": 8}}
    )
    print(f"Documents with score > 8:")
    for doc, meta in zip(high_score['documents'], high_score['metadatas']):
        print(f"  - {doc[:40]}... (score: {meta['score']})")

    print_section("FILTER - Less Than or Equal (WHERE score <= 8)")
    # SQL: SELECT * FROM collection WHERE score <= 8
    low_score = collection.get(
        where={"score": {"$lte": 8}}
    )
    print(f"Found {len(low_score['ids'])} documents with score <= 8")

    print_section("FILTER - IN operator (WHERE source IN ['blog', 'article'])")
    # SQL: SELECT * FROM collection WHERE source IN ('blog', 'article')
    blog_articles = collection.get(
        where={"source": {"$in": ["blog", "article"]}}
    )
    print(f"Documents from blog or article:")
    for doc, meta in zip(blog_articles['documents'], blog_articles['metadatas']):
        print(f"  - {doc[:40]}... (source: {meta['source']})")

    print_section("FILTER - NOT IN operator (WHERE topic NOT IN ['animals'])")
    # SQL: SELECT * FROM collection WHERE topic NOT IN ('animals')
    not_animals = collection.get(
        where={"topic": {"$nin": ["animals"]}}
    )
    print(f"Non-animal documents: {len(not_animals['ids'])}")

    print_section("FILTER - AND logic (WHERE topic='animals' AND score>=10)")
    # SQL: SELECT * FROM collection WHERE topic='animals' AND score >= 10
    animals_high_score = collection.get(
        where={
            "$and": [
                {"topic": "animals"},
                {"score": {"$gte": 10}}
            ]
        }
    )
    print(f"Animals with score >= 10:")
    for doc, meta in zip(animals_high_score['documents'], animals_high_score['metadatas']):
        print(f"  - {doc[:40]}... (score: {meta['score']})")

    print_section("FILTER - OR logic (WHERE topic='animals' OR score>9)")
    # SQL: SELECT * FROM collection WHERE topic='animals' OR score > 9
    animals_or_high = collection.get(
        where={
            "$or": [
                {"topic": "animals"},
                {"score": {"$gt": 9}}
            ]
        }
    )
    print(f"Animals OR high score documents: {len(animals_or_high['ids'])}")

    print_section("FILTER - Vector Search + Metadata Filter")
    # Find similar documents that are ONLY about animals
    # SQL equivalent: Semantic search + WHERE topic='animals'
    similar_animals = collection.query(
        query_embeddings=[[0.15, 0.15, 0.3]],
        n_results=5,
        where={"topic": "animals"}
    )
    print(f"Similar animal documents:")
    for doc, dist in zip(similar_animals['documents'][0], similar_animals['distances'][0]):
        print(f"  - {doc[:40]}... (distance: {dist:.4f})")

    # ========================================
    # UPDATE - Modifying documents
    # ========================================
    print_section("UPDATE - Modify Document")

    # Update document text, embedding, and metadata
    collection.update(
        ids=["doc1"],
        documents=["The cat is sleeping peacefully"],
        embeddings=[[0.12, 0.22, 0.32]],
        metadatas=[{"date": "2025-01-01", "topic": "animals", "score": 11, "source": "blog", "updated": True}]
    )

    updated = collection.get(ids=["doc1"])
    print(f"Updated document: {updated['documents'][0]}")
    print(f"Updated metadata: {updated['metadatas'][0]}")

    print_section("UPDATE - Modify Only Metadata")
    # Update only metadata, keep document and embedding the same
    collection.update(
        ids=["doc2"],
        metadatas=[{"date": "2025-01-02", "topic": "animals", "score": 12, "source": "news"}]
    )
    print(f"Updated doc2 score from 8 to 12")

    # ========================================
    # DELETE - Removing documents
    # ========================================
    print_section("DELETE - Remove by ID")

    print(f"Count before delete: {collection.count()}")
    collection.delete(ids=["doc5"])
    print(f"Count after deleting doc5: {collection.count()}")

    print_section("DELETE - Remove by Filter")
    # SQL: DELETE FROM collection WHERE source='news'
    collection.delete(
        where={"source": "news"}
    )
    print(f"Count after deleting all 'news' sources: {collection.count()}")

    remaining = collection.get()
    print(f"Remaining documents: {remaining['ids']}")

    # ========================================
    # Additional Operations
    # ========================================
    print_section("Vector Dimensions Info")
    print(f"- All vectors must have same dimensionality")
    print(f"- This example uses 3D vectors: [x, y, z]")
    print(f"- Real embedding models use 384-1536 dimensions")
    print(f"- Vectors are always 1D arrays, just longer!")

    print_section("Summary of Operations")
    print("""
    CRUD Operations:
    ✓ CREATE: collection.add()
    ✓ READ:   collection.get() / collection.query()
    ✓ UPDATE: collection.update()
    ✓ DELETE: collection.delete()

    Filter Operators (SQL-like):
    ✓ $eq  - equals (default)
    ✓ $ne  - not equals
    ✓ $gt  - greater than
    ✓ $gte - greater than or equal
    ✓ $lt  - less than
    ✓ $lte - less than or equal
    ✓ $in  - in list
    ✓ $nin - not in list
    ✓ $and - logical AND
    ✓ $or  - logical OR
    """)

if __name__ == "__main__":
    run_example()
