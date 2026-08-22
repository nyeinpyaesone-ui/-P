"""
Centralized Service Registry and Health Aggregator.
Registers core services (DB, Redis, RabbitMQ) and provides unified health status.
"""
import logging
from typing import Dict, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

logger = logging.getLogger("erp.core.services")


@dataclass
class ServiceStatus:
    """Represents the health status of a single service."""
    name: str
    is_healthy: bool
    latency_ms: float = 0.0
    message: str = ""
    last_checked: datetime = field(default_factory=datetime.utcnow)
    details: dict = field(default_factory=dict)


class ServiceRegistry:
    """
    Central registry for application services.
    Manages lifecycle, health checks, and dependency injection.
    """
    
    def __init__(self):
        self._services: Dict[str, ServiceStatus] = {}
        self._health_check_funcs: Dict[str, Callable[[], Awaitable[ServiceStatus]]] = {}
        self._lock = asyncio.Lock()

    def register_service(
        self, 
        name: str, 
        health_check_func: Optional[Callable[[], Awaitable[ServiceStatus]]] = None,
        initial_status: Optional[ServiceStatus] = None
    ):
        """
        Registers a service with an optional health check function.
        
        Args:
            name: Unique service identifier (e.g., "postgres", "redis", "rabbitmq")
            health_check_func: Async function that returns ServiceStatus
            initial_status: Initial status if known (defaults to unknown)
        """
        if initial_status is None:
            initial_status = ServiceStatus(
                name=name,
                is_healthy=False,
                message="Status unknown - awaiting first health check"
            )
            
        self._services[name] = initial_status
        
        if health_check_func:
            self._health_check_funcs[name] = health_check_func
            
        logger.info(f"Service registered: {name}")

    async def check_health(self, service_name: str) -> ServiceStatus:
        """
        Executes the health check for a specific service and updates its status.
        """
        if service_name not in self._health_check_funcs:
            return self._services.get(
                service_name, 
                ServiceStatus(name=service_name, is_healthy=False, message="Service not found")
            )
        
        try:
            status = await self._health_check_funcs[service_name]()
            status.last_checked = datetime.utcnow()
            
            async with self._lock:
                self._services[service_name] = status
                
            return status
            
        except Exception as e:
            error_status = ServiceStatus(
                name=service_name,
                is_healthy=False,
                message=f"Health check failed: {str(e)}",
                last_checked=datetime.utcnow()
            )
            async with self._lock:
                self._services[service_name] = error_status
            return error_status

    async def check_all_services(self) -> Dict[str, ServiceStatus]:
        """
        Runs health checks for all registered services concurrently.
        Returns a dictionary of service statuses.
        """
        tasks = [self.check_health(name) for name in self._health_check_funcs.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        status_dict = {}
        for result in results:
            if isinstance(result, Exception):
                # Should be handled inside check_health, but safety net here
                continue
            else:
                status_dict[result.name] = result
                
        return status_dict

    def get_status(self, service_name: str) -> Optional[ServiceStatus]:
        """Gets the current cached status of a service."""
        return self._services.get(service_name)

    def get_all_statuses(self) -> Dict[str, ServiceStatus]:
        """Gets current cached statuses for all services."""
        return self._services.copy()

    def is_system_healthy(self) -> bool:
        """
        Returns True only if ALL registered services are healthy.
        Useful for Kubernetes readiness probes.
        """
        if not self._services:
            return False
        return all(s.is_healthy for s in self._services.values())

    def get_critical_services_status(self) -> bool:
        """
        Returns True if critical services (DB, Message Queue) are healthy.
        Allows non-critical services (e.g., analytics) to fail without marking system down.
        """
        critical_services = ["postgres", "rabbitmq"]  # Define critical list
        for svc in critical_services:
            if svc in self._services and not self._services[svc].is_healthy:
                return False
        return True


# Global instance for easy import
service_registry = ServiceRegistry()


async def create_db_health_checker(db_session_factory, engine) -> Callable[[], Awaitable[ServiceStatus]]:
    """Factory to create a database health check function bound to the registry."""
    from .observability import DatabaseHealthCheck
    
    db_checker = DatabaseHealthCheck(db_session_factory)
    
    async def check() -> ServiceStatus:
        conn_result = await db_checker.check_connectivity()
        pool_result = await db_checker.check_pool_status(engine)
        
        is_healthy = conn_result["status"] == "healthy"
        message = conn_result.get("error", "Database operational") if not is_healthy else "Database operational"
        
        return ServiceStatus(
            name="postgres",
            is_healthy=is_healthy,
            latency_ms=conn_result.get("latency_ms", 0),
            message=message,
            details={
                "connection": conn_result,
                "pool": pool_result
            }
        )
    
    return check


async def create_redis_health_checker(redis_client) -> Callable[[], Awaitable[ServiceStatus]]:
    """Factory to create a Redis health check function."""
    async def check() -> ServiceStatus:
        import time
        try:
            start = time.time()
            await redis_client.ping()
            latency = (time.time() - start) * 1000
            
            info = await redis_client.info("server")
            return ServiceStatus(
                name="redis",
                is_healthy=True,
                latency_ms=round(latency, 2),
                message="Redis operational",
                details={"version": info.get("redis_version", "unknown")}
            )
        except Exception as e:
            return ServiceStatus(
                name="redis",
                is_healthy=False,
                message=f"Redis connection failed: {str(e)}"
            )
    
    return check


async def create_rabbitmq_health_checker(rabbit_connection) -> Callable[[], Awaitable[ServiceStatus]]:
    """Factory to create a RabbitMQ health check function."""
    async def check() -> ServiceStatus:
        import time
        try:
            start = time.time()
            # Check if connection is open
            if rabbit_connection.is_closed:
                raise Exception("Connection closed")
                
            latency = (time.time() - start) * 1000
            
            return ServiceStatus(
                name="rabbitmq",
                is_healthy=True,
                latency_ms=round(latency, 2),
                message="RabbitMQ connection active",
                details={"open": not rabbit_connection.is_closed}
            )
        except Exception as e:
            return ServiceStatus(
                name="rabbitmq",
                is_healthy=False,
                message=f"RabbitMQ connection failed: {str(e)}"
            )
    
    return check
