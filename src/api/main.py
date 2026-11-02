from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.api.routes import router
from src.observability.logging_config import configure_logging   # new
from src.api.middleware import RequestLogMiddleware 

configure_logging()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="FinSight API", description="AI-Powered Financial Research Assistant")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(router)
app.add_middleware(RequestLogMiddleware)