"""Example: RoadPermit.add() - create a new road permit.

Usage:
    uv run python examples/road_permit_add.py [--debug]

GeoJSON polygon: coordinates are [longitude, latitude];
the ring must be closed (first == last coordinate).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.endpoints.road_permit import RoadPermit
from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== RoadPermit.add() - create permit (test environment) ===\n")

poly = {
    "type": "Polygon",
    "coordinates": [
        [
            [21.000, 52.220],
            [21.020, 52.220],
            [21.020, 52.240],
            [21.000, 52.240],
            [21.000, 52.220],  # closing point == starting point
        ]
    ],
}

try:
    response = client.road_permit(RoadPermit.ROAD_PERMIT_ENVIRONMENT_TEST).add(
        permissions={"tr_tonnage": 12, "tr_tonn_axis": 8.5},
        poly=poly,
        date_start="2025-01-01",
        date_end="2025-12-31",
        description="Sample SDK permit",
        document_name="DOC-001",
        location="Warsaw test area",
        is_valid_after_expiry=False,
    )

    data = response.data()
    permit_id = data.get("id") or response.raw().get("result", {}).get("id", "n/a")
    print(f"Permit created. ID: {permit_id}")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
