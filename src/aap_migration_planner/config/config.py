"""Configuration models for AAP Migration Planner.

This module defines configuration schemas using Pydantic for validation.
"""

import os
from typing import Any

from pydantic import BaseModel, Field, SecretStr, field_validator


class AAPInstanceConfig(BaseModel):
    """Configuration for an AAP instance connection.

    This model validates AAP connection parameters and provides
    convenient loading from environment variables.
    """

    url: str = Field(
        ...,
        description="AAP instance URL (e.g., https://aap.example.com)",
    )
    token: SecretStr = Field(
        ...,
        description="AAP API authentication token",
    )
    verify_ssl: bool = Field(
        default=True,
        description="Whether to verify SSL certificates",
    )
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Request timeout in seconds",
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate and normalize URL.

        Args:
            v: URL string to validate

        Returns:
            Normalized URL

        Raises:
            ValueError: If URL is invalid
        """
        if not v:
            raise ValueError("URL cannot be empty")

        # Ensure URL starts with http:// or https://
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")

        # Remove trailing slash
        v = v.rstrip("/")

        # Add /api/v2 suffix if not present
        if not v.endswith("/api/v2"):
            v = f"{v}/api/v2"

        return v

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout value.

        Args:
            v: Timeout value in seconds

        Returns:
            Validated timeout

        Raises:
            ValueError: If timeout is out of range
        """
        if v < 1 or v > 300:
            raise ValueError("Timeout must be between 1 and 300 seconds")
        return v

    @classmethod
    def from_env(cls, prefix: str = "AAP") -> "AAPInstanceConfig":
        """Load configuration from environment variables.

        Args:
            prefix: Environment variable prefix (default: AAP)

        Returns:
            AAPInstanceConfig instance

        Raises:
            ValueError: If required environment variables are missing

        Environment variables:
            {PREFIX}_URL: AAP instance URL
            {PREFIX}_TOKEN: API token
            {PREFIX}_VERIFY_SSL: SSL verification (true/false)
            {PREFIX}_TIMEOUT: Request timeout in seconds
        """
        url = os.getenv(f"{prefix}_URL")
        token = os.getenv(f"{prefix}_TOKEN")

        if not url:
            raise ValueError(f"Missing required environment variable: {prefix}_URL")
        if not token:
            raise ValueError(f"Missing required environment variable: {prefix}_TOKEN")

        # Parse verify_ssl (default to true)
        verify_ssl_str = os.getenv(f"{prefix}_VERIFY_SSL", "true").lower()
        verify_ssl = verify_ssl_str in ("true", "1", "yes", "on")

        # Parse timeout (default to 30)
        timeout_str = os.getenv(f"{prefix}_TIMEOUT", "30")
        try:
            timeout = int(timeout_str)
        except ValueError:
            raise ValueError(f"Invalid timeout value: {timeout_str}. Must be an integer.")

        return cls(
            url=url,
            token=SecretStr(token),
            verify_ssl=verify_ssl,
            timeout=timeout,
        )

    def model_dump_safe(self) -> dict[str, Any]:
        """Dump model to dict with masked secrets.

        Returns:
            Dictionary with token masked
        """
        data = self.model_dump()
        data["token"] = "***REDACTED***"
        return data

    class Config:
        """Pydantic model configuration."""

        # Allow arbitrary types for SecretStr
        arbitrary_types_allowed = True
