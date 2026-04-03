from datetime import date, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from ragy_api.config import settings
from ragy_api.services.extract_service import list_collections
from ragy_api.services.index_service import process_day
from conn_db.client import client as db_client


scheduler = AsyncIOScheduler()


async def daily_update_all_collections():
    print("Starting daily update for all collections...")
    collections = list_collections()

    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    for collection_name in collections:
        try:
            print(f"Updating collection: {collection_name}")
            collection = db_client.get_collection(name=collection_name)

            sample = collection.get(limit=1, include=["metadatas"])
            if not sample or not sample['metadatas']:
                print(f"Skipping {collection_name}: no metadata found")
                continue

            metadata = sample['metadatas'][0]
            original_query = metadata.get('title', '')

            if not original_query:
                print(f"Skipping {collection_name}: no query in metadata")
                continue

            result = process_day(original_query, yesterday, save_full_data=True)
            if result:
                doc_id, document, embedding, meta = result
                collection.add(
                    ids=[doc_id],
                    documents=[document],
                    embeddings=[embedding],
                    metadatas=[meta]
                )
                print(f"Updated {collection_name} with data for {yesterday}")
            else:
                print(f"No data found for {collection_name} on {yesterday}")

        except Exception as e:
            print(f"Error updating {collection_name}: {e}")

    print("Daily update completed")


async def trigger_manual_update(collection_name: str):
    print(f"Manual update triggered for: {collection_name}")
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        collection = db_client.get_collection(name=collection_name)

        sample = collection.get(limit=1, include=["metadatas"])
        if not sample or not sample['metadatas']:
            print(f"No metadata found in {collection_name}")
            return

        metadata = sample['metadatas'][0]
        original_query = metadata.get('title', '')

        if not original_query:
            print(f"No query found in metadata for {collection_name}")
            return

        result = process_day(original_query, yesterday, save_full_data=True)
        if result:
            doc_id, document, embedding, meta = result
            collection.add(
                ids=[doc_id],
                documents=[document],
                embeddings=[embedding],
                metadatas=[meta]
            )
            print(f"Successfully updated {collection_name} with data for {yesterday}")
        else:
            print(f"No data found for {collection_name} on {yesterday}")

    except Exception as e:
        print(f"Error in manual update for {collection_name}: {e}")


def init_scheduler():
    if not settings.SCHEDULER_ENABLED:
        print("Scheduler disabled by configuration")
        return

    scheduler.add_job(
        daily_update_all_collections,
        CronTrigger(
            hour=settings.SCHEDULER_HOUR,
            timezone=settings.SCHEDULER_TIMEZONE
        ),
        id='daily_update',
        name='Daily Collection Update',
        replace_existing=True
    )
    scheduler.start()
    print(f"Scheduler started: daily updates at {settings.SCHEDULER_HOUR}:00 {settings.SCHEDULER_TIMEZONE}")


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler shut down")
