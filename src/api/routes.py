from fastapi.security import APIKeyHeader
from src.api.models import QueryRequest, QueryResponse
from src.generation.generator import generate_response, generate_response_stream
from src.security.input_guard import quick_check as input_quick_check
from src.security.output_guard import check_output as output_quick_check
from fastapi import APIRouter, HTTPException, Security, Depends, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

#Applying the rate limitting logic here
limiter = Limiter(key_func=get_remote_address)

api_key_header = APIKeyHeader(name="X-API-Key")
async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("FINSIGHT_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid or missing API key")


@router.post("/query", response_model=QueryResponse, dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")
async def query(request: Request,req: QueryRequest) -> QueryResponse:
    is_safe, message = input_quick_check(req.query) 
    if not is_safe:
        raise HTTPException(status_code=400, detail=message)

    answer = generate_response(req.query)

    is_safe, message = output_quick_check(answer)
    if not is_safe:
        raise HTTPException(status_code=500, detail=message)

    return QueryResponse(answer=answer)


@router.post("/query/stream", dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")
async def query_stream(request: Request, req: QueryRequest):
    is_safe, message = input_quick_check(req.query)
    if not is_safe:
        raise HTTPException(status_code=400, detail=message)

    #Added the check for output guard for streaming responses which was missing from the previous setup
    # 29thOct'26
    def event_stream():
        parts = []
        for chunk in generate_response_stream(req.query):
            parts.append(chunk)
            yield f"data: {chunk}\n\n"

        is_safe, _ = output_quick_check("".join(parts))
        if not is_safe:
            yield "event: replace\ndata: I can't provide an answer to this question.\n\n"
            return

        yield "data: [DONE]\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/health")
async def health():
    return {"status": "ok"}