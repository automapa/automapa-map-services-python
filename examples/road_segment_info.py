"""Example: Road.get_segment_info() - road segment information.

Usage:
    uv run python examples/road_segment_info.py [--debug]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== Road.get_segment_info() - road segment information ===\n")

# Warsaw city centre
x, y = 21.0073642, 52.2297

try:
    response = client.road().get_segment_info(
        {
            "point": [x, y],
        }
    )

    data = response.data()
    print(f"Segment ID   : {data.get('id', 'n/a')}")
    print(f"Category     : {data.get('category', 'n/a')}")
    print(f"Speed limit  : {data.get('speed', 'n/a')} km/h")
    print(f"Toll         : {data.get('toll', 'n/a')}")
    print(f"Restrictions : {data.get('restrictions', 'n/a')}")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
