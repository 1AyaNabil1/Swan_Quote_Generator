"""
Vercel serverless entry point for FastAPI backend.
This file wraps the FastAPI app with Mangum to handle AWS Lambda/Vercel requests.
"""

from mangum import Mangum

from app.main import app


# Mangum handler converts ASGI (FastAPI) to AWS Lambda/Vercel format
handler = Mangum(app, lifespan="auto")
