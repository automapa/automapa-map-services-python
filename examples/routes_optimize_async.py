"""Example: Routes.optimize_queue() + optimize_queue_result().

Asynchronous route optimisation (max 50 points).

Usage:
    uv run python examples/routes_optimize_async.py [--debug]
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== Routes.optimize_queue() - asynchronous optimisation ===\n")

# Each point requires an 'id' field
points = [
    {"id": "Warszawa", "x": 21.0073642, "y": 52.2297},
    {"id": "Gdańsk", "x": 18.6282, "y": 54.3520},
    {"id": "Kraków", "x": 19.9449800, "y": 50.0646},
    {"id": "Wrocław", "x": 17.0385, "y": 51.1079},
    {"id": "Poznań", "x": 16.9252, "y": 52.4064},
    {"id": "Łódź", "x": 19.4560, "y": 51.7592},
]

try:
    # Step 1: submit the optimisation job
    submit = client.routes().optimize_queue(
        {
            "points": points,
            "optimizeBy": "time",  # 'time' or 'distance'
            "object": {"type": "car"},
        }
    )

    request_id = submit.data().get("requestId", "")
    print(f"Job submitted. requestId: {request_id}\n")

    # Step 2: poll for the result
    max_attempts = 15
    for attempt in range(1, max_attempts + 1):
        time.sleep(2)
        result = client.routes().optimize_queue_result({"requestId": request_id})
        data = result.data()

        if data.get("resultReady") is True:
            sequence = data.get("optimizedSequence", [])
            print(f"Done after {attempt * 2}s!")
            print(f"Optimal sequence: {' → '.join(str(s) for s in sequence)}")
            break
        print(f"  Attempt {attempt}/{max_attempts}: result not ready...")
    else:
        print("Timeout waiting for result.")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
