import os
from datetime import datetime
from collections import Counter
from conn_db.client import client as db_client


def get_all_collections() -> list[dict]:
    collections = db_client.list_collections()

    output = []
    for collection in collections:
        col = db_client.get_collection(name=collection.name)
        count = col.count()

        sample_data = []
        if count > 0:
            sample = col.get(limit=3, include=["documents", "metadatas"])
            for doc, meta in zip(sample['documents'], sample['metadatas']):
                sample_data.append({
                    "date": meta.get('date', 'N/A'),
                    "content": doc[:100] if doc else ""
                })

        output.append({
            "name": collection.name,
            "count": count,
            "sample_data": sample_data
        })

    return output


def get_collection_by_name(name: str) -> dict:
    try:
        col = db_client.get_collection(name=name)
        count = col.count()

        sample_data = []
        if count > 0:
            sample = col.get(limit=5, include=["documents", "metadatas"])
            for doc, meta in zip(sample['documents'], sample['metadatas']):
                content = doc if doc else ""
                if len(content) > 200:
                    content = content[:200] + "..."

                date_str = meta.get('date', 'N/A')
                if date_str != 'N/A':
                    try:
                        parsed = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        date_str = parsed.strftime("%Y-%m-%d")
                    except:
                        pass

                sample_data.append({
                    "date": date_str,
                    "content": content
                })

        return {
            "name": name,
            "count": count,
            "sample_data": sample_data
        }
    except Exception as e:
        raise ValueError(f"Collection not found: {name}")


def delete_collection(name: str):
    db_client.delete_collection(name=name)


def get_collection_status(name: str) -> dict:
    try:
        col = db_client.get_collection(name=name)
        count = col.count()
        return {
            "collection_name": name,
            "exists": True,
            "total_docs": count
        }
    except:
        return {
            "collection_name": name,
            "exists": False,
            "total_docs": 0
        }


def get_total_database_size_mb() -> float:
    db_path = os.getenv('DB_PATH', './ragy_db')

    if not os.path.exists(db_path):
        return 0.0

    total_bytes = 0
    for root, dirs, files in os.walk(db_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_bytes += os.path.getsize(file_path)
            except:
                pass

    return total_bytes / (1024 * 1024)


def get_collection_date_range(col) -> tuple[str, str]:
    try:
        count = col.count()
        if count == 0:
            return "N/A", "N/A"

        sample = col.get(limit=min(100, count), include=["metadatas"])

        dates = []
        for meta in sample['metadatas']:
            date_str = meta.get('date')
            if date_str:
                try:
                    dates.append(datetime.fromisoformat(date_str.replace('Z', '+00:00')))
                except:
                    pass

        if not dates:
            return "N/A", "N/A"

        earliest = min(dates).strftime("%Y-%m-%d")
        latest = max(dates).strftime("%Y-%m-%d")
        return earliest, latest
    except:
        return "N/A", "N/A"


def get_collection_date_distribution(name: str) -> dict:
    try:
        col = db_client.get_collection(name=name)
        count = col.count()

        if count == 0:
            return {"dates": [], "counts": []}

        all_data = col.get(include=["metadatas"])

        dates = []
        for meta in all_data['metadatas']:
            date_str = meta.get('date')
            if date_str:
                try:
                    parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    dates.append(parsed_date.strftime("%Y-%m-%d"))
                except:
                    pass

        if not dates:
            return {"dates": [], "counts": []}

        date_counts = Counter(dates)
        sorted_dates = sorted(date_counts.items())

        return {
            "dates": [date for date, _ in sorted_dates],
            "counts": [count for _, count in sorted_dates]
        }
    except Exception as e:
        raise ValueError(f"Collection not found: {name}")


def get_head_documents(collection_name: str, limit: int = 5) -> list[dict]:
    try:
        col = db_client.get_collection(name=collection_name)
        count = col.count()

        if count == 0:
            return []

        actual_limit = min(limit, count)
        result = col.get(limit=actual_limit, include=["documents", "metadatas"])

        documents = []
        for i, (doc_id, doc, meta) in enumerate(zip(result['ids'], result['documents'], result['metadatas'])):
            documents.append({
                "id": doc_id,
                "index": i,
                "content": doc,
                "metadata": meta
            })

        return documents
    except Exception as e:
        raise ValueError(f"Collection not found: {collection_name}")


def get_tail_documents(collection_name: str, limit: int = 5) -> list[dict]:
    try:
        col = db_client.get_collection(name=collection_name)
        count = col.count()

        if count == 0:
            return []

        actual_limit = min(limit, count)
        start_index = count - actual_limit

        all_ids = col.get(include=[])['ids']
        tail_ids = all_ids[start_index:]

        result = col.get(ids=tail_ids, include=["documents", "metadatas"])

        documents = []
        for i, (doc_id, doc, meta) in enumerate(zip(result['ids'], result['documents'], result['metadatas']), start=start_index):
            documents.append({
                "id": doc_id,
                "index": i,
                "content": doc,
                "metadata": meta
            })

        return documents
    except Exception as e:
        raise ValueError(f"Collection not found: {collection_name}")


def get_sample_document_by_index(collection_name: str, index: int) -> dict:
    try:
        col = db_client.get_collection(name=collection_name)
        count = col.count()

        if index < 0 or index >= count:
            return None

        all_ids = col.get(include=[])['ids']

        if index >= len(all_ids):
            return None

        doc_id = all_ids[index]

        result = col.get(ids=[doc_id], include=["documents", "embeddings", "metadatas"])

        if len(result['documents']) == 0:
            return None

        document = result['documents'][0]
        metadata = result['metadatas'][0]
        embedding_list = result['embeddings'][0].tolist()

        return {
            "id": doc_id,
            "content": document,
            "embedding": embedding_list,
            "metadata": metadata
        }

    except Exception as e:
        raise ValueError(f"Error retrieving document: {str(e)}")


def get_all_collections_with_stats() -> dict:
    collections = db_client.list_collections()

    collection_stats = []
    total_docs = 0

    for collection in collections:
        col = db_client.get_collection(name=collection.name)
        count = col.count()
        earliest, latest = get_collection_date_range(col)

        total_docs += count

        collection_stats.append({
            "name": collection.name,
            "count": count,
            "earliest_date": earliest,
            "latest_date": latest
        })

    collection_stats.sort(key=lambda x: x['count'], reverse=True)

    total_size_mb = get_total_database_size_mb()

    return {
        "total_collections": len(collections),
        "total_documents": total_docs,
        "total_size_mb": total_size_mb,
        "avg_docs_per_collection": total_docs / len(collections) if collections else 0,
        "collections": collection_stats
    }
