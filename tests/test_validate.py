from __future__ import annotations

import pytest

from domain_ip_converter.errors import InvalidInputError
from domain_ip_converter.validate import normalize_domain


def test_normalize_domain_basic() -> None:
    assert normalize_domain("Example.COM") == "example.com"


def test_normalize_domain_url_with_credentials() -> None:
    assert (
        normalize_domain("https://user:pass@Example.com:8443/path")
        == "example.com"
    )


def test_normalize_domain_idn() -> None:
    assert normalize_domain("пример.рф") == "xn--e1afmkfd.xn--p1ai"


def test_normalize_domain_ipv4() -> None:
    assert normalize_domain("127.0.0.1") == "127.0.0.1"


def test_normalize_domain_ipv6_url() -> None:
    assert normalize_domain("http://[2001:db8::1]:8080/") == "2001:db8::1"


def test_normalize_domain_ipv6_bracketed() -> None:
    assert normalize_domain("[2001:db8::1]") == "2001:db8::1"


def test_normalize_domain_invalid_scheme() -> None:
    with pytest.raises(InvalidInputError):
        normalize_domain("ftp://example.com")


def test_normalize_domain_invalid_label() -> None:
    with pytest.raises(InvalidInputError):
        normalize_domain("-bad.example")


def test_normalize_domain_empty_input() -> None:
    with pytest.raises(InvalidInputError):
        normalize_domain("   ")


def test_normalize_domain_url_without_host() -> None:
    with pytest.raises(InvalidInputError):
        normalize_domain("http://")


def test_normalize_domain_url_without_scheme() -> None:
    assert normalize_domain("example.com/path") == "example.com"


def test_normalize_domain_empty_label() -> None:
    with pytest.raises(InvalidInputError):
        normalize_domain("example..com")
