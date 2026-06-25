"""Example: Speed.speed_report_result() - poll for speed report results.

Usage:
    uv run python examples/speed_report_result.py <requestId> [--debug]

Run examples/speed_report.py first to obtain a requestId.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

args = [a for a in sys.argv[1:] if not a.startswith("--")]
if not args:
    sys.stderr.write("Usage: uv run python examples/speed_report_result.py <requestId>\n")
    sys.exit(1)

request_id = args[0]
client = make_client()

print(f"=== Speed.speed_report_result() - results requestId={request_id} ===\n")

max_attempts = 15
for attempt in range(1, max_attempts + 1):
    try:
        response = client.speed().speed_report_result(request_id=request_id)
        data = response.data()

        if data.get("resultReady") is True:
            violations = data.get("violations", [])
            print(f"Done after attempt {attempt}.")
            if violations:
                print(f"Speed violations: {len(violations)}")
                for v in violations:
                    t = v.get("t")
                    limit = v.get("speed")
                    actual = v.get("actual")
                    print(f"  t={t}  limit={limit} km/h  actual={actual} km/h")
            else:
                print("No speed violations.")
            break

        print(f"  Attempt {attempt}/{max_attempts}: result not ready...")
        time.sleep(2)

    except AutomapaException as e:
        sys.stderr.write(f"API error: {e}\n")
        sys.exit(1)
else:
    print("Timeout waiting for result.")
