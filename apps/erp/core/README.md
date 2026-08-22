# Core Utilities for ERP System

This directory contains foundational utilities for production-ready enterprise applications:

## 📁 Modules

### `observability.py` - Logging & Request Tracing
- **Structured Logging**: JSON-formatted logs for ELK/Datadog integration
- **Request ID Middleware**: Automatic request tracing with UUID injection
- **Security Headers Middleware**: XSS, Clickjacking, MIME-sniffing protection
- **Database Health Check**: Connection pool monitoring

**Usage:**
```python
from apps.erp.core import setup_logging, RequestIDMiddleware, SecurityHeadersMiddleware

# Initialize logging
setup_logging(level="INFO", json_logs=True)

# Add to FastAPI app
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
```

### `resilience.py` - Fault Tolerance Patterns
- **Circuit Breaker**: Prevents cascading failures in external services
- **Retry with Exponential Backoff**: Handles transient failures gracefully
- **Configurable thresholds**: Customize failure counts and timeouts

**Usage:**
```python
from apps.erp.core import CircuitBreaker, retry_async, RetryConfig

# Circuit Breaker
db_breaker = CircuitBreaker(name="database", failure_threshold=5)

@db_breaker
async def query_db():
    return await db.execute(query)

# Retry Logic
config = RetryConfig(max_retries=3, base_delay=1.0)
result = await retry_async(api_call, config=config)
```

### `services.py` - Service Registry & Health Aggregation
- **Centralized Service Registry**: Track DB, Redis, RabbitMQ status
- **Health Check Factories**: Pre-built checkers for common services
- **Unified Health Status**: Aggregate all service health for probes

**Usage:**
```python
from apps.erp.core import service_registry, create_db_health_checker

# Register services during startup
db_checker = await create_db_health_checker(session_factory, engine)
service_registry.register_service("postgres", db_checker)

# Check health
statuses = await service_registry.check_all_services()
is_ready = service_registry.get_critical_services_status()
```

### `api/v1/health.py` - Health Endpoints
Automatically registered in `main.py`:

| Endpoint | Purpose | HTTP Codes |
|----------|---------|------------|
| `GET /api/v1/live` | Liveness probe (is app running?) | 200 |
| `GET /api/v1/ready` | Readiness probe (are deps ready?) | 200 / 503 |
| `GET /api/v1/health` | Full health report (all services) | 200 / 503 |
| `GET /api/v1/health/{service}` | Specific service status | 200 / 404 / 503 |

## 🔧 Integration in main.py

The utilities are automatically integrated:

```python
from apps.erp.core import (
    setup_logging,
    SecurityHeadersMiddleware,
    RequestIDMiddleware,
    service_registry,
)

# Logging initialized
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"), json_logs=True)

# Middlewares added
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Health endpoints registered
from apps.erp.api.v1.health import router as health_router
app.include_router(health_router, prefix="/api/v1")
```

## 🛡️ Security Features

All responses now include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy: default-src 'self'`
- `Referrer-Policy: strict-origin-when-cross-origin`

## 📊 Kubernetes Probe Configuration

```yaml
livenessProbe:
  httpGet:
    path: /api/v1/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /api/v1/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 3
```

## 🎯 Best Practices

1. **Always use circuit breakers** for external service calls (DB, Redis, APIs)
2. **Configure retry limits** to prevent infinite loops
3. **Monitor circuit breaker state** via logs (CLOSED → OPEN → HALF_OPEN)
4. **Use structured logging** in production for better observability
5. **Never skip health checks** - they're critical for auto-scaling and failover
