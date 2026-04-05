from fastapi import APIRouter, HTTPException
from ragy_api.models import DatabaseContentResponse, CollectionDetailResponse, MessageResponse
from ragy_api.services.database_service import (
    get_all_collections,
    get_collection_by_name,
    delete_collection,
    get_all_collections_with_stats,
    get_collection_date_distribution,
    get_sample_document_by_index,
    get_head_documents,
    get_tail_documents
)


router = APIRouter()


@router.get("/content", response_model=DatabaseContentResponse)
async def get_database_content():
    collections = get_all_collections()
    return {"collections": collections}


@router.get("/stats")
async def get_database_stats():
    try:
        return get_all_collections_with_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collection/{name}/distribution")
async def get_collection_distribution(name: str):
    try:
        return get_collection_date_distribution(name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collection/{name}/sample/{index}")
async def get_sample_document(name: str, index: int):
    try:
        doc = get_sample_document_by_index(name, index)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document at index {index} not found")
        return doc
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collection/{name}/head")
async def get_collection_head(name: str, limit: int = 5):
    try:
        return {"documents": get_head_documents(name, limit)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collection/{name}/tail")
async def get_collection_tail(name: str, limit: int = 5):
    try:
        return {"documents": get_tail_documents(name, limit)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
