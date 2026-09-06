import hashlib
import json
from typing import Any

from automapa_map_services.config import Config
from automapa_map_services.exceptions import ExceptionMapper
from automapa_map_services.http.builder import RequestBuilder
from automapa_map_services.http.client import HttpClientProtocol
from automapa_map_services.session.storage import SessionStorageProtocol


def hash_password(password: str, salt: str) -> str:
    """Return the credential expected by ``generateSession``: ``md5(md5(password) + salt)``."""
    return hashlib.md5((hashlib.md5(password.encode()).hexdigest() + salt).encode()).hexdigest()


class SessionManager:
    _NO_SESSION_METHODS = frozenset(["Session.getSalt", "Session.generateSession"])

    def __init__(
        self,
        config: Config,
        http_client: HttpClientProtocol,
        storage: SessionStorageProtocol,
    ) -> None:
        self._config = config
        self._http_client = http_client
        self._storage = storage
        self._request_builder = RequestBuilder(config.base_url, config.version)
        self._exception_mapper = ExceptionMapper()

    def requires_session(self, service: str, method: str) -> bool:
        return f"{service}.{method}" not in self._NO_SESSION_METHODS

    def ensure_session(self) -> str:
        session_id = self._storage.get()
        if session_id is not None:
            return session_id
        return self._init_session()

    def clear_session(self) -> None:
        self._storage.clear()

    def _init_session(self) -> str:
        salt_body = self._make_call("Session", "getSalt", {"key": self._config.key})
        salt = str(salt_body.get("result", {}).get("salt", ""))

        pass_hash = hash_password(self._config.password, salt)

        session_body = self._make_call(
            "Session",
            "generateSession",
            {"key": self._config.key, "pass": pass_hash},
        )
        session_id = str(session_body.get("result", {}).get("sessionId", ""))

        self._storage.store(session_id)
        return session_id

    def _make_call(self, service: str, method: str, params: dict[str, Any]) -> dict[str, Any]:
        request = self._request_builder.build(service, method, params)
        response = self._http_client.send(request)

        decoded = json.loads(response.body)
        body: dict[str, Any] = decoded if isinstance(decoded, dict) else {}

        if not response.is_success:
            raise self._exception_mapper.from_http_response(response.status_code, body)

        return body
