from fastapi import APIRouter
from src.api.models import QueryRequest, QueryResponse
from src.generation.generator import generate_response

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest) -> QueryResponse:
    answer = generate_response(req.query)
    return QueryResponse(answer=answer)

@router.get("/health")
async def health():
    return {"status": "ok"}