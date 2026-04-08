import os
import sys

# Set test database path
os.environ['DB_PATH'] = './test_zvec_db'

from conn_zvec.client import client
import numpy as np


def test_create_collection():
    """Test get_or_create_collection"""
    print("Test 1: Create collection...")
    col = client.get_or_create_collection("test_collection")
    assert col.name == "test_collection", f"Expected 'test_collection', got {col.name}"
    print("✓ Create collection")


def test_add_documents():
    """Test adding documents with metadata"""
    print("\nTest 2: Add documents...")
    col = client.get_or_create_collection("test_add")

    col.add(
        ids=["doc1", "doc2", "doc3"],
        documents=["First document", "Second document", "Third document"],
        embeddings=[np.random.rand(768).tolist() for _ in range(3)],
        metadatas=[
            {"date": "2024-01-01", "source": "test"},
            {"date": "2024-01-02", "source": "test"},
            {"date": "2024-01-03", "source": "test"}
        ]
    )
    print("✓ Add documents")


def test_count():
    """Test document count"""
    print("\nTest 3: Count documents...")
    col = client.get_collection("test_add")
    count = col.count()
    assert count == 3, f"Expected 3, got {count}"
    print(f"✓ Count: {count}")


def test_get_documents():
    """Test retrieving documents"""
    print("\nTest 4: Get documents...")
    col = client.get_collection("test_add")

    # Get all
    print("  4a: Get all documents...")
    results = col.get(include=["documents", "metadatas"])
    assert 'documents' in results, "Missing 'documents' in results"
    assert 'metadatas' in results, "Missing 'metadatas' in results"
    assert len(results['documents']) == 3, f"Expected 3 documents, got {len(results['documents'])}"
    print(f"  ✓ Get all documents: {len(results['documents'])} documents")

    # Get with limit
    print("  4b: Get with limit...")
    results = col.get(limit=2, include=["documents"])
    assert len(results['documents']) == 2, f"Expected 2 documents, got {len(results['documents'])}"
    print("  ✓ Get with limit")

    # Get by IDs
    print("  4c: Get by ID...")
    results = col.get(ids=["doc1"], include=["documents", "metadatas"])
    assert len(results['ids']) == 1, f"Expected 1 ID, got {len(results['ids'])}"
    assert results['ids'][0] == "doc1", f"Expected 'doc1', got {results['ids'][0]}"
    print("  ✓ Get by ID")


def test_query_vector_search():
    """Test vector similarity search - CRITICAL TEST"""
    print("\nTest 5: Query vector search (CRITICAL)...")
    col = client.get_collection("test_add")

    query_embedding = np.random.rand(768).tolist()

    results = col.query(
        query_embeddings=[query_embedding],
        n_results=2,
        include=["documents", "metadatas", "distances"]
    )

    # CRITICAL: Verify response format
    print("  5a: Verify response has all keys...")
    assert 'ids' in results, "Missing 'ids' in results"
    assert 'documents' in results, "Missing 'documents' in results"
    assert 'metadatas' in results, "Missing 'metadatas' in results"
    assert 'distances' in results, "Missing 'distances' in results"
    print("  ✓ All keys present")

    # CRITICAL: Verify nested list format
    print("  5b: Verify nested list format...")
    assert isinstance(results['ids'], list), f"ids should be list, got {type(results['ids'])}"
    assert isinstance(results['ids'][0], list), f"ids[0] should be list, got {type(results['ids'][0])}"
    assert len(results['ids']) == 1, f"Expected 1 query result list, got {len(results['ids'])}"
    assert len(results['ids'][0]) == 2, f"Expected 2 results, got {len(results['ids'][0])}"
    print("  ✓ ids: nested list format correct")

    assert isinstance(results['documents'][0], list), f"documents[0] should be list"
    assert len(results['documents'][0]) == 2, f"Expected 2 documents"
    print("  ✓ documents: nested list format correct")

    assert isinstance(results['metadatas'][0], list), f"metadatas[0] should be list"
    assert len(results['metadatas'][0]) == 2, f"Expected 2 metadatas"
    print("  ✓ metadatas: nested list format correct")

    assert isinstance(results['distances'][0], list), f"distances[0] should be list"
    assert len(results['distances'][0]) == 2, f"Expected 2 distances"
    print("  ✓ distances: nested list format correct")

    print("  ✓ Query response format: NESTED LISTS VERIFIED!")

    # Verify metadata preserved
    print("  5c: Verify metadata round-trip...")
    for meta in results['metadatas'][0]:
        assert 'date' in meta, f"Missing 'date' in metadata: {meta}"
        assert 'source' in meta, f"Missing 'source' in metadata: {meta}"
    print("  ✓ Metadata round-trip successful")

    # Verify distances are numeric
    print("  5d: Verify distances...")
    for dist in results['distances'][0]:
        assert isinstance(dist, (int, float)), f"Distance should be numeric, got {type(dist)}"
        assert dist >= 0, f"Distance should be non-negative, got {dist}"
    print("  ✓ Distances valid")

    print(f"  ✓ Query vector search: returned {len(results['ids'][0])} results")


def test_list_collections():
    """Test listing all collections"""
    print("\nTest 6: List collections...")
    collections = client.list_collections()
    names = [c.name for c in collections]
    assert "test_collection" in names, f"Expected 'test_collection' in {names}"
    assert "test_add" in names, f"Expected 'test_add' in {names}"
    print(f"✓ List collections: {names}")


def test_delete_collection():
    """Test deleting a collection"""
    print("\nTest 7: Delete collection...")
    client.delete_collection("test_collection")
    collections = client.list_collections()
    names = [c.name for c in collections]
    assert "test_collection" not in names, f"'test_collection' should be deleted, but found in {names}"
    print("✓ Delete collection")


def test_error_handling():
    """Test error cases"""
    print("\nTest 8: Error handling...")
    try:
        client.get_collection("nonexistent")
        assert False, "Should raise ValueError for missing collection"
    except ValueError as e:
        assert "not found" in str(e).lower(), f"Expected 'not found' in error message, got: {e}"
        print("✓ Error handling (missing collection)")


def cleanup():
    """Clean up test database"""
    print("\nCleaning up...")
    import shutil
    if os.path.exists('./test_zvec_db'):
        shutil.rmtree('./test_zvec_db')
    print("✓ Cleanup complete")


def main():
    print("=" * 60)
    print("Testing zvec client implementation")
    print("=" * 60)
    print()

    try:
        test_create_collection()
        test_add_documents()
        test_count()
        test_get_documents()
        test_query_vector_search()  # MOST CRITICAL TEST
        test_list_collections()
        test_delete_collection()
        test_error_handling()

        print()
        print("=" * 60)
        print("✅ ALL TESTS PASSED - zvec implementation ready!")
        print("=" * 60)
        return 0

    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1

    finally:
        cleanup()


if __name__ == "__main__":
    sys.exit(main())
