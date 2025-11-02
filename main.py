"""
Local development entry point.
For production (Vercel), use api/index.py instead.
"""
from app.main import app

if __name__ == "__main__":
    import uvicorn
    print("🦢 Starting Swan AI Quote Generator (Local Development)")
    print("=" * 60)
    print("Backend API: http://localhost:8000/api")
    print("Frontend:    http://localhost:8000")
    print("Docs:        http://localhost:8000/docs")
    print("Health:      http://localhost:8000/health")
    print("=" * 60)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
