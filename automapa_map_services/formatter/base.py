from typing import Any, Protocol


class FormatterProtocol(Protocol):
    def format(self, raw: dict[str, Any], method: str) -> dict[str, Any]: ...
