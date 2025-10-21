"""
FastAPI Main Application Entry Point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import structlog
from contextlib import asynccontextmanager

from app.config_simple import get_settings
from app.api import chat, agent
from app.middleware.auth import AuthMiddleware
from app.utils.logger import setup_logging
from app.utils.exceptions import CustomException

# Setup logging
setup_logging()
logger = structlog.get_logger()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting AI Foundry Agent Backend", version=settings.app_version)
    
    # Initialize services - commented out for testing chat function only
    try:
        # Initialize only GPT service for chat testing
        from app.services.gpt_service import GPTService
        
        gpt_service = GPTService()
        
        # Comment out Azure AI service to avoid connection issues during testing
        # from app.services.azure_ai_service import AzureAIService
        # azure_service = AzureAIService()
        # await azure_service.verify_connection()
        
        # Verify GPT connection (will use mock mode if no credentials)
        await gpt_service.verify_connection()
        
        logger.info("Services initialized successfully - GPT service ready for testing")
        
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
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Authentication Middleware
app.add_middleware(AuthMiddleware)

# Exception handlers
@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc: CustomException):
    """Handle custom exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_type,
            "message": exc.message,
            "details": exc.details
        }
    )

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

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Azure AI Foundry Agent Backend",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "api": f"{settings.api_v1_str}"
    }

# Include API routers
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


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )