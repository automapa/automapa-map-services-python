"""Example: Road.speed_check_multi() - speed limits for multiple points.

Usage:
    uv run python examples/road_speed_check_multi.py [--debug]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== Road.speed_check_multi() - speed limits for multiple points ===\n")

points = [
    [21.0073642, 52.2297],  # Warszawa
    [18.6282, 54.3520],  # Gdańsk
    [19.9449800, 50.0646],  # Kraków
]

try:
    response = client.road().speed_check_multi(
        {
            "points": points,
        }
    )

    results = response.data()
    for i, result in enumerate(results):
        x, y = points[i]
        speed = result.get("speed", "n/a")
        print(f"  ({x:.4f}, {y:.4f}) → {speed} km/h")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
