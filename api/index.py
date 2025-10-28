"""
Vercel serverless function entry point for AI Quote Generator.
This file is the serverless handler that Vercel will invoke.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
import sys
import os
from pathlib import Path
import logging

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.api.routes.quote_routes import router as quote_router

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
    description="An AI-powered quote generator API built with FastAPI",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error for {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(quote_router)

# Mount static files for the React app
static_dir = Path(__file__).parent.parent / "app" / "static" / "build"
logger.info(f"Looking for static files at: {static_dir}")

try:
    if static_dir.exists():
        logger.info("Static directory found, mounting static files")
        # Mount the static folder for JS/CSS files
        static_assets = static_dir / "static"
        if static_assets.exists():
            logger.info(f"Mounting /static from {static_assets}")
            app.mount("/static", StaticFiles(directory=str(static_assets)), name="static")
        
        # Mount the img folder for images
        img_dir = static_dir / "img"
        if img_dir.exists():
            logger.info(f"Mounting /img from {img_dir}")
            app.mount("/img", StaticFiles(directory=str(img_dir)), name="img")
    else:
        logger.warning(f"Static directory not found at {static_dir}")
except Exception as e:
    logger.error(f"Error mounting static files: {e}")

@app.get("/test", tags=["test"])
async def test_endpoint():
    """Simple test endpoint to verify deployment."""
    return {"status": "working", "message": "Vercel deployment successful!"}

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
    logger.info(f"Attempting to serve: {full_path} from {index_file}")
    
    if index_file.exists():
        return FileResponse(index_file)
    
    logger.warning(f"index.html not found at {index_file}")
    return JSONResponse(
        status_code=404,
        content={
            "error": "Frontend not found. Please build the React app first.",
            "path": str(index_file),
            "exists": index_file.exists()
        }
    )

# Mangum handler for Vercel serverless
handler = Mangum(app, lifespan="off")
