"""Shared initialisation for Automapa SDK examples.

Usage:
    from examples.bootstrap import make_client
    client = make_client()

Configuration:
    1. Copy .env.example to .env
    2. Fill in AUTOMAPA_API_KEY and AUTOMAPA_API_PASSWORD
    3. Run: uv run python examples/geocoder_geocode.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from automapa_map_services import ApiClient, Config
from automapa_map_services.http.debug_client import DebugHttpClient
from automapa_map_services.http.urllib_client import UrllibHttpClient


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not os.environ.get(key):
            os.environ[key] = value


def make_client() -> ApiClient:
    _load_dotenv(Path(__file__).parent.parent / ".env")

    api_key = os.environ.get("AUTOMAPA_API_KEY", "")
    api_password = os.environ.get("AUTOMAPA_API_PASSWORD", "")

    if not api_key or not api_password:
        sys.stderr.write(
            "Error: Missing API credentials.\n\n"
            "  1. Copy .env.example to .env:\n"
            "       cp .env.example .env\n"
            "  2. Fill in AUTOMAPA_API_KEY and AUTOMAPA_API_PASSWORD\n\n"
        )
        sys.exit(1)

    config = Config(key=api_key, password=api_password)
    debug = "--debug" in sys.argv or os.environ.get("DEBUG") == "1"
    http_client: UrllibHttpClient | DebugHttpClient = UrllibHttpClient(config.timeout_seconds)

    if debug:
        http_client = DebugHttpClient(http_client, sys.stderr)

    return ApiClient(config, http_client)
