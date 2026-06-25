"""Example: Geocoder.revgeocodemulti() - batch reverse geocode multiple points.

Usage:
    uv run python examples/geocoder_revgeocodemulti.py [--debug]

Note: x = longitude (lng), y = latitude (lat).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== Geocoder.revgeocodemulti() - batch reverse geocoding ===\n")

points = [
    [21.0073642, 52.18288],  # Warszawa
    [18.6282, 54.3520],  # Gdańsk
    [19.9449800, 50.0646500],  # Kraków
]

try:
    response = client.geocoder().revgeocodemulti(points=points)
    results = response.data()

    for i, result in enumerate(results):
        x, y = points[i]
        city = result.get("city", "n/a")
        street = result.get("street", "")
        house = result.get("house", "")
        print(f"  ({x}, {y}) → {city}, {street} {house}".rstrip())

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
