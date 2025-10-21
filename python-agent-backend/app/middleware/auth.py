"""
Authentication middleware
"""

from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for API requests."""
    
    def __init__(self, app, skip_auth_paths: Optional[list] = None):
        super().__init__(app)
        self.skip_auth_paths = skip_auth_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process authentication for incoming requests."""
        
        # Skip authentication for certain paths
        if any(request.url.path.startswith(path) for path in self.skip_auth_paths):
            return await call_next(request)
        
        # For demo purposes, we'll skip authentication
        # In production, implement proper JWT or API key validation
        
        # Example authentication logic (commented out for demo):
        # auth_header = request.headers.get("authorization")
        # if not auth_header or not auth_header.startswith("Bearer "):
        #     raise HTTPException(status_code=401, detail="Missing or invalid authentication")
        
        response = await call_next(request)
        return response