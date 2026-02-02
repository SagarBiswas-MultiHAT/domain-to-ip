"""Custom error types for domain IP conversion."""

from __future__ import annotations


class DomainIPConverterError(Exception):
    """Base exception for all domain-ip-converter errors."""


class InvalidInputError(DomainIPConverterError):
    """Raised when input cannot be normalized or validated."""


class ResolutionError(DomainIPConverterError):
    """Raised when DNS resolution fails."""


class DNSTimeoutError(ResolutionError):
    """Raised when DNS resolution times out."""
