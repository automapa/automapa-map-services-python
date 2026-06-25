from typing import Any


class FormatterRegistry:
    def __init__(self) -> None:
        self._formatters: dict[str, Any] = {}

    def register(self, name: str, formatter: Any) -> None:
        self._formatters[name] = formatter

    def get(self, name: str) -> Any:
        if not self.has(name):
            available = ", ".join(self._formatters.keys())
            raise KeyError(f'Formatter "{name}" is not registered. Available: {available}')
        return self._formatters[name]

    def has(self, name: str) -> bool:
        return name in self._formatters
