"""
Main application entry point for the AI Quote Generator.
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
    level=logging.INFO,  # Changed back to INFO for production
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="An AI-powered quote generator API built with FastAPI",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error for {request.url}: {exc.errors()}")
    logger.error(f"Request body: {await request.body()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(quote_router)

# Mount static files for the React app
static_dir = Path(__file__).parent / "app" / "static" / "build"
if static_dir.exists():
    # Mount the static folder for JS/CSS files
    app.mount("/static", StaticFiles(directory=str(static_dir / "static")), name="static")
    # Mount the img folder for images
    img_dir = static_dir / "img"
    if img_dir.exists():
        app.mount("/img", StaticFiles(directory=str(img_dir)), name="img")


@app.get("/api", tags=["root"])
async def api_root():
    """API root endpoint returning API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version
    }


# Serve the React app for all other routes (catch-all for SPA routing)
@app.get("/{full_path:path}", tags=["frontend"])
async def serve_react_app(full_path: str):
    """Serve the React application."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"error": "Frontend not found. Please build the React app first."}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
