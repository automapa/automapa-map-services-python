"""Example: Geocoder.geocode() - geocode an address to coordinates.

Usage:
    uv run python examples/geocoder_geocode.py [--debug]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== Geocoder.geocode() - address → coordinates ===\n")

try:
    response = client.geocoder().geocode(
        city="Warszawa", street="Domaniewska", house="37", max_results=1
    )

    results = response.data()
    if not results:
        print("No results.")
        sys.exit(0)

    first = results[0]
    print(f"City    : {first.get('city', 'n/a')}")
    print(f"Street  : {first.get('street', 'n/a')} {first.get('house', '')}")
    print(f"Postcode: {first.get('pcode', 'n/a')}")
    print(f"Lng (x) : {first.get('x', 'n/a')}")
    print(f"Lat (y) : {first.get('y', 'n/a')}")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
