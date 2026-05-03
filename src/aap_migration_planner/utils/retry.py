"""Retry decorator for API calls with exponential backoff.

This module provides retry logic for transient failures in API communication.
"""

import asyncio
import functools
from collections.abc import Callable
from typing import Any, TypeVar

from aap_migration_planner.client.base_client import APIError
from aap_migration_planner.utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

# HTTP status codes that should trigger retry
RETRYABLE_STATUS_CODES = {
    429,  # Too Many Requests
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
}


def retry_api_call(
    func: Callable[..., T] = None,
    *,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
) -> Callable[..., T] | Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to retry API calls with exponential backoff.

    Retries on network errors and specific HTTP status codes (429, 500, 502, 503, 504).

    Can be used with or without arguments:
        @retry_api_call
        async def fetch_data(self):
            return await self.client.get("/api/data")

        @retry_api_call(max_retries=5, base_delay=2.0)
        async def fetch_data(self):
            return await self.client.get("/api/data")

    Args:
        func: The function to decorate (when used without arguments)
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation

    Returns:
        Decorated function with retry logic
    """

    def decorator(f: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(f)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    # Try the API call
                    result = await f(*args, **kwargs)

                    # If we retried and succeeded, log it
                    if attempt > 0:
                        logger.info(
                            "retry_succeeded",
                            function=f.__name__,
                            attempt=attempt + 1,
                            max_retries=max_retries,
                        )

                    return result

                except APIError as e:
                    last_exception = e

                    # Check if error is retryable
                    is_retryable = (
                        e.status_code in RETRYABLE_STATUS_CODES
                        if e.status_code
                        else True  # Network errors are retryable
                    )

                    if not is_retryable or attempt >= max_retries:
                        # Don't retry non-retryable errors or if max retries reached
                        logger.error(
                            "api_call_failed",
                            function=f.__name__,
                            attempt=attempt + 1,
                            status_code=e.status_code,
                            error=str(e),
                            retryable=is_retryable,
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    logger.warning(
                        "api_call_retry",
                        function=f.__name__,
                        attempt=attempt + 1,
                        max_retries=max_retries,
                        status_code=e.status_code,
                        error=str(e),
                        retry_delay=delay,
                    )

                    # Wait before retrying
                    await asyncio.sleep(delay)

                except Exception as e:
                    # Non-API errors (unexpected exceptions) - don't retry
                    logger.error(
                        "unexpected_error",
                        function=f.__name__,
                        attempt=attempt + 1,
                        error=str(e),
                        error_type=type(e).__name__,
                    )
                    raise

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Retry logic failed for {f.__name__}")

        return wrapper

    # Handle both @retry_api_call and @retry_api_call()
    if func is not None:
        # Called without arguments: @retry_api_call
        return decorator(func)
    else:
        # Called with arguments: @retry_api_call(max_retries=5)
        return decorator
