"""Base HTTP client for AAP API communication.

This module provides a base async HTTP client with rate limiting,
logging, and error handling for AAP API interactions.
"""

import asyncio
from typing import Any
from urllib.parse import urljoin

import httpx
from httpx import AsyncClient, Response

from aap_migration_planner.utils.logging import get_logger

logger = get_logger(__name__)


class APIError(Exception):
    """Exception raised for API errors."""

    def __init__(self, message: str, status_code: int | None = None, response: dict | None = None):
        """Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code if available
            response: Response data if available
        """
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class BaseAPIClient:
    """Base async HTTP client for AAP API with rate limiting and logging.

    This client provides common HTTP methods with:
    - Async/await support via httpx
    - Rate limiting using semaphore
    - Automatic token authentication
    - Request/response logging
    - Error handling and retries
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        verify_ssl: bool = True,
        timeout: int = 30,
        rate_limit: int = 20,
        log_payloads: bool = False,
        max_payload_size: int = 10000,
        max_connections: int | None = None,
        max_keepalive_connections: int | None = None,
    ):
        """Initialize base API client.

        Args:
            base_url: Base URL of the API (e.g., https://aap.example.com/api/v2/)
            token: Authentication token
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
            rate_limit: Maximum concurrent requests
            log_payloads: Enable request/response payload logging
            max_payload_size: Maximum payload size to log before truncation
            max_connections: Maximum number of connections in pool
            max_keepalive_connections: Maximum keep-alive connections
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.log_payloads = log_payloads
        self.max_payload_size = max_payload_size

        # Rate limiting
        self._rate_limiter = asyncio.Semaphore(rate_limit)

        # HTTP client configuration
        limits = httpx.Limits(
            max_connections=max_connections or 100,
            max_keepalive_connections=max_keepalive_connections or 20,
        )

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        self._client = AsyncClient(
            base_url=self.base_url,
            headers=headers,
            verify=self.verify_ssl,
            timeout=timeout,
            limits=limits,
        )

        logger.info(
            "base_client_initialized",
            base_url=self.base_url,
            verify_ssl=self.verify_ssl,
            rate_limit=rate_limit,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
        logger.debug("base_client_closed")

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            Full URL
        """
        # Remove leading slash if present
        endpoint = endpoint.lstrip("/")
        return urljoin(f"{self.base_url}/", endpoint)

    def _log_request(self, method: str, url: str, **kwargs):
        """Log outgoing request.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request parameters
        """
        log_data = {
            "method": method,
            "url": url,
        }

        if self.log_payloads and "json" in kwargs:
            payload = str(kwargs["json"])
            if len(payload) > self.max_payload_size:
                payload = payload[: self.max_payload_size] + "... (truncated)"
            log_data["request_body"] = payload

        logger.debug("http_request", **log_data)

    def _log_response(self, response: Response):
        """Log API response.

        Args:
            response: HTTP response
        """
        log_data = {
            "status_code": response.status_code,
            "url": str(response.url),
        }

        if self.log_payloads:
            try:
                payload = response.text
                if len(payload) > self.max_payload_size:
                    payload = payload[: self.max_payload_size] + "... (truncated)"
                log_data["response_body"] = payload
            except Exception:
                pass

        logger.debug("http_response", **log_data)

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make HTTP request with rate limiting and error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to httpx request

        Returns:
            Response data as dictionary

        Raises:
            APIError: If request fails
        """
        url = self._build_url(endpoint)

        async with self._rate_limiter:
            self._log_request(method, url, **kwargs)

            try:
                response = await self._client.request(method, url, **kwargs)
                self._log_response(response)

                # Raise for HTTP errors
                response.raise_for_status()

                # Parse JSON response
                return response.json()

            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP {e.response.status_code} error for {url}"
                try:
                    error_data = e.response.json()
                    error_msg += f": {error_data}"
                except Exception:
                    error_msg += f": {e.response.text}"

                logger.error(
                    "http_error",
                    status_code=e.response.status_code,
                    url=url,
                    error=error_msg,
                )
                raise APIError(
                    error_msg,
                    status_code=e.response.status_code,
                    response=e.response.json() if e.response.text else None,
                )

            except httpx.RequestError as e:
                error_msg = f"Request error for {url}: {str(e)}"
                logger.error("request_error", url=url, error=str(e))
                raise APIError(error_msg)

            except Exception as e:
                error_msg = f"Unexpected error for {url}: {str(e)}"
                logger.error("unexpected_error", url=url, error=str(e))
                raise APIError(error_msg)

    async def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response data
        """
        return await self._request("GET", endpoint, params=params)

    async def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make POST request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data

        Returns:
            Response data
        """
        return await self._request("POST", endpoint, data=data, json=json)

    async def put(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make PUT request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data

        Returns:
            Response data
        """
        return await self._request("PUT", endpoint, data=data, json=json)

    async def patch(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make PATCH request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data

        Returns:
            Response data
        """
        return await self._request("PATCH", endpoint, data=data, json=json)

    async def delete(self, endpoint: str) -> dict[str, Any]:
        """Make DELETE request.

        Args:
            endpoint: API endpoint

        Returns:
            Response data
        """
        return await self._request("DELETE", endpoint)
