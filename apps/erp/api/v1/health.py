"""
Health Check API Endpoints.
Provides /health, /ready, and /live endpoints for Kubernetes probes and load balancers.
"""
import logging
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from typing import Dict, Any

# Import from core utilities
import sys
sys.path.insert(0, '/workspace/apps/erp')
from core.services import service_registry

logger = logging.getLogger("erp.api.health")

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Overall System Health")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check of all registered services.
    Returns detailed status of each component (DB, Redis, RabbitMQ).
    
    Use for: Kubernetes Readiness Probes, Load Balancer checks
    """
    # Run fresh health checks on all services
    statuses = await service_registry.check_all_services()
    
    overall_healthy = all(s.is_healthy for s in statuses.values())
    
    response_data = {
        "status": "healthy" if overall_healthy else "unhealthy",
        "services": {
            name: {
                "healthy": svc.is_healthy,
                "latency_ms": svc.latency_ms,
                "message": svc.message,
                "details": svc.details
            }
            for name, svc in statuses.items()
        }
    }
    
    http_status = status.HTTP_200_OK if overall_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=http_status, content=response_data)


@router.get("/ready", summary="Readiness Probe")
async def readiness_probe() -> Dict[str, Any]:
    """
    Checks if the application is ready to accept traffic.
    Verifies critical dependencies (Database, Message Queue).
    
    Returns 200 if ready, 503 if not.
    Use for: Kubernetes Readiness Probe
    """
    # Check cached statuses or run fresh checks
    if not service_registry.get_all_statuses():
        await service_registry.check_all_services()
    
    is_ready = service_registry.get_critical_services_status()
    
    if is_ready:
        return {"status": "ready", "message": "Application is ready to serve requests"}
    else:
        logger.warning("Readiness check failed: critical services unavailable")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "message": "Critical services unavailable"}
        )


@router.get("/live", summary="Liveness Probe")
async def liveness_probe() -> Dict[str, str]:
    """
    Simple liveness check.
    Returns 200 as long as the application process is running.
    
    Does NOT check dependencies - only verifies the app hasn't crashed.
    Use for: Kubernetes Liveness Probe
    """
    return {"status": "alive", "message": "Application is running"}


@router.get("/health/{service_name}", summary="Specific Service Health")
async def service_health(service_name: str) -> Dict[str, Any]:
    """
    Check health of a specific service by name.
    
    Available services: postgres, redis, rabbitmq
    """
    status_obj = service_registry.get_status(service_name)
    
    if not status_obj:
        # Try to run a fresh check
        await service_registry.check_health(service_name)
        status_obj = service_registry.get_status(service_name)
    
    if not status_obj:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Service '{service_name}' not found"}
        )
    
    return {
        "service": service_name,
        "healthy": status_obj.is_healthy,
        "latency_ms": status_obj.latency_ms,
        "message": status_obj.message,
        "last_checked": status_obj.last_checked.isoformat(),
        "details": status_obj.details
    }
