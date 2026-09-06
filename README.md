# Automapa Map Services Python SDK

> European Geocoding, Routing & Address Autocomplete

[![Python Versions](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Python SDK for the Automapa Map Services REST API. Simplifies integration with geocoding, routing, and address autocomplete services for Europe.

---

## Getting started with your `.env` file

You will receive a `.env` file from us containing your API credentials. Place it in the root directory of this repository:

```
AUTOMAPA_API_KEY=your-key
AUTOMAPA_API_PASSWORD=your-password
```

Once the `.env` file is in place, you can **test all endpoints against the live API using Docker** — no local Python installation required:

```bash
# Run the full test suite (unit + integration) inside Docker
make docker-test

# Run only integration tests (live API calls)
make docker-test-integration

# Run only unit tests (no API calls)
make docker-test-unit

# Run all checks (unit, integration, lint, type checks)
make docker-check
```

> **Zero dependencies.** The SDK has no runtime dependencies — it uses only Python's built-in `urllib`. It is compatible with **Python 3.11 and above**.

---

## 1. Overview

The SDK covers:

- **Geocoding** — convert an address to coordinates and back
- **Routing** — calculate routes, distance matrices, and point-order optimization
- **Address autocomplete** — suggestions as the user types
- **Google Geocoding API compatibility** — optional `google` response format

For the full list of endpoints and parameters, see the [Automapa REST API documentation](https://docs.automapa.pl/wiki/external/view/AM/API_REST/services/).

---

## 2. Installation

```bash
pip install automapa-map-services
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add automapa-map-services
```

Requirements: Python 3.11+, no external runtime dependencies.

---

## 3. Client configuration

```python
from automapa_map_services import ApiClient, Config

client = ApiClient(Config(
    key="YOUR_API_KEY",
    password="YOUR_PASSWORD",
))
```

---

## 4. Session handling

A session is opened automatically (lazy) on the first call that requires authorization.
To open it manually (fetches a salt, hashes the configured password and stores the session id
for subsequent calls):

```python
session_id = client.open_session()
```

Sessions opened through `Session.login()` / `generate_session()` are **not** stored in the
client; use `client.open_session()` when you want the client itself to reuse the session.

---

## 5. Available services

| Class | Methods |
|-------|---------|
| `Geocoder` | `geocode()`, `geocodemulti()`, `revgeocode()`, `revgeocodemulti()` |
| `Autocomplete` | `search()`, `search_address()` |
| `Road` | `get_segment_info()`, `speed_check()`, `speed_check_multi()` |
| `RoadPermit` | `add()`, `overwrite()`, `remove()`, `list()` |
| `Routes` | `matrix()`, `optimize()`, `optimize_queue()`, `optimize_queue_result()`, `route()` |
| `Speed` | `speed_report()`, `speed_report_result()` |

All methods also accept camelCase aliases (`searchAddress()`, `getSegmentInfo()`, etc.) for consistency with the PHP SDK.

### Geocoder

```python
# Address → coordinates
response = client.geocoder().geocode({
    "address":    {"city": "Warsaw", "street": "Domaniewska", "house": "37"},
    "maxResults": 1,
})
results = response.data()  # list of results, each with x, y, city, street, ...

# Reverse geocoding — coordinates → address
response = client.geocoder().revgeocode({
    "point":  [21.0073642, 52.18288],
    "params": {},
})
address = response.data()  # city, street, house, pcode, ...
```

### Autocomplete

Address and POI autocomplete — returns suggestions as the user types.

#### `search()` — search by phrase

```python
response = client.autocomplete().search({
    "query": "Warsaw Domaniewska 37",
    # "types": ["place"],  # optional: "place", "poi", or both
})

items = response.data()["items"]

for item in items:
    print(item["name"])          # "Domaniewska 37, 02-672 Warsaw"
    print(item["type"])          # "place"
    print(item["subtype"])       # "building"
    print(item["coords"]["x"])   # longitude (lng)
    print(item["coords"]["y"])   # latitude (lat)
```

Each `items` entry contains: `type`, `subtype`, `name`, `province`, `district`, `community`,
`place`, `quarter`, `street`, `number`, `postal_code`, `coords.{x,y}`.

#### `search_address()` — step-by-step address search

Useful for multi-field address forms (city → street → number → postcode).

```python
response = client.autocomplete().search_address({
    "query": {
        "city":    "Warsaw",
        "street":  "Dom",     # partial street name
        "number":  "",
        "zipcode": "02-672",
    },
    "source":   "street",              # field being searched: "place", "street", "number", "zipcode"
    "selected": ["city", "zipcode"],   # fields already confirmed by the user
    # "limit": 10,                     # optional: max results (default 10)
})

items = response.data()["items"]
# [{"city": "Warsaw", "street": "Domaniewska", "zipcode": "02-672", "count": 1}]
```

Each entry may contain: `city`, `street`, `number`, `zipcode`, `count`, and optionally `coords.{x,y}`.

> **Note on Autocomplete coordinates:** Unlike `Geocoder`, coordinates are nested:
> `coords.x` = longitude, `coords.y` = latitude.

### Routes

Route calculation, distance matrix, and point-order optimisation.

#### `route()` — calculate a route

```python
response = client.routes().route({
    "points": [
        {"x": 21.0073642, "y": 52.2297},  # Warsaw (x=lng, y=lat)
        {"x": 18.6282,    "y": 54.3520},  # Gdańsk
    ],
    "route": {
        "type":    "short",  # "quick" | "short" | "optimal"
        "traffic": True,     # True = take live traffic into account
    },
    "object": {"type": "car"},
})

data = response.data()
print(round(data["length"] / 1000, 1), "km")
import time; print(time.strftime("%H:%M:%S", time.gmtime(data["eta"])))  # estimated travel time
print(data["mapurl"])   # link to map
# data["desc"]  — turn-by-turn manoeuvre list
# data["tolls"] — toll charges
```

#### `matrix()` — distance / time matrix

```python
response = client.routes().matrix({
    "points": [
        {"x": 21.0073642, "y": 52.2297},
        {"x": 18.6282,    "y": 54.3520},
        {"x": 16.9252,    "y": 52.4064},
    ],
    "type": 1,  # 1 = time (duration in minutes), 2 = distance (length in metres)
})

for row in response.data():
    print(f"Segment {row['points']}: {round(row['length'] / 1000)} km, {row['duration']} min")
```

#### `optimize()` — synchronous optimisation (max 10 points)

```python
response = client.routes().optimize({
    "points":   [{"x": 21.0, "y": 52.2}, {"x": 18.6, "y": 54.4}],
    "type":     1,      # 1 = time, 2 = distance
    "fixedEnd": False,  # True = last point is the destination; False = return to start
    "object":   {"type": "car"},
})

data = response.data()
data["order"]    # optimal index sequence, e.g. "0,3,2,1"
data["sections"] # segment details: x, y, eta, dist
```

#### `optimize_queue()` + `optimize_queue_result()` — asynchronous optimisation (max 50 points)

```python
import time

# Step 1: submit — each point requires an "id" field
response   = client.routes().optimize_queue({
    "points":     [{"id": "Warsaw", "x": 21.0, "y": 52.2}],
    "optimizeBy": "time",  # "time" or "distance"
    "object":     {"type": "car"},
})
request_id = response.data()["requestId"]

# Step 2: poll for the result
while True:
    time.sleep(2)
    result = client.routes().optimize_queue_result({"requestId": request_id})
    data   = result.data()
    if data["resultReady"] is True:
        break

data["optimizedSequence"]  # list of point IDs in the optimal order
```

---

## 6. Examples

```bash
# Copy configuration
cp .env.example .env
# Fill in AUTOMAPA_API_KEY and AUTOMAPA_API_PASSWORD in .env

# Routes
python examples/routes_route.py                # point-to-point route
python examples/routes_matrix.py               # distance/time matrix
python examples/routes_optimize.py             # sync optimisation (max 10 points)
python examples/routes_optimize_async.py       # async optimisation (max 50 points)

# Geocoder
python examples/geocoder_geocode.py            # single address → coordinates
python examples/geocoder_geocodemulti.py       # batch address geocoding
python examples/geocoder_revgeocode.py         # coordinates → single address
python examples/geocoder_revgeocodemulti.py    # coordinates → multiple addresses

# Autocomplete
python examples/autocomplete_search.py         # search places and POI by phrase
python examples/autocomplete_search_address.py # search address objects

# Road
python examples/road_segment_info.py           # road segment metadata
python examples/road_speed_check.py            # speed limit for a single point
python examples/road_speed_check_multi.py      # speed limits for multiple points

# Road permits
python examples/road_permit_list.py            # list permits
python examples/road_permit_add.py             # create a new permit
python examples/road_permit_overwrite.py <id>  # replace an existing permit
python examples/road_permit_remove.py <id>     # delete a permit

# Speed reports
python examples/speed_report.py                # submit async speed report
python examples/speed_report_result.py <id>    # poll for report results
```

Or simply run `make examples` to run all examples.

---

## 7. Passing additional parameters

The SDK does not restrict unknown parameters — all fields are forwarded to the API as-is:

```python
client.geocoder().geocode({
    "address":       {"city": "Warsaw"},
    "myCustomParam": "value",  # passed through without modification
})
```

---

## 8. Low-level `call()` and `request()`

```python
# Via service + method name (preferred)
client.call("Geocoder", "newMethod", {"param": "value"})

# Or via full URL path (fallback)
client.request("POST", "/v3/Geocoder/newMethod", {"param": "value"})
```

---

## 9. Response formats: `native` vs `google`

```python
# Native format (default)
response = client.geocoder().geocode({"address": {"city": "Kraków"}})
data = response.data()   # API data
raw  = response.raw()    # full raw response (always available)

# Google format
response = client.geocoder().geocode({
    "address": {"city": "Kraków"},
    "format":  "google",
})
```

---

## 10. Google format field limitations

| Google field | Value |
|---|---|
| `geometry.viewport` | always `null` (not provided by the API) |
| `place_id` | always `null` (not provided by the API) |

> **Note:** The Automapa API uses `x` = longitude and `y` = latitude — the opposite of Google's convention.

---

## 11. Error handling

| Situation | Exception class |
|-----------|----------------|
| Invalid API key / password | `AuthenticationException` |
| Expired session | `SessionException` |
| Parameter validation failure | `ValidationException` |
| Resource not found | `NotFoundException` |
| Rate limit exceeded | `RateLimitException` |
| Network / urllib error | `NetworkException` |
| Server error (5xx) | `ServerException` |
| Unexpected response | `UnknownResponseException` |

```python
from automapa_map_services.exceptions import AuthenticationException, AutomapaException

try:
    response = client.geocoder().geocode({"address": {"city": "Warsaw"}})
except AuthenticationException as e:
    print("Authentication error:", e)
except AutomapaException as e:
    print("API error:", e)
```

---

## License

[MIT](LICENSE) © 2026 Automapa sp. z o.o.
