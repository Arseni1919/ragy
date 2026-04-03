import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ragy_api.models import IndexCreateRequest, IndexStatusResponse
from ragy_api.services.index_service import create_index
from ragy_api.services.database_service import get_collection_status
from ragy_api.config import settings


router = APIRouter()


@router.post("/create")
async def create_index_endpoint(request: IndexCreateRequest):
    async def generate():
        for update in create_index(
            request.query,
            request.collection_name,
            request.save_full_data,
            request.num_days,
            settings.RAGY_MAX_CONCURRENT
        ):
            yield f"data: {json.dumps(update)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/status/{collection_name}", response_model=IndexStatusResponse)
async def get_index_status(collection_name: str):
    return get_collection_status(collection_name)
