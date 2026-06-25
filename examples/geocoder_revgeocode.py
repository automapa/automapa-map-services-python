"""Example: Geocoder.revgeocode() - reverse geocode coordinates to an address.

Usage:
    uv run python examples/geocoder_revgeocode.py [--debug]

Note: x = longitude (lng), y = latitude (lat).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== Geocoder.revgeocode() - coordinates → address ===\n")

# Warsaw city centre (x=lng, y=lat)
x, y = 21.0073642, 52.18288

try:
    response = client.geocoder().revgeocode(point=[x, y])

    data = response.data()
    print(f"City    : {data.get('city', 'n/a')}")
    print(f"Street  : {data.get('street', 'n/a')} {data.get('house', '')}")
    print(f"Postcode: {data.get('pcode', 'n/a')}")
    print(f"Province: {data.get('province', 'n/a')}")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
