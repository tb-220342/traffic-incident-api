from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.logging import configure_logging, log_request
from app.database import configure_database, init_db
from app.routers.incidents import router as incidents_router
from app.routers.stream import router as stream_router
from app.services.sse_manager import SSEManager


def build_error_body(status_code: int, detail) -> dict:
    if isinstance(detail, dict):
        return {
            "success": False,
            "error": {
                "code": detail.get("code", "HTTP_ERROR"),
                "message": detail.get("message", "Request failed"),
                "details": detail.get("details"),
            },
        }

    code = {
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
    }.get(status_code, "HTTP_ERROR")
    return {
        "success": False,
        "error": {
            "code": code,
            "message": str(detail),
            "details": None,
        },
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    configure_database(force=True)
    logger = configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Traffic incident monitoring back-end with real-time SSE updates.",
        lifespan=lifespan,
    )
    app.state.sse_manager = SSEManager()
    app.state.logger = logger

    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        return await log_request(logger, request, call_next)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=build_error_body(
                422,
                {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation error",
                    "details": exc.errors(),
                },
            ),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_body(exc.status_code, exc.detail),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("unhandled_exception path=%s", request.url.path)
        return JSONResponse(
            status_code=500,
            content=build_error_body(
                500,
                {
                    "code": "INTERNAL_ERROR",
                    "message": "Internal server error",
                },
            ),
        )

    @app.get("/health", include_in_schema=False)
    async def healthcheck():
        return {"success": True, "data": {"status": "ok"}}

    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/ui/")

    app.include_router(stream_router)
    app.include_router(incidents_router)

    ui_directory = Path(__file__).resolve().parent.parent / "ui"
    app.mount("/ui", StaticFiles(directory=ui_directory, html=True), name="ui")

    return app


app = create_app()
