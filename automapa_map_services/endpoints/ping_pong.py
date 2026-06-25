from typing import TYPE_CHECKING

from automapa_map_services.response.api_response import ApiResponse

if TYPE_CHECKING:
    from automapa_map_services.client import ApiClient


class PingPong:
    def __init__(self, client: "ApiClient") -> None:
        self._client = client

    def ping(self, msg: str) -> ApiResponse:
        return self._client.call("PingPong", "ping", {"msg": msg})
