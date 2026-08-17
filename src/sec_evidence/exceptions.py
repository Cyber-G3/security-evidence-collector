"""Application-specific exceptions."""


class SecEvidenceError(Exception):
    """Base exception for the application."""


class ConfigurationError(SecEvidenceError):
    """Invalid or missing configuration."""


class AuthenticationError(SecEvidenceError):
    """Authentication failed or credentials are insufficient."""


class ApiError(SecEvidenceError):
    """Remote API request failed."""


class CollectorError(SecEvidenceError):
    """Evidence collection failed."""
