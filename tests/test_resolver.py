from __future__ import annotations

import socket

import pytest

from domain_ip_converter.errors import DNSTimeoutError, ResolutionError
from domain_ip_converter import resolver


class _FakeAnswer:
    def __init__(self, address: str) -> None:
        self.address = address


class _FakeTimeout(Exception):
    pass


class _FakeDNSException(Exception):
    pass


class _FakeNXDOMAIN(_FakeDNSException):
    pass


class _FakeNoAnswer(_FakeDNSException):
    pass


class _FakeNoNameservers(_FakeDNSException):
    pass


class _FakeResolver:
    def __init__(self) -> None:
        self.timeout = 0.0
        self.lifetime = 0.0

    def resolve(self, host: str, record_type: str, lifetime: float):
        if host == "timeout.example":
            raise _FakeTimeout()
        if host == "missing.example":
            raise _FakeNXDOMAIN()
        if host == "nonameservers.example":
            raise _FakeNoNameservers()
        if host == "error.example":
            raise _FakeDNSException()
        if host == "noanswer.example":
            raise _FakeNoAnswer()
        if record_type == "A":
            return [_FakeAnswer("1.1.1.1"), _FakeAnswer("1.1.1.1")]
        if record_type == "AAAA":
            return [_FakeAnswer("2001:db8::1")]
        raise _FakeNoAnswer()


class _FakeDNS:
    class resolver:
        Resolver = _FakeResolver
        NXDOMAIN = _FakeNXDOMAIN
        NoAnswer = _FakeNoAnswer
        NoNameservers = _FakeNoNameservers

    class exception:
        Timeout = _FakeTimeout
        DNSException = _FakeDNSException


def test_resolve_with_dnspython(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(resolver, "HAS_DNSPYTHON", True)
    monkeypatch.setattr(resolver, "dns_exception", _FakeDNS.exception)
    monkeypatch.setattr(resolver, "dns_resolver", _FakeDNS.resolver)

    result = resolver.resolve_host("example.com", timeout=1.0)
    assert result.ipv4 == ["1.1.1.1"]
    assert result.ipv6 == ["2001:db8::1"]


def test_resolve_dnspython_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(resolver, "HAS_DNSPYTHON", True)
    monkeypatch.setattr(resolver, "dns_exception", _FakeDNS.exception)
    monkeypatch.setattr(resolver, "dns_resolver", _FakeDNS.resolver)

    with pytest.raises(DNSTimeoutError):
        resolver.resolve_host("timeout.example", timeout=1.0)


def test_resolve_dnspython_nxdomain(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(resolver, "HAS_DNSPYTHON", True)
    monkeypatch.setattr(resolver, "dns_exception", _FakeDNS.exception)
    monkeypatch.setattr(resolver, "dns_resolver", _FakeDNS.resolver)

    with pytest.raises(ResolutionError):
        resolver.resolve_host("missing.example", timeout=1.0)


def test_resolve_dnspython_noanswer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(resolver, "HAS_DNSPYTHON", True)
    monkeypatch.setattr(resolver, "dns_exception", _FakeDNS.exception)
    monkeypatch.setattr(resolver, "dns_resolver", _FakeDNS.resolver)

    result = resolver.resolve_host("noanswer.example", timeout=1.0)
    assert result.ipv4 == []
    assert result.ipv6 == []


def test_resolve_dnspython_nonameservers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(resolver, "HAS_DNSPYTHON", True)
    monkeypatch.setattr(resolver, "dns_exception", _FakeDNS.exception)
    monkeypatch.setattr(resolver, "dns_resolver", _FakeDNS.resolver)

    with pytest.raises(ResolutionError):
        resolver.resolve_host("nonameservers.example", timeout=1.0)


def test_resolve_dnspython_generic_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(resolver, "HAS_DNSPYTHON", True)
    monkeypatch.setattr(resolver, "dns_exception", _FakeDNS.exception)
    monkeypatch.setattr(resolver, "dns_resolver", _FakeDNS.resolver)

    with pytest.raises(ResolutionError):
        resolver.resolve_host("error.example", timeout=1.0)


def test_resolve_with_socket(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_getaddrinfo(host: str, *_args, **_kwargs):
        assert host == "example.com"
        return [
            (socket.AF_INET, None, None, None, ("8.8.8.8", 0)),
            (socket.AF_INET6, None, None, None, ("2001:db8::2", 0, 0, 0)),
        ]

    monkeypatch.setattr(resolver, "HAS_DNSPYTHON", False)
    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    result = resolver.resolve_host("example.com", timeout=1.0)
    assert result.ipv4 == ["8.8.8.8"]
    assert result.ipv6 == ["2001:db8::2"]


def test_resolve_with_socket_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_getaddrinfo(host: str, *_args, **_kwargs):
        raise socket.gaierror(8, "not found")

    monkeypatch.setattr(resolver, "HAS_DNSPYTHON", False)
    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    with pytest.raises(ResolutionError):
        resolver.resolve_host("bad.example", timeout=1.0)


def test_resolve_literal_ip() -> None:
    result = resolver.resolve_host("192.0.2.1", timeout=1.0)
    assert result.ipv4 == ["192.0.2.1"]
    assert result.ipv6 == []
