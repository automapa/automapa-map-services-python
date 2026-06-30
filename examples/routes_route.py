"""Example: Routes.route() - calculate a route from point A to point B.

Usage:
    uv run python examples/routes_route.py [--debug]

Note: x = longitude (lng), y = latitude (lat).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== Routes.route() - route Warsaw → Gdansk ===\n")

try:
    response = client.routes().route(
        points=[
            {"x": 21.0073642, "y": 52.2297},  # Warszawa
            {"x": 18.6282, "y": 54.3520},  # Gdańsk
        ],
        route={
            "type": "short",  # 'quick' | 'short' | 'optimal'
            "traffic": True,  # account for traffic
        },
        object={"type": "car"},
    )

    data = response.data()
    length_km = round(data.get("length", 0) / 1000, 1)
    eta_s = data.get("eta", 0)
    hours, remainder = divmod(int(eta_s), 3600)
    minutes = remainder // 60
    mapurl = data.get("mapurl", "")

    print(f"Distance : {length_km} km")
    print(f"Duration : {hours}h {minutes}min")
    print(f"Map      : {mapurl}")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
