from datetime import date, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from ragy_api.config import settings
from ragy_api.services.extract_service import list_collections
from ragy_api.services.index_service import process_day
from ragy_api.job_store import JobMetadataStore
from conn_db.client import client as db_client


jobstore = SQLAlchemyJobStore(url='sqlite:///ragy_jobs.db')
scheduler = AsyncIOScheduler(jobstores={'default': jobstore})
job_metadata_store = JobMetadataStore()


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

            existing_docs = collection.count()
            result = process_day(original_query, yesterday, existing_docs)
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

        existing_docs = collection.count()
        result = process_day(original_query, yesterday, existing_docs)
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


async def scheduled_job_task(job_id: int, query: str, collection_name: str):
    from datetime import datetime, timezone
    from conn_emb_hugging_face.client import get_document_embedding
    from ragy_api.services.search_service import search_with_retry

    print(f"Running job {job_id}: '{query}' → {collection_name}")

    utc_timestamp = datetime.now(timezone.utc).isoformat()

    try:
        collection = db_client.get_or_create_collection(name=collection_name)

        response = search_with_retry(query)

        if not response or not response.get('results'):
            print(f"Job {job_id}: No results found")
            job_metadata_store.update_run_stats(job_id, success=True)
            return

        first_result = response['results'][0]
        content = first_result.get('raw_content') or first_result.get('content', '')

        if not content:
            print(f"Job {job_id}: No content in results")
            job_metadata_store.update_run_stats(job_id, success=True)
            return

        embedding = get_document_embedding(content)

        existing_docs = collection.count()
        doc_id = str(existing_docs)

        metadata = {
            "date": utc_timestamp,
            "url": first_result.get('url') or '',
            "title": first_result.get('title') or '',
            "score": first_result.get('score', 0.0),
            "query": query
        }

        collection.add(
            ids=[doc_id],
            documents=[content],
            embeddings=[embedding],
            metadatas=[metadata]
        )

        print(f"Job {job_id} success: Added document at {utc_timestamp}")
        job_metadata_store.update_run_stats(job_id, success=True)

    except Exception as e:
        print(f"Job {job_id} error: {e}")
        job_metadata_store.update_run_stats(job_id, success=False, error=str(e))


def create_user_job(query: str, collection_name: str, interval_type: str, interval_amount: int) -> dict:
    job_id = job_metadata_store.create_job(query, collection_name, interval_type, interval_amount)
    apscheduler_job_id = f"user_job_{job_id}"

    if interval_type == 'minute':
        trigger = IntervalTrigger(minutes=interval_amount)
    elif interval_type == 'hour':
        trigger = IntervalTrigger(hours=interval_amount)
    elif interval_type == 'day':
        trigger = IntervalTrigger(days=interval_amount)
    elif interval_type == 'week':
        trigger = IntervalTrigger(weeks=interval_amount)
    elif interval_type == 'month':
        trigger = CronTrigger(day=1, hour=0, minute=0)
    elif interval_type == 'year':
        trigger = CronTrigger(month='1', day=1, hour=0, minute=0)
    else:
        raise ValueError(f"Invalid interval type: {interval_type}")

    scheduler.add_job(
        scheduled_job_task,
        trigger=trigger,
        args=[job_id, query, collection_name],
        id=apscheduler_job_id,
        name=f"Job {job_id}: {query} → {collection_name}",
        replace_existing=True
    )

    return {
        "job_id": job_id,
        "apscheduler_job_id": apscheduler_job_id,
        "query": query,
        "collection_name": collection_name,
        "interval_type": interval_type,
        "interval_amount": interval_amount
    }


def delete_user_job(job_id: int):
    apscheduler_job_id = f"user_job_{job_id}"
    scheduler.remove_job(apscheduler_job_id)
    job_metadata_store.delete_job(job_id)


def init_scheduler():
    if not settings.SCHEDULER_ENABLED:
        print("Scheduler disabled by configuration")
        return

    scheduler.start()
    print("Scheduler started: user jobs will be loaded from database")


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler shut down")
