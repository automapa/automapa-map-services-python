"""Example: GoogleGeocodeAdapter - drop-in adapter for Google Geocoding API users.

Usage:
    uv run python examples/google_geocode_adapter.py [--debug]

Input modes demonstrated:
    1. components string  - most accurate (recommended)
    2. address string     - best-effort parse (easiest migration)
    3. address dict       - structured Automapa format (no parsing)
"""

from __future__ import annotations

import pprint
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services import GoogleGeocodeAdapter
from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()
adapter = GoogleGeocodeAdapter(client)


def print_google_result(result: dict) -> None:  # type: ignore[type-arg]
    print(f"Status  : {result.get('status', 'n/a')}")
    results = result.get("results", [])
    if not results:
        print("No results.")
        return
    first = results[0]
    location = first.get("geometry", {}).get("location", {})
    print(f"Address : {first.get('formatted_address', 'n/a')}")
    print(f"Lat     : {location.get('lat', 'n/a')}")
    print(f"Lng     : {location.get('lng', 'n/a')}")
    print(f"Types   : {', '.join(first.get('types', []))}")
    pprint.pprint({"google_raw": result})


# --- Mode 1: components string (Google filter format) -------------------------
print("=== Mode 1: components string ===\n")
try:
    result = adapter.geocode(
        {
            "components": "locality:Warszawa|route:Domaniewska|street_number:37",
        }
    )
    print_google_result(result)
except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")

print()

# --- Mode 2: address string (best-effort parse) --------------------------------
print("=== Mode 2: address string ===\n")
try:
    result = adapter.geocode(
        {
            "address": "Domaniewska 37, Warszawa",
            "language": "pl",  # accepted, ignored (Google compatibility)
            "key": "n/a",  # accepted, ignored (SDK uses its own credentials)
        }
    )
    print_google_result(result)
except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")

print()

# --- Mode 3: address dict (structured Automapa format) ------------------------
print("=== Mode 3: address dict ===\n")
try:
    result = adapter.geocode(
        {
            "address": {"city": "Gdańsk", "street": "Długa", "house": "1"},
            "maxResults": 3,
        }
    )
    print_google_result(result)
except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
