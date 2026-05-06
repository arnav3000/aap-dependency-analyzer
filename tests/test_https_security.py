"""Test HTTPS-only security enforcement for AAP connections."""

import pytest
from pydantic import SecretStr, ValidationError

from aap_migration_planner.config.config import AAPInstanceConfig


class TestHTTPSOnlySecurity:
    """Test that only HTTPS URLs are accepted for AAP connections."""

    def test_https_url_accepted(self):
        """HTTPS URLs should be accepted."""
        config = AAPInstanceConfig(url="https://aap.example.com", token=SecretStr("test_token"))
        assert config.url == "https://aap.example.com/api/v2"

    def test_http_url_rejected(self):
        """HTTP URLs should be rejected with security error."""
        with pytest.raises(ValidationError) as exc_info:
            AAPInstanceConfig(url="http://aap.example.com", token=SecretStr("test_token"))

        error_message = str(exc_info.value)
        assert "HTTP URLs are not allowed" in error_message
        assert "security" in error_message.lower()
        assert "https://aap.example.com" in error_message  # Suggested fix

    def test_url_without_protocol_rejected(self):
        """URLs without https:// protocol should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AAPInstanceConfig(url="aap.example.com", token=SecretStr("test_token"))

        error_message = str(exc_info.value)
        assert "must start with https://" in error_message

    def test_url_normalization_preserves_https(self):
        """URL normalization should preserve HTTPS scheme."""
        config = AAPInstanceConfig(url="https://aap.example.com/", token=SecretStr("test_token"))
        assert config.url.startswith("https://")
        assert config.url == "https://aap.example.com/api/v2"

    def test_http_url_with_api_suffix_still_rejected(self):
        """HTTP URLs should be rejected even with /api/v2 suffix."""
        with pytest.raises(ValidationError) as exc_info:
            AAPInstanceConfig(url="http://aap.example.com/api/v2", token=SecretStr("test_token"))

        error_message = str(exc_info.value)
        assert "HTTP URLs are not allowed" in error_message

    def test_https_url_with_port(self):
        """HTTPS URLs with custom ports should be accepted."""
        config = AAPInstanceConfig(
            url="https://aap.example.com:8443", token=SecretStr("test_token")
        )
        assert config.url == "https://aap.example.com:8443/api/v2"

    def test_token_is_secret(self):
        """Token should be masked in model dump."""
        config = AAPInstanceConfig(
            url="https://aap.example.com", token=SecretStr("secret_token_123")
        )
        safe_dump = config.model_dump_safe()
        assert safe_dump["token"] == "***REDACTED***"
        assert "secret_token_123" not in str(safe_dump)

    def test_from_env_with_http_url_fails(self, monkeypatch):
        """Loading from environment with HTTP URL should fail."""
        monkeypatch.setenv("AAP_URL", "http://aap.example.com")
        monkeypatch.setenv("AAP_TOKEN", "test_token")

        with pytest.raises(ValidationError) as exc_info:
            AAPInstanceConfig.from_env()

        error_message = str(exc_info.value)
        assert "HTTP URLs are not allowed" in error_message

    def test_from_env_with_https_url_succeeds(self, monkeypatch):
        """Loading from environment with HTTPS URL should succeed."""
        monkeypatch.setenv("AAP_URL", "https://aap.example.com")
        monkeypatch.setenv("AAP_TOKEN", "test_token")

        config = AAPInstanceConfig.from_env()
        assert config.url == "https://aap.example.com/api/v2"
        assert config.token.get_secret_value() == "test_token"
