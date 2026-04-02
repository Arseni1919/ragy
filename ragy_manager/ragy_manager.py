import re
from typing import Generator

from conn_tavily.client import client as tavily_client
from ragy_extractor.client import extract_relevant_days
from ragy_creator.client import create_index
from conn_db.client import client as db_client
from conn_emb_hugging_face.client import MODEL, model


def execute_web_search(query: str) -> str:
    response = tavily_client.search(query)
    results = response.get('results', [])

    if not results:
        return "No results found."

    output = f"Web Search Results for: '{query}'\n"
    output += "=" * 60 + "\n\n"

    for i, result in enumerate(results[:5], 1):
        output += f"{i}. {result.get('title', 'No title')}\n"
        output += f"   URL: {result.get('url', 'N/A')}\n"
        output += f"   {result.get('content', 'No content')[:200]}...\n\n"

    return output


def execute_data_extraction(
    query: str,
    top_k: int,
    collection_name: str
) -> Generator[dict, None, None]:
    try:
        yield {"status": "in_progress", "progress": 10.0, "message": "Extracting data..."}

        results = extract_relevant_days(query, collection_name, top_k)

        if not results:
            yield {"status": "error", "progress": 0.0, "message": "No results found"}
            return

        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        date_only = all(date_pattern.match(r['content'].strip()) for r in results)

        if date_only:
            yield {"status": "in_progress", "progress": 30.0, "message": "Date-only results, searching web..."}

            enriched_results = []
            for i, result in enumerate(results):
                search_query = f"{query} {result['date']}"
                web_result = execute_web_search(search_query)
                enriched_results.append({
                    "date": result['date'],
                    "content": web_result,
                    "score": result['score']
                })
                progress = 30.0 + (i + 1) / len(results) * 60.0
                yield {"status": "in_progress", "progress": progress, "message": f"Searched {i+1}/{len(results)} dates"}

            results = enriched_results

        output = f"Data Extraction Results for: '{query}'\n"
        output += f"Collection: {collection_name} | Top {top_k} results\n"
        output += "=" * 60 + "\n\n"

        for i, result in enumerate(results, 1):
            output += f"{i}. Date: {result['date']} | Score: {result['score']:.3f}\n"
            output += f"   {result['content'][:300]}...\n\n"

        yield {"status": "success", "progress": 100.0, "message": output}

    except Exception as e:
        yield {"status": "error", "progress": 0.0, "message": f"Error: {str(e)}"}


def execute_index_creation(
    query: str,
    collection_name: str,
    save_full_data: bool,
    num_days: int = 365
) -> Generator[dict, None, None]:
    try:
        for update in create_index(query, collection_name, save_full_data, num_days):
            if update['status'] == 'success':
                message = f"Index Creation Complete\n"
                message += "=" * 60 + "\n"
                message += f"Query: {query}\n"
                message += f"Collection: {collection_name}\n"
                message += f"Full Data: {save_full_data}\n"
                message += f"Result: {update['message']}\n"
                yield {"status": "success", "progress": 100.0, "message": message}
            else:
                yield update
    except Exception as e:
        yield {"status": "error", "progress": 0.0, "message": f"Error: {str(e)}"}


def show_db_content() -> str:
    collections = db_client.list_collections()

    if not collections:
        return "Database is empty. No collections found."

    output = "Database Content\n"
    output += "=" * 60 + "\n\n"

    for collection in collections:
        output += f"Collection: {collection.name}\n"
        output += "-" * 60 + "\n"

        col = db_client.get_collection(name=collection.name)
        count = col.count()
        output += f"Total documents: {count}\n"

        if count > 0:
            sample = col.get(limit=3, include=["documents", "metadatas"])
            output += "\nSample Data:\n"
            for i, (doc, meta) in enumerate(zip(sample['documents'], sample['metadatas']), 1):
                output += f"  {i}. Date: {meta.get('date', 'N/A')}\n"
                output += f"     {doc[:100]}...\n"

        output += "\n"

    return output


def show_emb_info() -> str:
    output = "Embedding Model Information\n"
    output += "=" * 60 + "\n\n"
    output += f"Model: {MODEL}\n"
    output += f"Dimensions: {model.get_sentence_embedding_dimension()}\n"
    output += f"Max Sequence Length: {model.max_seq_length}\n"
    output += f"Context Window: ~256 tokens (~190-200 words)\n"
    return output
