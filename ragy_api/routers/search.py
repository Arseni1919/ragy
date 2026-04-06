from fastapi import APIRouter, Depends
from ragy_api.models import WebSearchRequest, WebSearchResponse
from ragy_api.services.search_service import web_search, yfinance_search
from ragy_api.dependencies import get_tavily_client


router = APIRouter()


@router.post("/web", response_model=WebSearchResponse)
async def search_web(request: WebSearchRequest):
    return web_search(request.query)


@router.post("/yfinance", response_model=WebSearchResponse)
async def search_yfinance_endpoint(request: WebSearchRequest):
    """Search financial data using yfinance (no API key needed)"""
    return yfinance_search(request.query, request.max_results)
