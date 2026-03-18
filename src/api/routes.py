from fastapi import APIRouter, HTTPException
from src.api.models import QueryRequest, QueryResponse
from src.generation.generator import generate_response
from src.security.input_guard import quick_check as input_quick_check
from src.security.output_guard import quick_check as output_quick_check

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest) -> QueryResponse:
    is_safe, message = (req.query)
    if not is_safe:
        raise HTTPException(status_code=400, detail=message)

    answer = generate_response(req.query)

    is_safe, message = output_quick_check(answer)
    if not is_safe:
        raise HTTPException(status_code=500, detail=message)

    return QueryResponse(answer=answer)

@router.get("/health")
async def health():
    return {"status": "ok"}
