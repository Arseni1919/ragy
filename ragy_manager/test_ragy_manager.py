from ragy_manager.ragy_manager import (
    execute_web_search,
    execute_data_extraction,
    execute_index_creation,
    show_db_content,
    show_emb_info
)

print("=" * 60)
print("TEST 1: Web Search")
print("=" * 60)
result = execute_web_search("latest AI news")
print(result)

print("\n" + "=" * 60)
print("TEST 2: Show Embedding Info")
print("=" * 60)
result = show_emb_info()
print(result)

print("\n" + "=" * 60)
print("TEST 3: Show DB Content")
print("=" * 60)
result = show_db_content()
print(result)

print("\n" + "=" * 60)
print("TEST 4: Data Extraction")
print("=" * 60)
for update in execute_data_extraction("breakthroughs", 5, "persistent_test_data"):
    if update['status'] == 'success':
        print(update['message'])
    else:
        print(f"[{update['status']}] Progress: {update['progress']:.1f}% - {update['message']}")

print("\n" + "=" * 60)
print("TEST 5: Index Creation (5 days)")
print("=" * 60)
for update in execute_index_creation("AI news", "test_small_collection", True, 5):
    if update['status'] == 'success':
        print(update['message'])
    elif update['status'] == 'in_progress':
        print(f"Progress: {update['progress']:.1f}%", end='\r')
    else:
        print(f"[{update['status']}] {update['message']}")

print("\n\nAll tests completed!")
