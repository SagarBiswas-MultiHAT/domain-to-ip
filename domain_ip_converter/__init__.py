"""Domain to IP Converter package."""

from __future__ import annotations

from .cli import main
from .errors import (
    DNSTimeoutError,
    DomainIPConverterError,
    InvalidInputError,
    ResolutionError,
)
from .resolver import ResolveResult, resolve_host
from .validate import normalize_domain

__all__ = [
    "DNSTimeoutError",
    "DomainIPConverterError",
    "InvalidInputError",
    "ResolutionError",
    "ResolveResult",
    "main",
    "normalize_domain",
    "resolve_host",
]
