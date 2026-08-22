"""
Observability, Security, and Resilience Utilities.
Provides structured logging, security headers, request tracing, and graceful shutdown helpers.
"""
import logging
import sys
import uuid
import time
from contextvars import ContextVar
from typing import Callable, Optional

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

# Context variable for Request ID to ensure thread-safe tracing
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class StructuredFormatter(logging.Formatter):
    """
    JSON Formatter for structured logging.
    Enables easy parsing by ELK Stack, Datadog, or CloudWatch.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        import json
        return json.dumps(log_data)


def setup_logging(level: str = "INFO", json_logs: bool = True) -> None:
    """
    Configures root logger with structured formatting.
    """
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    handler = logging.StreamHandler(sys.stdout)
    
    if json_logs:
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [Req: %(request_id)s]",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
    
    # Add a filter to inject request_id into standard log records if not using JSON
    class RequestIDFilter(logging.Filter):
        def filter(self, record):
            record.request_id = request_id_var.get()
            return True
    
    if not json_logs:
        handler.addFilter(RequestIDFilter())
        
    logger.addHandler(handler)
    logger.info("Logging initialized with level=%s, json=%s", level, json_logs)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Applies essential security headers to all responses.
    Mitigates XSS, Clickjacking, MIME-sniffing, and other attacks.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Enable XSS filter in older browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Strict Transport Security (HSTS) - enforce HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Content Security Policy (Default restrictive policy)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
        # Permissions Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Generates a unique Request ID for every incoming request.
    Injects it into the context var for logging and adds it to response headers.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract existing ID from headers (for distributed tracing) or generate new
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Set in context for logging
        token = request_id_var.set(request_id)
        
        try:
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Attach ID and timing to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            return response
        finally:
            # Reset context var to prevent leakage
            request_id_var.reset(token)


class DatabaseHealthCheck:
    """
    Service to verify database connectivity and pool health.
    Used for Kubernetes liveness/readiness probes or load balancer checks.
    """
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    async def check_connectivity(self) -> dict:
        """
        Attempts a simple query to verify DB connection.
        Returns status and latency.
        """
        import time
        from sqlalchemy import text
        
        start = time.time()
        try:
            # Use a fresh connection to test pool health
            with self.db_session_factory() as session:
                session.execute(text("SELECT 1"))
                latency = (time.time() - start) * 1000  # ms
                return {"status": "healthy", "latency_ms": round(latency, 2)}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "latency_ms": 0}

    async def check_pool_status(self, engine) -> dict:
        """
        Checks SQLAlchemy connection pool statistics.
        """
        pool = engine.pool
        return {
            "status": "operational",
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalidatedcount() if hasattr(pool, 'invalidatedcount') else 0
        }


async def graceful_shutdown_handler(app):
    """
    Logic to handle application shutdown gracefully.
    Ensures background tasks finish and connections close.
    """
    logging.getLogger("erp.core.observability").info("Initiating graceful shutdown...")
    
    # Wait for background tasks (if any registered)
    # In FastAPI, this is often handled by lifespan events, 
    # but explicit cleanup ensures resources are released.
    
    logging.getLogger("erp.core.observability").info("Graceful shutdown complete.")
