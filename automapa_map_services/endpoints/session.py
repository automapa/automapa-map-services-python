from typing import TYPE_CHECKING

from automapa_map_services.response.api_response import ApiResponse

if TYPE_CHECKING:
    from automapa_map_services.client import ApiClient


class Session:
    def __init__(self, client: "ApiClient") -> None:
        self._client = client

    def getSalt(self, key: str) -> ApiResponse:
        return self._client.call("Session", "getSalt", {"key": key})

    def get_salt(self, key: str) -> ApiResponse:
        return self.getSalt(key)

    def generateSession(self, key: str, pass_: str) -> ApiResponse:
        return self._client.call("Session", "generateSession", {"key": key, "pass": pass_})

    def generate_session(self, key: str, pass_: str) -> ApiResponse:
        return self.generateSession(key, pass_)
