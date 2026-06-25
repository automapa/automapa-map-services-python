import json
from pathlib import Path
from typing import Any

_FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def load_fixture(name: str) -> dict[str, Any]:
    """Load a JSON fixture by filename (with or without .json extension)."""
    if not name.endswith(".json"):
        name = f"{name}.json"
    path = _FIXTURES_DIR / name
    with path.open(encoding="utf-8") as f:
        result = json.load(f)
    if not isinstance(result, dict):
        raise TypeError(f"Fixture {name} must be a JSON object, got {type(result).__name__}")
    return result


def load_fixture_raw(name: str) -> Any:
    """Load a JSON fixture without requiring it to be a dict."""
    if not name.endswith(".json"):
        name = f"{name}.json"
    path = _FIXTURES_DIR / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def fixture_body(name: str) -> str:
    """Return raw JSON string of a fixture file (for use with MockHttpClient)."""
    if not name.endswith(".json"):
        name = f"{name}.json"
    path = _FIXTURES_DIR / name
    return path.read_text(encoding="utf-8")
