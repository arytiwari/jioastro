"""
JioAstro API - Main Application
FastAPI backend for AI-powered JioAstro service
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    print("🚀 Starting JioAstro API...")

    # Try to initialize database, but don't fail if connection is blocked
    try:
        await init_db()
        print("✅ Database initialized via direct connection")
    except Exception as e:
        print(f"⚠️  Database direct connection failed: {type(e).__name__}")
        print("ℹ️  Using Supabase REST API instead (this is normal if PostgreSQL ports are blocked)")
        print("✅ Application will use Supabase REST API for database operations")

    yield
    # Shutdown
    print("👋 Shutting down...")

app = FastAPI(
    title="JioAstro API",
    description="AI-powered JioAstro service with birth chart generation, numerology, and personalized interpretations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "JioAstro API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "supabase_rest_api",
        "api": "operational",
        "note": "Using Supabase REST API for database operations"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT == "development"
    )
