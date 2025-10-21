"""
Logging configuration and utilities
"""

import logging
import sys
from typing import Any, Dict
import structlog
from structlog.stdlib import LoggerFactory


def setup_logging(log_level: str = "INFO") -> None:
    """Set up structured logging with structlog."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            # Add timestamp
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # JSON formatting for production
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    
    # Set log levels for external libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class RequestLogger:
    """Logger for HTTP requests."""
    
    def __init__(self):
        self.logger = get_logger("request")
    
    async def log_request(self, request: Any, response: Any, process_time: float):
        """Log HTTP request details."""
        self.logger.info(
            "HTTP request processed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time_ms=round(process_time * 1000, 2),
            user_agent=request.headers.get("user-agent", "unknown"),
            client_ip=request.client.host if request.client else "unknown"
        )


class ServiceLogger:
    """Logger for service operations."""
    
    def __init__(self, service_name: str):
        self.logger = get_logger(service_name)
        self.service_name = service_name
    
    def log_operation(
        self,
        operation: str,
        success: bool,
        duration_ms: float = None,
        details: Dict[str, Any] = None
    ):
        """Log service operation."""
        log_data = {
            "service": self.service_name,
            "operation": operation,
            "success": success
        }
        
        if duration_ms is not None:
            log_data["duration_ms"] = round(duration_ms, 2)
        
        if details:
            log_data.update(details)
        
        if success:
            self.logger.info("Service operation completed", **log_data)
        else:
            self.logger.error("Service operation failed", **log_data)
    
    def log_error(self, operation: str, error: Exception, details: Dict[str, Any] = None):
        """Log service error."""
        log_data = {
            "service": self.service_name,
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        if details:
            log_data.update(details)
        
        self.logger.error("Service error occurred", **log_data)


class ChatLogger:
    """Logger for chat operations."""
    
    def __init__(self):
        self.logger = get_logger("chat")
    
    def log_message(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        tokens_used: int = None,
        response_time_ms: float = None
    ):
        """Log chat message exchange."""
        self.logger.info(
            "Chat message processed",
            session_id=session_id,
            user_message_length=len(user_message),
            assistant_response_length=len(assistant_response),
            tokens_used=tokens_used,
            response_time_ms=response_time_ms
        )
    
    def log_session_event(self, session_id: str, event: str, details: Dict[str, Any] = None):
        """Log chat session events."""
        log_data = {
            "session_id": session_id,
            "event": event
        }
        
        if details:
            log_data.update(details)
        
        self.logger.info("Chat session event", **log_data)


class SecurityLogger:
    """Logger for security events."""
    
    def __init__(self):
        self.logger = get_logger("security")
    
    def log_auth_attempt(
        self,
        success: bool,
        user_id: str = None,
        client_ip: str = None,
        user_agent: str = None,
        details: Dict[str, Any] = None
    ):
        """Log authentication attempts."""
        log_data = {
            "event": "authentication_attempt",
            "success": success,
            "user_id": user_id,
            "client_ip": client_ip,
            "user_agent": user_agent
        }
        
        if details:
            log_data.update(details)
        
        if success:
            self.logger.info("Authentication successful", **log_data)
        else:
            self.logger.warning("Authentication failed", **log_data)
    
    def log_rate_limit(self, client_ip: str, endpoint: str, limit: int):
        """Log rate limit violations."""
        self.logger.warning(
            "Rate limit exceeded",
            event="rate_limit_exceeded",
            client_ip=client_ip,
            endpoint=endpoint,
            limit=limit
        )
    
    def log_suspicious_activity(self, description: str, details: Dict[str, Any] = None):
        """Log suspicious activities."""
        log_data = {
            "event": "suspicious_activity",
            "description": description
        }
        
        if details:
            log_data.update(details)
        
        self.logger.warning("Suspicious activity detected", **log_data)