from typing import TYPE_CHECKING, Any

from automapa_map_services.response.api_response import ApiResponse

if TYPE_CHECKING:
    from automapa_map_services.client import ApiClient


class Speed:
    def __init__(self, client: "ApiClient") -> None:
        self._client = client

    def speedReport(
        self,
        obj_id: str,
        obj_name: str,
        obj_group: str,
        points: list[Any],
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {} if extra is None else extra
        return self._client.call(
            "Speed",
            "speedReport",
            {
                **_extra,
                "objID": obj_id,
                "objName": obj_name,
                "objGroup": obj_group,
                "points": points,
            },
        )

    def speed_report(
        self,
        obj_id: str,
        obj_name: str,
        obj_group: str,
        points: list[Any],
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        return self.speedReport(obj_id, obj_name, obj_group, points, extra)

    def speedReportResult(
        self,
        request_id: str,
        limit: int = 1,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {} if extra is None else extra
        return self._client.call(
            "Speed",
            "speedReportResult",
            {
                **_extra,
                "requestID": request_id,
                "limit": limit,
            },
        )

    def speed_report_result(
        self,
        request_id: str,
        limit: int = 1,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        return self.speedReportResult(request_id, limit, extra)
