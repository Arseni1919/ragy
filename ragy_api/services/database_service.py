import os
from datetime import datetime
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
            sample = col.get(limit=3, include=["documents", "metadatas"])
            for doc, meta in zip(sample['documents'], sample['metadatas']):
                sample_data.append({
                    "date": meta.get('date', 'N/A'),
                    "content": doc[:100] if doc else ""
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


def get_collection_size_mb(collection_id: str) -> float:
    db_path = os.getenv('DB_PATH', './ragy_db')
    col_dir = os.path.join(db_path, str(collection_id))

    if not os.path.exists(col_dir):
        return 0.0

    total_bytes = 0
    for root, dirs, files in os.walk(col_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_bytes += os.path.getsize(file_path)
            except:
                pass

    return total_bytes / (1024 * 1024)


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


def get_all_collections_with_stats() -> dict:
    collections = db_client.list_collections()

    collection_stats = []
    total_docs = 0

    for collection in collections:
        col = db_client.get_collection(name=collection.name)
        count = col.count()
        size_mb = get_collection_size_mb(col.id)
        earliest, latest = get_collection_date_range(col)

        total_docs += count

        collection_stats.append({
            "name": collection.name,
            "count": count,
            "size_mb": size_mb,
            "earliest_date": earliest,
            "latest_date": latest
        })

    collection_stats.sort(key=lambda x: x['size_mb'], reverse=True)

    total_size_mb = get_total_database_size_mb()

    return {
        "total_collections": len(collections),
        "total_documents": total_docs,
        "total_size_mb": total_size_mb,
        "avg_docs_per_collection": total_docs / len(collections) if collections else 0,
        "collections": collection_stats
    }
