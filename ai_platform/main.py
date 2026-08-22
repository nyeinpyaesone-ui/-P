"""
AI Platform Main Entry Point

FastAPI application for AI/ML services in ERP03.
"""
from fastapi import FastAPI
from fastapi.healthcheck import HealthCheck

app = FastAPI(
    title="ERP03 AI Platform",
    description="AI/ML services for ERP03 enterprise system",
    version="1.0.0",
)


@app.get("/healthz")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "ok", "service": "ai-platform"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "ERP03 AI Platform",
        "version": "1.0.0",
        "endpoints": {
            "health": "/healthz",
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
