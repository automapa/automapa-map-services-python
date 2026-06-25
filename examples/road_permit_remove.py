"""Example: RoadPermit.remove() - delete a road permit.

Usage:
    uv run python examples/road_permit_remove.py <id> [--debug]
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
    sys.stderr.write("Usage: uv run python examples/road_permit_remove.py <id>\n")
    sys.exit(1)

permit_id = args[0]
client = make_client()

print(f"=== RoadPermit.remove() - delete permit ID={permit_id} ===\n")

try:
    client.road_permit(RoadPermit.ROAD_PERMIT_ENVIRONMENT_TEST).remove(permit_id)
    print("Permit deleted.")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
