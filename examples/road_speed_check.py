"""Example: Road.speed_check() - speed limit for a single point.

Usage:
    uv run python examples/road_speed_check.py [--debug]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== Road.speed_check() - speed limit for a point ===\n")

x, y = 21.0073642, 52.2297  # Warszawa

try:
    response = client.road().speed_check(
        {
            "point": [x, y],
        }
    )

    data = response.data()
    print(f"Speed limit  : {data.get('speed', 'n/a')} km/h")
    print(f"Road name    : {data.get('road', 'n/a')}")
    print(f"Segment ID   : {data.get('segmentId', 'n/a')}")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
