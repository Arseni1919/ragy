#!/usr/bin/env python3
"""
Phase 3 Integration Testing - zvec Backend
Tests all critical services and endpoints with zvec
"""

import os
os.environ['DB_PROVIDER'] = 'zvec'
os.environ['DB_PATH'] = './test_integration_zvec'

import sys
import numpy as np
from rich.console import Console

console = Console()

def test_extract_service():
    """Test extract_service.py - CRITICAL for nested list format"""
    console.print("\n[bold cyan]Test 1: Extract Service (Vector Search)[/bold cyan]")

    from ragy_api.services import extract_service
    from conn_db.client import client

    # Create test collection
    col = client.get_or_create_collection("test_extract")

    # Add test documents
    console.print("  Adding test documents...")
    col.add(
        ids=["doc1", "doc2", "doc3"],
        documents=[
            "Python is a programming language",
            "JavaScript is used for web development",
            "Machine learning uses Python"
        ],
        embeddings=[np.random.rand(768).tolist() for _ in range(3)],
        metadatas=[
            {"date": "2024-01-01", "source": "test"},
            {"date": "2024-01-02", "source": "test"},
            {"date": "2024-01-03", "source": "test"}
        ]
    )

    # Test list_collections
    console.print("  Testing list_collections()...")
    collections = extract_service.list_collections()
    assert "test_extract" in collections, f"Expected 'test_extract' in {collections}"
    console.print(f"  ✓ Found collections: {collections}")

    # Test extract_relevant_days - CRITICAL
    console.print("  Testing extract_relevant_days() [CRITICAL]...")
    results = extract_service.extract_relevant_days(
        query="Python programming",
        collection_name="test_extract",
        top_k=2
    )

    assert len(results) > 0, "Expected results from extract_relevant_days"
    assert 'date' in results[0], f"Missing 'date' in result: {results[0]}"
    assert 'content' in results[0], f"Missing 'content' in result: {results[0]}"
    assert 'score' in results[0], f"Missing 'score' in result: {results[0]}"
    assert 'metadata' in results[0], f"Missing 'metadata' in result: {results[0]}"
    console.print(f"  ✓ extract_relevant_days returned {len(results)} results")
    console.print(f"  ✓ First result score: {results[0]['score']:.4f}")

    # Test extract_all_with_scores - CRITICAL
    console.print("  Testing extract_all_with_scores() [CRITICAL]...")
    all_results = extract_service.extract_all_with_scores(
        query="Python",
        collection_name="test_extract"
    )

    assert len(all_results) == 3, f"Expected 3 results, got {len(all_results)}"
    console.print(f"  ✓ extract_all_with_scores returned {len(all_results)} results")

    # Cleanup
    client.delete_collection("test_extract")
    console.print("[bold green]✓ Extract Service: ALL TESTS PASSED[/bold green]")


def test_database_service():
    """Test database_service.py functions"""
    console.print("\n[bold cyan]Test 2: Database Service[/bold cyan]")

    from ragy_api.services import database_service
    from conn_db.client import client

    # Create test collection
    col = client.get_or_create_collection("test_db_service")
    col.add(
        ids=["doc1", "doc2"],
        documents=["First doc", "Second doc"],
        embeddings=[np.random.rand(768).tolist() for _ in range(2)],
        metadatas=[
            {"date": "2024-01-01"},
            {"date": "2024-01-02"}
        ]
    )

    # Test get_all_collections
    console.print("  Testing get_all_collections()...")
    all_cols = database_service.get_all_collections()
    assert len(all_cols) > 0, "Expected at least one collection"
    console.print(f"  ✓ Found {len(all_cols)} collections")

    # Test get_collection_by_name
    console.print("  Testing get_collection_by_name()...")
    col_info = database_service.get_collection_by_name("test_db_service")
    assert col_info['name'] == "test_db_service", f"Expected 'test_db_service', got {col_info['name']}"
    assert col_info['count'] == 2, f"Expected count=2, got {col_info['count']}"
    console.print(f"  ✓ Collection info: {col_info['name']}, count={col_info['count']}")

    # Test get_collection_status
    console.print("  Testing get_collection_status()...")
    status = database_service.get_collection_status("test_db_service")
    assert 'exists' in status, "Missing 'exists' in status"
    assert status['exists'] == True, "Collection should exist"
    console.print(f"  ✓ Collection status: exists={status['exists']}, count={status.get('count', 0)}")

    # Test get_head_documents
    console.print("  Testing get_head_documents()...")
    head_docs = database_service.get_head_documents("test_db_service", limit=1)
    assert len(head_docs) == 1, f"Expected 1 document, got {len(head_docs)}"
    console.print(f"  ✓ Head documents: {len(head_docs)} docs")

    # Test get_tail_documents
    console.print("  Testing get_tail_documents()...")
    tail_docs = database_service.get_tail_documents("test_db_service", limit=1)
    assert len(tail_docs) == 1, f"Expected 1 document, got {len(tail_docs)}"
    console.print(f"  ✓ Tail documents: {len(tail_docs)} docs")

    # Cleanup
    client.delete_collection("test_db_service")
    console.print("[bold green]✓ Database Service: ALL TESTS PASSED[/bold green]")


def test_index_service():
    """Test index_service.py - parallel processing"""
    console.print("\n[bold cyan]Test 3: Index Service (Parallel Processing)[/bold cyan]")

    # Note: We won't test full indexing (requires API calls)
    # Just verify the service can be imported and collection creation works
    from ragy_api.services import index_service
    from conn_db.client import client

    # Create a test collection to verify index_service can work with zvec
    col = client.get_or_create_collection("test_index")

    # Simulate what index_service does - add multiple documents
    console.print("  Testing batch document addition...")
    ids = [f"doc{i}" for i in range(10)]
    docs = [f"Document {i}" for i in range(10)]
    embeddings = [np.random.rand(768).tolist() for _ in range(10)]
    metadatas = [{"date": f"2024-01-{i+1:02d}", "source": "test"} for i in range(10)]

    col.add(ids=ids, documents=docs, embeddings=embeddings, metadatas=metadatas)

    count = col.count()
    assert count == 10, f"Expected 10 documents, got {count}"
    console.print(f"  ✓ Added 10 documents in batch")

    # Cleanup
    client.delete_collection("test_index")
    console.print("[bold green]✓ Index Service: BATCH OPERATIONS WORKING[/bold green]")


def cleanup():
    """Clean up test database"""
    import shutil
    if os.path.exists('./test_integration_zvec'):
        shutil.rmtree('./test_integration_zvec')
        console.print("\n[dim]✓ Cleanup complete[/dim]")


def main():
    console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")
    console.print("[bold yellow]Phase 3: zvec Integration Testing[/bold yellow]")
    console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")

    try:
        test_extract_service()
        test_database_service()
        test_index_service()

        console.print("\n[bold yellow]" + "=" * 60 + "[/bold yellow]")
        console.print("[bold green]✅ ALL INTEGRATION TESTS PASSED![/bold green]")
        console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")
        console.print("\n[bold cyan]Next:[/bold cyan] Test API endpoints with running server")
        return 0

    except Exception as e:
        console.print("\n[bold yellow]" + "=" * 60 + "[/bold yellow]")
        console.print(f"[bold red]❌ TEST FAILED: {e}[/bold red]")
        console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        cleanup()


if __name__ == "__main__":
    sys.exit(main())
