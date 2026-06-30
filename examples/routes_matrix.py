"""Example: Routes.matrix() - distance/time matrix between points.

Usage:
    uv run python examples/routes_matrix.py [--debug]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== Routes.matrix() - distance/time matrix ===\n")

cities = ["Warszawa", "Gdańsk", "Kraków", "Wrocław"]
points = [
    {"x": 21.0073642, "y": 52.2297},  # Warszawa
    {"x": 18.6282, "y": 54.3520},  # Gdańsk
    {"x": 19.9449800, "y": 50.0646},  # Kraków
    {"x": 17.0385, "y": 51.1079},  # Wrocław
]

try:
    response = client.routes().matrix(
        points=points,
        type=1,  # 1 = time (minutes), 2 = distance (metres)
    )

    rows = response.data()
    print(f"  {'Route':<30}  {'km':>8}  {'time':>8}")
    print("  " + "-" * 52)

    for row in rows:
        pts = row.get("points", "?→?")
        try:
            from_idx, to_idx = [int(p) for p in str(pts).split(",")]
            label = f"{cities[from_idx]} → {cities[to_idx]}"
        except (ValueError, IndexError):
            label = str(pts)
        km = round(row.get("length", 0) / 1000)
        mins = row.get("duration", 0)
        print(f"  {label:<30}  {km:>7} km  {mins:>5} min")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
