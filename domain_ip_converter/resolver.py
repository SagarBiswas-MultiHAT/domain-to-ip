"""DNS resolver implementation with dnspython preference."""

from __future__ import annotations

import importlib
import ipaddress
import socket
from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Set

from .errors import DNSTimeoutError, ResolutionError
from .validate import is_ip_address

dns_exception: Optional[Any]
dns_resolver: Optional[Any]
try:  # pragma: no cover - import presence tested via monkeypatch
    dns_exception = importlib.import_module("dns.exception")
    dns_resolver = importlib.import_module("dns.resolver")
    HAS_DNSPYTHON = True
except Exception:  # pragma: no cover
    dns_exception = None
    dns_resolver = None
    HAS_DNSPYTHON = False


@dataclass(frozen=True)
class ResolveResult:
    ipv4: List[str]
    ipv6: List[str]


def _sorted_unique(ips: Iterable[str]) -> List[str]:
    unique = {str(ipaddress.ip_address(ip)) for ip in ips}
    return sorted(unique, key=lambda ip: ipaddress.ip_address(ip))


def _resolve_with_dnspython(host: str, timeout: float) -> ResolveResult:
    if not HAS_DNSPYTHON or dns_exception is None or dns_resolver is None:
        raise ResolutionError("dnspython is not available.")

    resolver = dns_resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = timeout

    ipv4: Set[str] = set()
    ipv6: Set[str] = set()

    def _query(record_type: str, bucket: Set[str]) -> None:
        try:
            answers = resolver.resolve(host, record_type, lifetime=timeout)
        except dns_exception.Timeout as exc:
            raise DNSTimeoutError(
                f"DNS resolution timed out for '{host}'."
            ) from exc
        except dns_resolver.NXDOMAIN as exc:
            raise ResolutionError(
                f"Domain does not exist: '{host}'."
            ) from exc
        except dns_resolver.NoAnswer:
            return
        except dns_resolver.NoNameservers as exc:
            raise ResolutionError(
                f"No nameservers available for '{host}'."
            ) from exc
        except dns_exception.DNSException as exc:
            raise ResolutionError(
                f"DNS resolution failed for '{host}'."
            ) from exc

        for item in answers:
            address = getattr(item, "address", None)
            if address is not None:
                bucket.add(str(address))

    _query("A", ipv4)
    _query("AAAA", ipv6)

    return ResolveResult(ipv4=_sorted_unique(ipv4), ipv6=_sorted_unique(ipv6))


def _resolve_with_socket(host: str) -> ResolveResult:
    ipv4: Set[str] = set()
    ipv6: Set[str] = set()

    try:
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise ResolutionError(
            f"DNS resolution failed for '{host}'."
        ) from exc

    for family, _, _, _, sockaddr in infos:
        if family == socket.AF_INET:
            ipv4.add(str(sockaddr[0]))
        elif family == socket.AF_INET6:
            ipv6.add(str(sockaddr[0]))

    return ResolveResult(ipv4=_sorted_unique(ipv4), ipv6=_sorted_unique(ipv6))


def resolve_host(host: str, timeout: float = 5.0) -> ResolveResult:
    """Resolve a hostname or literal IP to IPv4/IPv6 addresses."""

    if is_ip_address(host):
        ip_obj = ipaddress.ip_address(host)
        if ip_obj.version == 4:
            return ResolveResult(ipv4=[str(ip_obj)], ipv6=[])
        return ResolveResult(ipv4=[], ipv6=[str(ip_obj)])

    if HAS_DNSPYTHON:
        return _resolve_with_dnspython(host, timeout)

    return _resolve_with_socket(host)
