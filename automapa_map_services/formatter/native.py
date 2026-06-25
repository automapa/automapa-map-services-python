from typing import Any


class NativeFormatter:
    def format(self, raw: dict[str, Any], method: str) -> dict[str, Any]:
        result = raw.get("result", raw)

        if not isinstance(result, dict):
            return {"data": result, "_raw": raw}

        output = dict(result)
        output["_raw"] = raw
        return output
