"""
Main application entry point for the AI Quote Generator.
Optimized for Vercel serverless deployment.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.api.routes import quote_router
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Quote Generator powered by Google Gemini",
    docs_url="/docs" if settings.debug else None,
    redoc_url=None
)

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error for {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

# Configure CORS - Allow all origins for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(quote_router)

# Serve React build from static/build/ directory (at project root)
# Path goes up from app/ to project root, then to static/build
build_dir = Path(__file__).parent.parent / "static" / "build"
if build_dir.exists():
    # Mount static assets (JS, CSS, etc.)
    static_assets_dir = build_dir / "static"
    if static_assets_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_assets_dir)), name="static-assets")
    
    # Mount images directory if it exists
    img_dir = build_dir / "img"
    if img_dir.exists():
        app.mount("/img", StaticFiles(directory=str(img_dir)), name="images")
    
    logger.info(f"✓ React app configured from {build_dir}")
else:
    logger.warning(f"⚠ React build not found at {build_dir}. Run 'npm run build' in static/ directory.")


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "model": settings.default_model
    }


# Catch-all route to serve React SPA (must be last)
@app.get("/{full_path:path}", tags=["frontend"])
async def serve_react_app(full_path: str):
    """Serve the React single-page application."""
    build_dir_local = Path(__file__).parent.parent / "static" / "build"
    index_file = build_dir_local / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse(
        status_code=404,
        content={"error": "Frontend not found. Build the React app: cd static && npm run build"}
    )


# Local development server (not used on Vercel)
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting local development server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
