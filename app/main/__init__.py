from fastapi import FastAPI

from app.api.v1.routes import api_router
from app.core.config import settings


app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(api_router, prefix="/api/v1")
