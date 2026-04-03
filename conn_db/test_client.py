from conn_db.client import client

print("Testing ChromaDB client...")

collection = client.get_or_create_collection("test")
print(f"✓ Collection created: {collection.name}")

collection.add(
    documents=["test doc"],
    embeddings=[[0.1, 0.2, 0.3]],
    metadatas=[{"date": "2026-04-02"}],
    ids=["test1"]
)
print(f"✓ Document added")

count = collection.count()
print(f"✓ Count: {count}")

collections = [c.name for c in client.list_collections()]
print(f"✓ Collections: {collections}")

client.delete_collection("test")
print(f"✓ Test collection deleted")

print("\n✅ All tests passed!")
