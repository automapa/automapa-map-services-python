"""Example: Geocoder.geocodemulti() - batch geocode multiple addresses.

Usage:
    uv run python examples/geocoder_geocodemulti.py [--debug]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== Geocoder.geocodemulti() - batch geocoding ===\n")

addresses = [
    {"city": "Warszawa", "street": "Domaniewska", "house": "37"},
    {"city": "Gdańsk", "street": "Długa", "house": "1"},
    {"city": "Kraków", "street": "Floriańska", "house": "2"},
]

try:
    response = client.geocoder().geocodemulti(addresses=addresses)
    results = response.data()

    for i, result in enumerate(results):
        addr = addresses[i]
        label = f"{addr['city']}, {addr['street']} {addr['house']}"
        x = result.get("x", "n/a")
        y = result.get("y", "n/a")
        print(f"  {label:<40} → x={x}, y={y}")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
