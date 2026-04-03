import os
from datetime import date, timedelta
from typing import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed

from conn_emb_hugging_face.client import get_document_embedding
from conn_db.client import client as db_client
from .search_service import search_with_retry


def process_day(query: str, day_date: str, save_full_data: bool) -> tuple[str, dict, list[float], dict]:
    query_with_date = f"{query} {day_date}"

    response = search_with_retry(query_with_date)

    if not response or not response.get('results'):
        return None

    first_result = response['results'][0]
    content = first_result.get('content', '') or first_result.get('raw_content', '')

    if not content:
        return None

    embedding = get_document_embedding(content)

    doc_id = f"{day_date}"

    if save_full_data:
        document = content
        metadata = {
            "date": day_date,
            "url": first_result.get('url', ''),
            "title": first_result.get('title', ''),
            "score": first_result.get('score', 0.0)
        }
    else:
        document = day_date
        metadata = {"date": day_date}

    return doc_id, document, embedding, metadata


def create_index(
    query: str,
    collection_name: str,
    save_full_data: bool = True,
    num_days: int = 365,
    max_concurrent: int = 10
) -> Generator[dict, None, None]:
    try:
        dates = []
        today = date.today()
        for i in range(num_days):
            day = today - timedelta(days=i)
            dates.append(day.strftime("%Y-%m-%d"))

        collection = db_client.get_or_create_collection(name=collection_name)

        completed = 0
        failed = 0

        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = {
                executor.submit(process_day, query, day_date, save_full_data): day_date
                for day_date in dates
            }

            for future in as_completed(futures):
                day_date = futures[future]
                try:
                    result = future.result()
                    if result:
                        doc_id, document, embedding, metadata = result
                        collection.add(
                            ids=[doc_id],
                            documents=[document],
                            embeddings=[embedding],
                            metadatas=[metadata]
                        )
                        completed += 1
                    else:
                        failed += 1
                except Exception as e:
                    print(f"Failed to process {day_date}: {e}")
                    failed += 1

                progress = (completed + failed) / num_days * 100
                yield {
                    "status": "in_progress",
                    "progress": progress,
                    "message": f"Processed {completed + failed}/{num_days} days"
                }

        yield {
            "status": "success",
            "progress": 100.0,
            "message": f"{completed}/{num_days} days indexed (failed: {failed})"
        }

    except Exception as e:
        yield {
            "status": "error",
            "progress": 0.0,
            "message": str(e)
        }
