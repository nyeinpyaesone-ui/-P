"""
ERP Core Module.
Provides foundational utilities for observability, resilience, and service management.
"""

from .observability import (
    setup_logging,
    StructuredFormatter,
    SecurityHeadersMiddleware,
    RequestIDMiddleware,
    DatabaseHealthCheck,
    graceful_shutdown_handler,
)

from .resilience import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitState,
    RetryConfig,
    retry_async,
    retry_decorator,
)

from .services import (
    ServiceRegistry,
    ServiceStatus,
    service_registry,
    create_db_health_checker,
    create_redis_health_checker,
    create_rabbitmq_health_checker,
)

__all__ = [
    # Observability
    "setup_logging",
    "StructuredFormatter",
    "SecurityHeadersMiddleware",
    "RequestIDMiddleware",
    "DatabaseHealthCheck",
    "graceful_shutdown_handler",
    # Resilience
    "CircuitBreaker",
    "CircuitBreakerError",
    "CircuitState",
    "RetryConfig",
    "retry_async",
    "retry_decorator",
    # Services
    "ServiceRegistry",
    "ServiceStatus",
    "service_registry",
    "create_db_health_checker",
    "create_redis_health_checker",
    "create_rabbitmq_health_checker",
]