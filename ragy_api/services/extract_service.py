from conn_emb_hugging_face.client import get_query_embedding
from conn_db.client import client as db_client


def list_collections() -> list[str]:
    collections = db_client.list_collections()
    return [c.name for c in collections]


def extract_relevant_days(
    query: str,
    collection_name: str,
    top_k: int = 10
) -> list[dict]:
    try:
        query_embedding = get_query_embedding(query)

        collection = db_client.get_collection(name=collection_name)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        output = []
        for doc, meta, dist in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            output.append({
                "date": meta.get("date", ""),
                "content": doc,
                "score": 1 / (1 + dist),
                "metadata": meta
            })

        return output

    except Exception as e:
        print(f"Error in extract_relevant_days: {e}")
        return []

def extract_all_with_scores(
    query: str,
    collection_name: str
) -> list[dict]:
    """Get ALL documents with similarity scores for timeline visualization"""
    try:
        query_embedding = get_query_embedding(query)
        collection = db_client.get_collection(name=collection_name)

        max_results = collection.count()
        if max_results == 0:
            return []

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=max_results,
            include=["documents", "metadatas", "distances"]
        )

        output = []
        for doc, meta, dist in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            output.append({
                "date": meta.get("date", ""),
                "content": doc,
                "score": 1 / (1 + dist),
                "metadata": meta
            })

        output.sort(key=lambda x: x['date'])
        return output

    except Exception as e:
        print(f"Error in extract_all_with_scores: {e}")
        return []
