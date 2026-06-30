"""Example: Routes.optimize() - synchronous point-order optimisation (max 10).

Usage:
    uv run python examples/routes_optimize.py [--debug]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== Routes.optimize() - route optimisation (synchronous) ===\n")

cities = ["Warszawa", "Gdańsk", "Kraków", "Wrocław"]
points = [
    {"x": 21.0073642, "y": 52.2297},
    {"x": 18.6282, "y": 54.3520},
    {"x": 19.9449800, "y": 50.0646},
    {"x": 17.0385, "y": 51.1079},
]

try:
    response = client.routes().optimize(
        points=points,
        type=1,  # 1 = time, 2 = distance
        fixed_end=False,  # True = last point is the destination; False = return to start
        object={"type": "car"},
    )

    data = response.data()
    order = data.get("order", "")
    print(f"Optimal order (indices): {order}")

    indices = [int(i) for i in str(order).split(",") if i.strip().lstrip("-").isdigit()]
    names = [cities[i] for i in indices if 0 <= i < len(cities)]
    print(f"Route: {' → '.join(names)}\n")

    sections = data.get("sections", [])
    for section in sections:
        dist = round(section.get("dist", 0) / 1000, 1)
        eta = section.get("eta", 0)
        x = section.get("x", "?")
        y = section.get("y", "?")
        print(f"  ({x}, {y})  {dist} km  {eta} s")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
