from ragy_manager.ragy_manager import (
    execute_web_search,
    execute_data_extraction,
    execute_index_creation,
    show_db_content,
    show_emb_info,
)


def handle_search():
    """Handle search command"""
    query = input("Enter search query: ").strip()
    if not query:
        print("Query cannot be empty")
        return

    print(f"\nSearching for: {query}")
    result = execute_web_search(query)
    print(result)
    print()


def handle_show_db():
    """Handle show-db command"""
    print("\nDatabase Content:")
    result = show_db_content()
    print(result)
    print()


def handle_show_emb():
    """Handle show-emb command"""
    print("\nEmbedding Information:")
    result = show_emb_info()
    print(result)
    print()


def handle_extract():
    """Handle extract command with progress"""
    query = input("Enter query: ").strip()
    top_k = input("Top K results (default 5): ").strip() or "5"
    collection = input("Collection name: ").strip()

    if not query or not collection:
        print("Query and collection are required")
        return

    print(f"\nExtracting data...")
    for update in execute_data_extraction(query, int(top_k), collection):
        if update['status'] == 'in_progress':
            print(f"\rProgress: {update['progress']:.1f}% - {update['message']}", end='', flush=True)
        elif update['status'] == 'success':
            print(f"\n{update['message']}")
        else:
            print(f"\n[{update['status']}] {update['message']}")
    print()


def handle_create():
    """Handle create command with progress"""
    query = input("Enter query: ").strip()
    collection = input("Collection name: ").strip()
    save_full = input("Save full data? (y/n, default n): ").strip().lower() == 'y'
    num_days = input("Number of days (default 365): ").strip() or "365"

    if not query or not collection:
        print("Query and collection are required")
        return

    print(f"\nCreating index...")
    for update in execute_index_creation(query, collection, save_full, int(num_days)):
        if update['status'] == 'in_progress':
            print(f"\rProgress: {update['progress']:.1f}% - {update['message']}", end='', flush=True)
        elif update['status'] == 'success':
            print(f"\n{update['message']}")
        else:
            print(f"\n[{update['status']}] {update['message']}")
    print()
