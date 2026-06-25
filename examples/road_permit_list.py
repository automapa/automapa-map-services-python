"""Example: RoadPermit.list() - list road permits.

Usage:
    uv run python examples/road_permit_list.py [--debug]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.endpoints.road_permit import RoadPermit
from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== RoadPermit.list() - list permits (test environment) ===\n")

try:
    response = client.road_permit(RoadPermit.ROAD_PERMIT_ENVIRONMENT_TEST).list()
    items = response.data()

    if not items:
        print("No permits found.")
        sys.exit(0)

    for permit in items:
        permit_id = permit.get("id", "n/a")
        description = permit.get("description", "n/a")
        date_start = permit.get("date_start", "n/a")
        date_end = permit.get("date_end", "n/a")
        print(f"  ID         : {permit_id}")
        print(f"  Description: {description}")
        print(f"  Valid      : {date_start} – {date_end}")
        print()

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
