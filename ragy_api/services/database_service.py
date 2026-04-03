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
