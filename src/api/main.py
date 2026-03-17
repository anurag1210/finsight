from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(title="FinSight API", description="AI-Powered Financial Research Assistant")
app.include_router(router)