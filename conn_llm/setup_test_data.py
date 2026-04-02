from ragy_creator.client import create_index

print("="*60)
print("Creating Persistent 265-Day Test Data")
print("="*60)

query = "technology news"
collection_name = "persistent_test_data"
num_days = 265

print(f"✓ Query: '{query}'")
print(f"✓ Collection: '{collection_name}'")
print(f"✓ Days to index: {num_days}")
print(f"✓ Mode: save_full_data=True")
print()
print("⚠️  This will take several minutes due to API rate limits...")
print("⚠️  This collection will NOT be deleted (persistent for testing)")
print()

print("Starting indexing...")
for update in create_index(query, collection_name, save_full_data=True, num_days=num_days):
    status = update["status"]
    progress = update["progress"]
    message = update["message"]

    if status == "in_progress":
        if int(progress) % 10 == 0:
            print(f"Progress: {progress:.1f}%")
    elif status == "success":
        print(f"\n✅ {message}")
    elif status == "error":
        print(f"\n✗ Error: {message}")

print(f"\n✓ Collection '{collection_name}' created and ready for testing")
print("✓ Data is persistent - will not be deleted")
