
from fastapi import APIRouter, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from src.api.models import QueryRequest, QueryResponse
from src.generation.generator import generate_response
from src.security.input_guard import quick_check as input_quick_check
from src.security.output_guard import check_output as output_quick_check
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()


api_key_header = APIKeyHeader(name="X-API-Key")
async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("FINSIGHT_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid or missing API key")


@router.post("/query", response_model=QueryResponse, dependencies=[Depends(verify_api_key)])
async def query(req: QueryRequest) -> QueryResponse:
    is_safe, message = input_quick_check(req.query) 
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
