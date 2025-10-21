"""
Custom exceptions for the application
"""

from typing import Optional, Dict, Any


class CustomException(Exception):
    """Base custom exception class."""
    
    def __init__(
        self,
        status_code: int,
        error_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(CustomException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=400,
            error_type="validation_error",
            message=message,
            details=details
        )


class AuthenticationException(CustomException):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=401,
            error_type="authentication_error",
            message=message,
            details=details
        )


class AuthorizationException(CustomException):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=403,
            error_type="authorization_error",
            message=message,
            details=details
        )


class NotFoundException(CustomException):
    """Exception for resource not found errors."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=404,
            error_type="not_found_error",
            message=message,
            details=details
        )


class ServiceException(CustomException):
    """Exception for external service errors."""
    
    def __init__(self, message: str, service_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=503,
            error_type="service_error",
            message=f"{service_name}: {message}",
            details=details
        )


class RateLimitException(CustomException):
    """Exception for rate limit errors."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=429,
            error_type="rate_limit_error",
            message=message,
            details=details
        )