"""Example: Autocomplete.search_address() - step-by-step address search.

Usage:
    uv run python examples/autocomplete_search_address.py [--debug]

Useful for multi-field address forms: city → street → number → postcode.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automapa_map_services.exceptions import AutomapaException
from examples.bootstrap import make_client

client = make_client()

print("=== Autocomplete.search_address() - step-by-step address search ===\n")

try:
    response = client.autocomplete().search_address(
        query={
            "city": "Warszawa",
            "street": "Dom",  # partial street name
            "number": "",
            "zipcode": "02-672",
        },
        # source: field being searched: 'place', 'street', 'number', 'zipcode'
        source="street",
        selected=["city", "zipcode"],  # fields already confirmed by the user
        # limit=10,                    # optional: max results (default 10)
    )

    items = response.data().get("items", [])

    if not items:
        print("No results.")
        sys.exit(0)

    for item in items:
        city = item.get("city", "")
        street = item.get("street", "")
        zipcode = item.get("zipcode", "")
        count = item.get("count", "")
        print(f"  {city}, {street}  [{zipcode}]  (number count: {count})")

except AutomapaException as e:
    sys.stderr.write(f"API error: {e}\n")
    sys.exit(1)
