"""Example: Autocomplete.search() - search for places and POI by phrase.

Usage:
    uv run python examples/autocomplete_search.py [--debug]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== Autocomplete.search() - phrase search ===\n")

try:
    response = client.autocomplete().search(
        query="Warszawa Domaniewska 37",
        # types=["place"],  # optional: 'place', 'poi' or both
    )

    items = response.data().get("items", [])

    if not items:
        print("No results.")
        sys.exit(0)

    for item in items:
        name = item.get("name", "n/a")
        item_type = item.get("type", "n/a")
        subtype = item.get("subtype", "n/a")
        coords = item.get("coords", {})
        x = coords.get("x", "n/a")  # lng
        y = coords.get("y", "n/a")  # lat
        print(f"  {name}")
        print(f"    type={item_type}/{subtype}  x={x}, y={y}")
        print()

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
