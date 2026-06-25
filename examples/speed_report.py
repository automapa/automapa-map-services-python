"""Example: Speed.speed_report() - submit an asynchronous speed report.

Usage:
    uv run python examples/speed_report.py [--debug]

The script submits a report and prints the requestId for polling results.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== Speed.speed_report() - submitting speed report ===\n")

now = int(time.time())

# Tracked vehicle route (Unix timestamp, x=lng, y=lat)
track_points = [
    {"t": now - 300, "x": 21.0073642, "y": 52.2297},
    {"t": now - 240, "x": 21.0200000, "y": 52.2350},
    {"t": now - 180, "x": 21.0350000, "y": 52.2400},
    {"t": now - 120, "x": 21.0500000, "y": 52.2450},
    {"t": now - 60, "x": 21.0650000, "y": 52.2500},
]

try:
    response = client.speed().speed_report(
        obj_id="test-vehicle-001",
        obj_name="Test Vehicle",
        obj_group="TestGroup",
        points=track_points,
    )

    request_id = response.data().get("requestId", "")
    print(f"Report submitted. requestId: {request_id}")
    print(f"\nTo fetch results:\n  uv run python examples/speed_report_result.py {request_id}")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
