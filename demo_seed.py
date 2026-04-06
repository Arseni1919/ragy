"""
Demo collection seeder for hosted deployment.
Creates a small ai_news_demo collection with 7 days of data.
"""
import asyncio
import os
from ragy_api.services.index_service import create_index_streaming

async def seed_demo_collection():
    """Seed a small demo collection for public access."""

    # Check if demo already exists
    from conn_db.client import db_client
    client = db_client.get_client()
    collections = client.list_collections()

    if any(c.name == "ai_news_demo" for c in collections):
        print("Demo collection already exists, skipping seed.")
        return

    print("Seeding demo collection...")
    print("This will create a 7-day AI news index...")

    # Create 7-day index (fast, ~2-3 minutes)
    async for event in create_index_streaming(
        query="artificial intelligence news",
        collection_name="ai_news_demo",
        num_days=7,
        save_full_data=True
    ):
        print(f"Progress: {event}")

    print("\nDemo collection seeded successfully!")
    print("Collection: ai_news_demo")
    print("Available for querying via API")

if __name__ == "__main__":
    asyncio.run(seed_demo_collection())
