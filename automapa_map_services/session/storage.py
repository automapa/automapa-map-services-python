from typing import Protocol


class SessionStorageProtocol(Protocol):
    def get(self) -> str | None: ...
    def store(self, session_id: str) -> None: ...
    def clear(self) -> None: ...


class InMemorySessionStorage:
    def __init__(self) -> None:
        self._session_id: str | None = None

    def get(self) -> str | None:
        return self._session_id

    def store(self, session_id: str) -> None:
        self._session_id = session_id

    def clear(self) -> None:
        self._session_id = None
