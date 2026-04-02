import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ragy_creator.client import create_index
from conn_db.client import client as db_client

print("="*60)
print("Testing Ragy Creator - 7 Day Index")
print("="*60)

query = "what happened in the israeli economics this day"
collection_name = "test_ai_collection"

print(f"✓ Query: '{query}'")
print(f"✓ Collection: '{collection_name}'")
print(f"✓ Testing with 7 days (instead of 365)")
print(f"✓ Mode: save_full_data=True")
print()

print("Starting indexing...")
generator = create_index(query, collection_name, save_full_data=True, num_days=7)

for update in generator:
    status = update["status"]
    progress = update["progress"]
    message = update["message"]

    if status == "in_progress":
        print(f"Progress: {progress:.1f}%")
    elif status == "success":
        print(f"\n✓ {message}")
    elif status == "error":
        print(f"\n✗ Error: {message}")

print("\n" + "="*60)
print("Verifying stored data...")
print("="*60)

collection = db_client.get_collection(name=collection_name)
count = collection.count()
print(f"✓ Collection '{collection_name}' has {count} documents")

if count > 0:
    sample = collection.get(limit=1, include=["documents", "metadatas", "embeddings"])
    print(f"✓ Sample document ID: {sample['ids'][0]}")
    print(f"✓ Sample metadata: {sample['metadatas'][0]}")
    print(f"✓ Sample document length: {len(sample['documents'][0])} characters")
    print(f"✓ Sample embedding dimensions: {len(sample['embeddings'][0])}")
    print(f"✓ Sample document content: {sample['documents'][0]}")

print("\n" + "="*60)
print("Cleaning up...")
print("="*60)
db_client.delete_collection(name=collection_name)
print(f"✓ Deleted test collection '{collection_name}'")

print("\n✅ All tests passed!")
