"""Validation and normalization utilities."""

from __future__ import annotations

import ipaddress
import re
from typing import Tuple
from urllib.parse import urlsplit

from .errors import InvalidInputError

_HOST_LABEL_RE = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")


def _split_url(value: str) -> Tuple[str, str]:
    value = value.strip()
    if not value:
        raise InvalidInputError("Input is empty.")

    if value.startswith(("http://", "https://")) or "://" in value:
        split = urlsplit(value)
        if split.scheme and split.scheme not in {"http", "https"}:
            raise InvalidInputError(
                f"Unsupported URL scheme: '{split.scheme}'."
            )
        host = split.hostname
        if not host:
            raise InvalidInputError("URL does not contain a host.")
        return host, split.scheme

    if any(ch in value for ch in "/?#@"):  # likely a URL without scheme
        split = urlsplit(f"http://{value}")
        host = split.hostname
        if not host:
            raise InvalidInputError("URL does not contain a host.")
        return host, "http"

    return value, ""


def is_ip_address(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return False
    return True


def normalize_domain(raw: str) -> str:
    """Normalize a raw input into a hostname or literal IP string.

    Accepts:
        - Hostnames (including IDNs)
        - IPv4 / IPv6 literal addresses
        - http/https URLs (with credentials, port, path)
    """

    host, _scheme = _split_url(raw)
    host = host.strip().rstrip(".")
    if host.startswith("[") and host.endswith("]"):
        host = host[1:-1]

    if not host:
        raise InvalidInputError("Host is empty after normalization.")

    if is_ip_address(host):
        return str(ipaddress.ip_address(host))

    try:
        ascii_host = (
            host.encode("idna").decode("ascii").lower()
        )
    except UnicodeError as exc:
        raise InvalidInputError(
            "Invalid internationalized domain name."
        ) from exc

    if len(ascii_host) > 253:
        raise InvalidInputError("Hostname exceeds 253 characters.")

    labels = ascii_host.split(".")
    if any(not label for label in labels):
        raise InvalidInputError("Hostname contains empty labels.")

    for label in labels:
        if not _HOST_LABEL_RE.match(label):
            raise InvalidInputError(
                f"Invalid hostname label: '{label}'."
            )

    return ascii_host
