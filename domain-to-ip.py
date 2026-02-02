#!/usr/bin/env python3
"""Backward-compatible entry script."""

from __future__ import annotations

from domain_ip_converter.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
