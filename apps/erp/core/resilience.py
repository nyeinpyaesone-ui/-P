"""
Circuit Breaker and Retry Mechanism Utilities.
Implements resilience patterns to handle transient failures in external services (DB, Redis, RabbitMQ).
"""
import asyncio
import time
import logging
from enum import Enum
from typing import Callable, Any, Optional, Tuple
from functools import wraps

logger = logging.getLogger("erp.core.resilience")


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, stop requests
    HALF_OPEN = "half_open" # Testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when the circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern.
    
    - **Closed**: Requests go through. If failures exceed threshold, opens circuit.
    - **Open**: Requests fail immediately. After timeout, moves to Half-Open.
    - **Half-Open**: Allows one test request. If success -> Closed, else -> Open.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 1,
        name: str = "default"
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_successes = 0
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executes the function wrapped by the circuit breaker logic.
        """
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    logger.info(f"Circuit {self.name} moving from OPEN to HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_successes = 0
                else:
                    raise CircuitBreakerError(f"Circuit {self.name} is OPEN. Try again later.")

        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            await self._on_success()
            return result
            
        except Exception as e:
            await self._on_failure()
            raise e

    async def _on_success(self):
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_successes += 1
                if self.half_open_successes >= self.half_open_max_calls:
                    logger.info(f"Circuit {self.name} moving from HALF_OPEN to CLOSED")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0

    async def _on_failure(self):
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                logger.warning(f"Circuit {self.name} failed in HALF_OPEN, returning to OPEN")
                self.state = CircuitState.OPEN
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.failure_threshold:
                    logger.warning(f"Circuit {self.name} moving from CLOSED to OPEN (failures: {self.failure_count})")
                    self.state = CircuitState.OPEN

    def __call__(self, func: Callable) -> Callable:
        """Decorator usage: @circuit_breaker"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        return wrapper


class RetryConfig:
    """Configuration for retry logic."""
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        exceptions_to_retry: Tuple = (Exception,)
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.exceptions_to_retry = exceptions_to_retry


async def retry_async(
    func: Callable,
    *args,
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
    **kwargs
) -> Any:
    """
    Executes an async function with exponential backoff retry logic.
    
    Args:
        func: The async function to execute.
        config: RetryConfig instance. Defaults are used if None.
        on_retry: Optional callback(retry_count, exception, delay) called before each retry.
    """
    if config is None:
        config = RetryConfig()
        
    last_exception = None
    delay = config.base_delay
    
    for attempt in range(config.max_retries + 1):
        try:
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        except config.exceptions_to_retry as e:
            last_exception = e
            
            if attempt == config.max_retries:
                break
                
            if on_retry:
                on_retry(attempt, e, delay)
                
            logger.warning(f"Retry {attempt + 1}/{config.max_retries} after {delay:.2f}s due to: {e}")
            
            await asyncio.sleep(delay)
            
            # Exponential backoff with optional jitter
            delay = min(delay * config.exponential_base, config.max_delay)
            if config.jitter:
                import random
                delay += random.uniform(0, 0.1 * delay)
    
    logger.error(f"All retries exhausted for {func.__name__}")
    raise last_exception


def retry_decorator(config: Optional[RetryConfig] = None):
    """Decorator for adding retry logic to async functions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_async(func, *args, config=config, **kwargs)
        return wrapper
    return decorator
