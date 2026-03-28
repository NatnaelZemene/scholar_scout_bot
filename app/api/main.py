from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.routers.router import router as api_router
from app.domain.services.exceptions import ConflictError, NotFoundError

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
)

app.include_router(api_router)


def _error_response(request: Request, status_code: int, code: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": detail,
            "code": code,
            "path": str(request.url.path),
        },
    )


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return _error_response(request, status.HTTP_404_NOT_FOUND, "not_found", str(exc))


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return _error_response(request, status.HTTP_409_CONFLICT, "conflict", str(exc))


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return _error_response(request, status.HTTP_422_UNPROCESSABLE_ENTITY, "validation_error", str(exc))


@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception) -> JSONResponse:
    return _error_response(request, status.HTTP_500_INTERNAL_SERVER_ERROR, "internal_error", str(exc))

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/ping")
def ping():
    return {"message": "pong"}