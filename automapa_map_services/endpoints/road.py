from typing import TYPE_CHECKING, Any

from automapa_map_services.response.api_response import ApiResponse

if TYPE_CHECKING:
    from automapa_map_services.client import ApiClient


class Road:
    def __init__(self, client: "ApiClient") -> None:
        self._client = client

    def getSegmentInfo(self, params: dict[str, Any]) -> ApiResponse:
        return self._client.call("Road", "getSegmentInfo", params)

    def get_segment_info(self, params: dict[str, Any]) -> ApiResponse:
        return self.getSegmentInfo(params)

    def speedCheck(self, params: dict[str, Any]) -> ApiResponse:
        return self._client.call("Road", "speedCheck", params)

    def speed_check(self, params: dict[str, Any]) -> ApiResponse:
        return self.speedCheck(params)

    def speedCheckMulti(self, params: dict[str, Any]) -> ApiResponse:
        return self._client.call("Road", "speedCheckMulti", params)

    def speed_check_multi(self, params: dict[str, Any]) -> ApiResponse:
        return self.speedCheckMulti(params)
