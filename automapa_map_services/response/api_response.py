from typing import Any


class ApiResponse:
    def __init__(
        self,
        raw: dict[str, Any],
        status_code: int,
        formatted_data: Any | None = None,
        meta: dict[str, object] | None = None,
    ) -> None:
        self._raw = raw
        self._status_code = status_code
        self._formatted_data = formatted_data
        self._meta: dict[str, object] = meta if meta is not None else {}

    def raw(self) -> dict[str, Any]:
        return self._raw

    def data(self) -> Any:
        if self._formatted_data is not None:
            return self._formatted_data
        return self._raw.get("result", self._raw)

    def status(self) -> int:
        return self._status_code

    def meta(self) -> dict[str, object]:
        return self._meta
