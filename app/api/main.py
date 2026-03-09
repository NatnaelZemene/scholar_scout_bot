from fastapi import FastAPI
from app.core.config import settings
from app.api.routers.router import router as user_router  # or .router, depending on filename

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
)

app.include_router(user_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/ping")
def ping():
    return {"message": "pong"}