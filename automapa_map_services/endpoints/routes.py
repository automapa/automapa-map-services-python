from __future__ import annotations

from typing import TYPE_CHECKING, Any

from automapa_map_services.response.api_response import ApiResponse

if TYPE_CHECKING:
    from automapa_map_services.client import ApiClient


class Routes:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def matrix(
        self,
        points: list[Any],
        type: int,
        precise: bool = False,
        simple: bool = False,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {} if extra is None else extra
        return self._client.call(
            "Routes",
            "matrix",
            {
                **_extra,
                "points": points,
                "type": type,
                "precise": precise,
                "simple": simple,
            },
        )

    def optimize(
        self,
        points: list[Any],
        type: int,
        fixed_end: bool = True,
        route: list[Any] | None = None,
        object: dict[str, Any] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {} if extra is None else extra
        optional = {k: v for k, v in {"route": route, "object": object}.items() if v is not None}
        return self._client.call(
            "Routes",
            "optimize",
            {
                **_extra,
                "points": points,
                "type": type,
                "fixedEnd": fixed_end,
                **optional,
            },
        )

    def optimizeQueue(
        self,
        points: list[Any] | dict[str, Any],
        optimize_by: str | None = None,
        fixed_end: bool = True,
        route: list[Any] | None = None,
        object: dict[str, Any] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {} if extra is None else extra
        if isinstance(points, dict):
            return self._client.call("Routes", "optimizeQueue", {**_extra, **points})
        if optimize_by is None:
            raise TypeError("optimizeQueue() missing required argument: 'optimize_by'")
        optional = {k: v for k, v in {"route": route, "object": object}.items() if v is not None}
        return self._client.call(
            "Routes",
            "optimizeQueue",
            {
                **_extra,
                "points": points,
                "optimizeBy": optimize_by,
                "fixedEnd": fixed_end,
                **optional,
            },
        )

    def optimize_queue(
        self,
        points: list[Any],
        optimize_by: str,
        fixed_end: bool = True,
        route: list[Any] | None = None,
        object: dict[str, Any] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        return self.optimizeQueue(points, optimize_by, fixed_end, route, object, extra)

    def optimizeQueueResult(
        self,
        request_id: str | dict[str, Any],
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {} if extra is None else extra
        if isinstance(request_id, dict):
            return self._client.call("Routes", "optimizeQueueResult", {**_extra, **request_id})
        return self._client.call(
            "Routes",
            "optimizeQueueResult",
            {
                **_extra,
                "requestId": request_id,
            },
        )

    def optimize_queue_result(
        self,
        request_id: str,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        return self.optimizeQueueResult(request_id, extra)

    def route(
        self,
        points: list[Any],
        route: list[Any] | dict[str, Any],
        object: dict[str, Any],
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {} if extra is None else extra
        return self._client.call(
            "Routes",
            "route",
            {
                **_extra,
                "points": points,
                "route": route,
                "object": object,
            },
        )
