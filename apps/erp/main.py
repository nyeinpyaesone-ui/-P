"""
ERP Backend Main Entry Point

FastAPI application for ERP03 enterprise resource planning system.
Provides health checks, API endpoints, and service integration.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

# Global connection status
connection_status = {
    "db": "pending",
    "redis": "pending",
    "rabbitmq": "pending",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup: Initialize connections
    await initialize_connections()
    yield
    # Shutdown: Clean up connections
    await cleanup_connections()


app = FastAPI(
    title="ERP03 Enterprise System",
    description="Complete ERP solution with accounting, sales, inventory, HR, CRM, warehouse, logistics, and reporting",
    version="1.0.0",
    lifespan=lifespan,
)


async def initialize_connections():
    """Initialize database and service connections on startup."""
    # Database connection check
    try:
        import psycopg2
        db_config = {
            "user": os.getenv("POSTGRES_USER", "erp"),
            "password": os.getenv("POSTGRES_PASSWORD", "erp_secure_password_change_me"),
            "host": os.getenv("POSTGRES_HOST", "postgres"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DB", "erp_core"),
        }
        conn = psycopg2.connect(**db_config, connect_timeout=5)
        conn.close()
        connection_status["db"] = "connected"
    except Exception as e:
        connection_status["db"] = f"failed: {str(e)}"

    # Redis connection check
    try:
        import redis
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            decode_responses=True,
            socket_connect_timeout=5,
        )
        redis_client.ping()
        connection_status["redis"] = "connected"
    except Exception as e:
        connection_status["redis"] = f"failed: {str(e)}"

    # RabbitMQ connection check
    try:
        import pika
        credentials = pika.PlainCredentials(
            os.getenv("RABBITMQ_DEFAULT_USER", "erp"),
            os.getenv("RABBITMQ_DEFAULT_PASS", "erp_secure_password_change_me"),
        )
        parameters = pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
            port=int(os.getenv("RABBITMQ_PORT", "5672")),
            credentials=credentials,
            connection_attempts=3,
            retry_delay=5,
        )
        connection = pika.BlockingConnection(parameters)
        connection.close()
        connection_status["rabbitmq"] = "connected"
    except Exception as e:
        connection_status["rabbitmq"] = f"failed: {str(e)}"


async def cleanup_connections():
    """Clean up connections on shutdown."""
    # Add cleanup logic here if needed
    pass


@app.get("/healthz")
async def health_check():
    """
    Comprehensive health check endpoint.
    Returns status of the application and all dependencies.
    """
    overall_status = "ok" if all(
        v == "connected" for v in connection_status.values()
    ) else "degraded"

    return {
        "status": overall_status,
        "service": "erp-backend",
        "version": "1.0.0",
        "dependencies": connection_status,
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "ERP03 Enterprise System",
        "version": "1.0.0",
        "description": "Complete ERP solution",
        "modules": [
            "accounting",
            "sales",
            "inventory",
            "hr",
            "crm",
            "warehouse",
            "logistics",
            "reporting",
        ],
        "endpoints": {
            "health": "/healthz",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "api": "/api/v1",
        },
    }


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint."""
    return {
        "api_version": "v1",
        "status": "operational",
        "modules_available": 8,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
