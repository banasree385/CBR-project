"""
FastAPI Main Application Entry Point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import structlog
from contextlib import asynccontextmanager
import os

from app.config_simple import get_settings
from app.api import chat, agent
from app.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = structlog.get_logger()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting AI Foundry Agent Backend", version=settings.app_version)
    
    # Initialize services
    try:
        # Initialize Azure Agent Service
        from app.services.azure_agent_service import SimpleAzureAgentService
        
        azure_agent_service = SimpleAzureAgentService()
        
        # Verify Azure Agent Service connection
        await azure_agent_service.verify_connection()
        
        logger.info("Services initialized successfully - Azure Agent Service ready for testing")
        
    except Exception as e:
        logger.error("Failed to initialize services", error=str(e))
        # Don't raise exception - continue with mock mode for testing
        logger.warning("Continuing in mock mode for testing purposes")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Foundry Agent Backend")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Azure AI Foundry Agent with GPT-4 Integration",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.api_v1_str}/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "timestamp": "2025-10-21T17:00:00Z"
    }

# Simple test endpoint for API connectivity
@app.get("/api/test")
async def api_test():
    """Simple API test endpoint."""
    return {
        "status": "success",
        "message": "API is working correctly",
        "timestamp": "2025-10-23T19:16:00Z"
    }

# Root endpoint for API info (only when accessing /api)
@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "message": "Azure AI Foundry Agent Backend",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "api": f"{settings.api_v1_str}"
    }

# Include API routers BEFORE static files
app.include_router(
    chat.router,
    prefix=f"{settings.api_v1_str}/chat",
    tags=["chat"]
)

app.include_router(
    agent.router,
    prefix=f"{settings.api_v1_str}/agent",
    tags=["agent"]
)

# Mount static files AFTER API routes
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    # Serve HTML files directly from root
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")

# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An internal server error occurred"
        }
    )

# Development server
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )