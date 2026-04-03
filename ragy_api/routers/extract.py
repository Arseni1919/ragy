import json
import re
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ragy_api.models import CollectionsResponse, ExtractRequest
from ragy_api.services.extract_service import list_collections, extract_relevant_days
from ragy_api.services.search_service import web_search


router = APIRouter()


@router.get("/collections", response_model=CollectionsResponse)
async def get_collections():
    collections = list_collections()
    return {"collections": collections}


@router.post("/data")
async def extract_data(request: ExtractRequest):
    async def generate():
        try:
            yield f"data: {json.dumps({'status': 'in_progress', 'progress': 10.0, 'message': 'Extracting data...'})}\n\n"

            results = extract_relevant_days(request.query, request.collection_name, request.top_k)

            if not results:
                yield f"data: {json.dumps({'status': 'error', 'progress': 0.0, 'message': 'No results found'})}\n\n"
                return

            date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
            date_only = all(date_pattern.match(r['content'].strip()) for r in results)

            if date_only:
                yield f"data: {json.dumps({'status': 'in_progress', 'progress': 30.0, 'message': 'Date-only results, searching web...'})}\n\n"

                enriched_results = []
                for i, result in enumerate(results):
                    search_query = f"{request.query} {result['date']}"
                    web_result = web_search(search_query)

                    formatted_content = f"Web Search Results:\n"
                    for r in web_result.get('results', [])[:3]:
                        formatted_content += f"- {r['title']}\n  {r['url']}\n  {r['content'][:150]}...\n\n"

                    enriched_results.append({
                        "date": result['date'],
                        "content": formatted_content,
                        "score": result['score']
                    })
                    progress = 30.0 + (i + 1) / len(results) * 60.0
                    yield f"data: {json.dumps({'status': 'in_progress', 'progress': progress, 'message': f'Searched {i+1}/{len(results)} dates'})}\n\n"

                results = enriched_results

            output_data = {
                "query": request.query,
                "collection": request.collection_name,
                "top_k": request.top_k,
                "results": results
            }

            yield f"data: {json.dumps({'status': 'success', 'progress': 100.0, 'message': 'Extraction complete', 'data': output_data})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'progress': 0.0, 'message': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
