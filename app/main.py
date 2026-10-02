"""
Main application entry point for the AI Quote Generator.
Serves the API and the built React frontend from one process.
"""

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import quote_router
from app.config import settings


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
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
async def validation_exception_handler(request: Request, exc: RequestValidationError):
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

# Include API routers
app.include_router(quote_router)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "version": settings.app_version, "model": settings.default_model}


# Serve React build
build_dir = Path(__file__).parent.parent / "static" / "build"
if build_dir.exists():
    app.mount("/", StaticFiles(directory=str(build_dir), html=True), name="static")
    logger.info(f"React app served from {build_dir}")
else:

    @app.get("/")
    async def no_build():
        return {"error": "React build missing. Run: cd static && npm run build"}


# Local dev only
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
