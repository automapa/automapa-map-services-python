"""Example: RoadPermit.overwrite() - replace an existing road permit.

Usage:
    uv run python examples/road_permit_overwrite.py <id> [--debug]
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.endpoints.road_permit import RoadPermit
from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

args = [a for a in sys.argv[1:] if not a.startswith("--")]
if not args:
    sys.stderr.write("Usage: uv run python examples/road_permit_overwrite.py <id>\n")
    sys.exit(1)

permit_id = args[0]
client = make_client()

print(f"=== RoadPermit.overwrite() - replace permit ID={permit_id} ===\n")

poly = {
    "type": "Polygon",
    "coordinates": [
        [
            [21.000, 52.220],
            [21.030, 52.220],
            [21.030, 52.250],
            [21.000, 52.250],
            [21.000, 52.220],
        ]
    ],
}

try:
    response = client.road_permit(RoadPermit.ROAD_PERMIT_ENVIRONMENT_TEST).overwrite(
        permit_id,
        permissions={"tr_tonnage": 20, "tr_tonn_axis": 10.0},
        poly=poly,
        date_start="2025-03-01",
        date_end="2025-12-31",
        description="Updated SDK permit",
        document_name="DOC-002",
        location="Warsaw test area (extended)",
        is_valid_after_expiry=False,
    )

    data = response.data()
    new_id = data.get("id") or response.raw().get("result", {}).get("id", "n/a")
    print(f"Permit updated. ID: {new_id}")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
