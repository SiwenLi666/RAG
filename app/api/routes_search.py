from fastapi import APIRouter
from app.api.schemas import SearchRequest, SearchResponse
from app.core.search_service import SearchService

router = APIRouter()

search_service = SearchService()


@router.post("/search", response_model=SearchResponse)
def search_endpoint(request: SearchRequest):
    results = search_service.search(request)
    return SearchResponse(results=results, total=len(results))
