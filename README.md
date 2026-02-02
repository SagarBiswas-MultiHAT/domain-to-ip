# Domain to IP Converter

Resolve domains, URLs, and IP literals into IPv4/IPv6 addresses with a fast, library-safe API and a production-ready CLI.

## Overview

- Accepts hostnames, IPv4, IPv6, IDNs (punycode), and http/https URLs.
- Uses dnspython (A + AAAA) when available with real timeout support.
- Falls back to `socket.getaddrinfo` when dnspython is unavailable.
- Clean CLI with JSON output, concurrency, and quiet/no-color controls.

## Installation

Install from source:

```
pip install .
```

Optional DNS dependency (recommended for timeouts):

```
pip install .[dns]
```

Development tooling:

```
pip install .[dev]
```

## CLI Examples

Resolve a domain:

```
ip-converter example.com
```

Resolve a URL and emit JSON:

```
ip-converter https://user:pass@example.com/path --json
```

Resolve many domains with concurrency and a custom timeout:

```
ip-converter example.com example.org --timeout 2.5 --concurrency 8
```

Read from a file:

```
ip-converter --file domains.txt
```

## Library Usage

```python
from domain_ip_converter import normalize_domain, resolve_host

host = normalize_domain("https://пример.рф/path")
result = resolve_host(host, timeout=2.0)
print(result.ipv4, result.ipv6)
```

## Optional Dependencies

- `dnspython` (extra: `dns`) enables reliable DNS timeouts and record querying.

## Testing

```
pytest
```

Run with coverage:

```
pytest --cov=domain_ip_converter --cov-report=term-missing
```

## License

MIT License. See LICENSE.
