from __future__ import annotations

import sys

import pytest

from domain_ip_converter import cli
from domain_ip_converter.resolver import ResolveResult


def test_cli_json_output(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fake_resolve(host: str, timeout: float = 5.0) -> ResolveResult:
        assert timeout == 2.5
        return ResolveResult(ipv4=["203.0.113.1"], ipv6=[])

    monkeypatch.setattr(cli, "resolve_host", fake_resolve)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)

    code = cli.main(["example.com", "--json", "--timeout", "2.5"])
    assert code == 0
    output = capsys.readouterr().out
    assert "Domain to IP Converter" not in output
    assert "203.0.113.1" in output


def test_cli_text_output(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fake_resolve(host: str, timeout: float = 5.0) -> ResolveResult:
        return ResolveResult(ipv4=["198.51.100.2"], ipv6=["2001:db8::3"])

    monkeypatch.setattr(cli, "resolve_host", fake_resolve)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)

    code = cli.main(["example.com"])
    assert code == 0
    output = capsys.readouterr().out
    assert "Domain: example.com" in output
    assert "198.51.100.2" in output
    assert "2001:db8::3" in output


def test_cli_file_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)

    code = cli.main(["--file", "does-not-exist.txt"])
    assert code == 2
    err = capsys.readouterr().err
    assert "File error" in err


def test_cli_parser_no_inputs(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    code = cli.main([])
    assert code == 2
    err = capsys.readouterr().err
    assert "No domains or URLs provided" in err


def test_cli_banner_when_tty(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_resolve(host: str, timeout: float = 5.0) -> ResolveResult:
        return ResolveResult(ipv4=["203.0.113.10"], ipv6=[])

    monkeypatch.setattr(cli, "resolve_host", fake_resolve)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

    code = cli.main(["example.com"])
    assert code == 0
    output = capsys.readouterr().out
    assert "Domain to IP Converter" in output


def test_cli_no_color_suppresses_banner(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_resolve(host: str, timeout: float = 5.0) -> ResolveResult:
        return ResolveResult(ipv4=["203.0.113.11"], ipv6=[])

    monkeypatch.setattr(cli, "resolve_host", fake_resolve)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

    code = cli.main(["example.com", "--no-color"])
    assert code == 0
    output = capsys.readouterr().out
    assert "Domain to IP Converter" not in output


def test_cli_invalid_timeout(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    code = cli.main(["example.com", "--timeout", "0"])
    assert code == 2
    err = capsys.readouterr().err
    assert "--timeout must be greater than 0" in err


def test_cli_invalid_concurrency(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    code = cli.main(["example.com", "--concurrency", "0"])
    assert code == 2
    err = capsys.readouterr().err
    assert "--concurrency must be at least 1" in err


def test_cli_file_input(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    def fake_resolve(host: str, timeout: float = 5.0) -> ResolveResult:
        return ResolveResult(ipv4=["203.0.113.12"], ipv6=[])

    file_path = tmp_path / "domains.txt"
    file_path.write_text(
        "example.com\n# comment\nexample.org\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "resolve_host", fake_resolve)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)

    code = cli.main(["--file", str(file_path)])
    assert code == 0
