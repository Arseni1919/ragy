from fastapi import APIRouter, HTTPException
from ragy_api.models import DatabaseContentResponse, CollectionDetailResponse, MessageResponse
from ragy_api.services.database_service import (
    get_all_collections,
    get_collection_by_name,
    delete_collection
)


router = APIRouter()


@router.get("/content", response_model=DatabaseContentResponse)
async def get_database_content():
    collections = get_all_collections()
    return {"collections": collections}


@router.get("/collection/{name}", response_model=CollectionDetailResponse)
async def get_collection(name: str):
    try:
        return get_collection_by_name(name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/collection/{name}", response_model=MessageResponse)
async def remove_collection(name: str):
    try:
        delete_collection(name)
        return {"message": f"Collection '{name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
