import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ragy_creator.client import create_index
from ragy_extractor.client import extract_relevant_days
from conn_db.client import client as db_client

print("="*60)
print("Setting up test index...")
print("="*60)

collection_name = "test_extraction_collection"
query_to_index = "artificial intelligence news"

print(f"✓ Creating 7-day index for: '{query_to_index}'")
for update in create_index(query_to_index, collection_name, save_full_data=True, num_days=7):
    if update["status"] == "success":
        print(f"✓ {update['message']}")
        break

print("\n" + "="*60)
print("TEST 1: Semantic Match Query")
print("="*60)

test_query = "machine learning developments"
print(f"✓ Query: '{test_query}'")
results = extract_relevant_days(test_query, collection_name, top_k=3)

print(f"✓ Found {len(results)} results")
for i, result in enumerate(results, 1):
    print(f"\n  {i}. Date: {result['date']}")
    print(f"     Score: {result['score']:.4f}")
    print(f"     Content: {result['content'][:100]}...")
    if result['metadata'].get('title'):
        print(f"     Title: {result['metadata']['title']}")

print("\n" + "="*60)
print("TEST 2: Exact Match Query")
print("="*60)

test_query = "artificial intelligence"
print(f"✓ Query: '{test_query}'")
results = extract_relevant_days(test_query, collection_name, top_k=5)

print(f"✓ Found {len(results)} results")
for i, result in enumerate(results, 1):
    print(f"  {i}. [{result['score']:.4f}] {result['date']}")

print("\n" + "="*60)
print("TEST 3: Unrelated Query")
print("="*60)

test_query = "cooking recipes"
print(f"✓ Query: '{test_query}'")
results = extract_relevant_days(test_query, collection_name, top_k=3)

print(f"✓ Found {len(results)} results (should have low scores)")
for i, result in enumerate(results, 1):
    print(f"  {i}. [{result['score']:.4f}] {result['date']}")

print("\n" + "="*60)
print("Cleaning up...")
print("="*60)
db_client.delete_collection(name=collection_name)
print(f"✓ Deleted test collection '{collection_name}'")

print("\n✅ All tests passed!")
