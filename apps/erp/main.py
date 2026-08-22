"""
ERP03 v1.0.0 - Main Application Entry Point
Modular Monolith Architecture with Event-Driven Capabilities
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import os
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://erp:erp@postgres:5432/erp_core"
)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Import module routers
try:
    from apps.erp.modules.finance.router import router as finance_router
    from apps.erp.modules.hcm.router import router as hcm_router
    from apps.erp.modules.scm.router import router as scm_router
    from apps.erp.modules.mfg.router import router as mfg_router
    from apps.erp.modules.crm.router import router as crm_router
    MODULES_LOADED = True
    logger.info("All ERP modules loaded successfully")
except ImportError as e:
    MODULES_LOADED = False
    logger.error(f"Failed to load ERP modules: {e}")


async def get_db_session():
    """
    Provide a database session for request-scoped operations.
    
    Yields:
        AsyncSession: The active database session.
    
    The session is committed after successful use, rolled back when an exception
    occurs, and closed afterward.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown resources.
    
    Parameters:
    	app (FastAPI): The application instance whose lifespan is being managed.
    """
    # Startup: Initialize DB connections and verify connectivity
    logger.info("Starting ERP03 application...")
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection established")
    except Exception as e:
        logger.warning(f"Database not yet available: {e}")
    yield
    # Shutdown: Close DB connections
    logger.info("Shutting down ERP03 application...")
    await engine.dispose()


app = FastAPI(
    title="ERP03 Enterprise System",
    version="1.0.0",
    description="Core ERP modules: Finance, HCM, SCM, Manufacturing, CRM",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration - Restrictive defaults for security
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
allowed_methods = os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,PATCH").split(",")
allowed_headers = os.getenv("ALLOWED_HEADERS", "Content-Type,Authorization").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Format request validation failures as a structured HTTP 422 response.
    
    Parameters:
        exc (RequestValidationError): The validation failure containing error details and the request body.
    
    Returns:
        JSONResponse: A response containing the validation error details and request body.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "detail": exc.errors(),
            "body": exc.body
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle an unhandled application exception with a generic error response.
    
    Returns:
        JSONResponse: An HTTP 500 response containing a generic internal error message.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_error",
            "detail": "An unexpected error occurred"
        }
    )


# Register Modules if available
if MODULES_LOADED:
    app.include_router(finance_router, prefix="/api/v1/finance", tags=["Finance"])
    app.include_router(hcm_router, prefix="/api/v1/hcm", tags=["HCM"])
    app.include_router(scm_router, prefix="/api/v1/scm", tags=["SCM"])
    app.include_router(mfg_router, prefix="/api/v1/mfg", tags=["Manufacturing"])
    app.include_router(crm_router, prefix="/api/v1/crm", tags=["CRM"])


@app.get("/healthz")
async def health_check():
    """
    Report the availability of the application and its external dependencies.
    
    Returns:
        JSONResponse: A health report with application metadata and the status of
            the database, Redis, and RabbitMQ. Uses HTTP 200 when all checks
            succeed and HTTP 503 when any dependency is unavailable.
    """
    health_status = {
        "status": "ok",
        "version": "1.0.0",
        "modules": MODULES_LOADED,
        "db": "unknown",
        "redis": "unknown",
        "rabbitmq": "unknown"
    }
    
    # Check database connectivity
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        health_status["db"] = "connected"
    except Exception as e:
        health_status["db"] = f"disconnected: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis connectivity
    try:
        import redis.asyncio as redis
        redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))
        await redis_client.ping()
        health_status["redis"] = "connected"
        await redis_client.close()
    except Exception as e:
        health_status["redis"] = f"disconnected: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check RabbitMQ connectivity
    try:
        import aio_pika
        rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://erp:erp@rabbitmq:5672//")
        connection = await aio_pika.connect_robust(rabbitmq_url)
        await connection.close()
        health_status["rabbitmq"] = "connected"
    except Exception as e:
        health_status["rabbitmq"] = f"disconnected: {str(e)}"
        health_status["status"] = "degraded"
    
    status_code = 200 if health_status["status"] == "ok" else 503
    return JSONResponse(status_code=status_code, content=health_status)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "ERP03 Enterprise System",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/healthz"
    }
