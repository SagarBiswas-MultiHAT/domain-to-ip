"""Command-line interface for domain-ip-converter."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, List, Tuple, TypedDict

from .errors import DomainIPConverterError, InvalidInputError
from .resolver import resolve_host
from .validate import normalize_domain


def _supports_color(no_color: bool) -> bool:
    if no_color:
        return False
    return sys.stdout.isatty()


def _banner(no_color: bool) -> str:
    if not _supports_color(no_color):
        return "Domain to IP Converter"
    return "\033[92mDomain to IP Converter\033[0m"


def _load_domains_from_file(path: str) -> List[str]:
    domains: List[str] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line and not line.startswith("#"):
                domains.append(line)
    return domains


class ResultItem(TypedDict, total=False):
    ipv4: List[str]
    ipv6: List[str]
    error: str


ResultsMap = Dict[str, ResultItem]


def _resolve_one(raw: str, timeout: float) -> Tuple[str, ResultItem]:
    try:
        normalized = normalize_domain(raw)
    except InvalidInputError as exc:
        return raw, {"error": str(exc)}

    try:
        result = resolve_host(normalized, timeout=timeout)
    except DomainIPConverterError as exc:
        return normalized, {"error": str(exc)}

    return normalized, {"ipv4": result.ipv4, "ipv6": result.ipv6}


def _resolve_many(
    domains: List[str], timeout: float, workers: int
) -> ResultsMap:
    results: ResultsMap = {}
    if not domains:
        return results

    if workers <= 1 or len(domains) == 1:
        for raw in domains:
            key, data = _resolve_one(raw, timeout)
            results[key] = data
        return results

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {
            executor.submit(_resolve_one, raw, timeout): raw for raw in domains
        }
        for future in as_completed(future_map):
            key, data = future.result()
            results[key] = data

    return results


def _print_human(results: ResultsMap) -> None:
    for domain, data in results.items():
        print(f"\nDomain: {domain}")
        if "error" in data:
            print(f"  Error: {data['error']}")
        else:
            ipv4 = ", ".join(data["ipv4"]) or "none"
            ipv6 = ", ".join(data["ipv6"]) or "none"
            print(f"  IPv4: {ipv4}")
            print(f"  IPv6: {ipv6}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve domain names to IPv4 and IPv6 addresses",
    )
    parser.add_argument(
        "domains",
        nargs="*",
        help="Domains or URLs to resolve",
    )
    parser.add_argument("-f", "--file", help="File containing domains")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress banner",
    )
    parser.add_argument(
        "--timeout", type=float, default=5.0, help="Timeout in seconds"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Number of thread workers for bulk resolution",
    )
    parser.add_argument(
        "--no-color", action="store_true", help="Disable colored output"
    )
    return parser


def main(argv: Iterable[str] = sys.argv[1:]) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv))

    if args.timeout <= 0:
        print("error: --timeout must be greater than 0.", file=sys.stderr)
        return 2

    if args.concurrency < 1:
        print("error: --concurrency must be at least 1.", file=sys.stderr)
        return 2

    raw_domains: List[str] = []
    if args.file:
        try:
            raw_domains.extend(_load_domains_from_file(args.file))
        except OSError as exc:
            print(f"File error: {exc}", file=sys.stderr)
            return 2

    raw_domains.extend(args.domains)

    if not raw_domains:
        print("error: No domains or URLs provided.", file=sys.stderr)
        parser.print_usage(sys.stderr)
        return 2

    if not args.quiet and _supports_color(args.no_color):
        print(_banner(args.no_color))

    results = _resolve_many(
        raw_domains,
        timeout=args.timeout,
        workers=args.concurrency,
    )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        _print_human(results)

    return 0
