"""
Main application entry point for the AI Quote Generator.
Serves the API and the built React frontend from one process.
"""

import hmac
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest

from app import observability
from app.api.routes import quote_router
from app.api.routes.quote_routes import circuit_breakers
from app.config import settings
from app.llm.factory import model_specs


# Configure logging; every line carries the request ID
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s [%(request_id)s] %(name)s: %(message)s"
)
for handler in logging.getLogger().handlers:
    handler.addFilter(observability.RequestIdFilter())
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Quote Generator powered by Google Gemini",
    docs_url="/docs" if settings.debug else None,
    redoc_url=None,
)


# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.error(f"Validation error for {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


# The bundled frontend is same-origin, so CORS is only needed for extra origins that
# are configured explicitly. No credentials: the API uses no cookies or auth.
if settings.allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

app.middleware("http")(observability.observe_http)

# Include API routers
app.include_router(quote_router)

observability.BUILD_INFO.labels(settings.app_version, settings.default_model).set(1)
REGISTRY.register(observability.CircuitCollector(circuit_breakers))


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, object]:
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "model": settings.default_model,
        "models": [spec.name for spec in model_specs()],
        "guardrails": settings.guardrails_enabled,
    }


@app.get("/metrics", include_in_schema=False)
async def metrics(request: Request) -> Response:
    """Prometheus metrics. Protected by METRICS_TOKEN when that is set."""
    if settings.metrics_token:
        expected = f"Bearer {settings.metrics_token}"
        given = request.headers.get("authorization", "")
        if not hmac.compare_digest(given.encode(), expected.encode()):
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


# Serve React build
build_dir = Path(__file__).parent.parent / "static" / "build"
if build_dir.exists():
    app.mount("/", StaticFiles(directory=str(build_dir), html=True), name="static")
    logger.info(f"React app served from {build_dir}")
else:

    @app.get("/")
    async def no_build() -> dict[str, str]:
        return {"error": "React build missing. Run: cd static && npm run build"}


# Local dev only
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
