# Contributing

Thanks for contributing!

## Development Setup

1. Create a virtual environment.
2. Install dependencies:

```
pip install .[dev]
```

## Code Quality

- Format: `black .`
- Lint: `flake8`
- Types: `mypy domain_ip_converter`

## Tests

```
pytest
```

## Guidelines

- Keep functions small and well-documented.
- Add or update tests for any behavior changes.
- Avoid real network access in tests.
