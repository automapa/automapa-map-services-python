import builtins
from typing import TYPE_CHECKING, Any

from automapa_map_services.response.api_response import ApiResponse

if TYPE_CHECKING:
    from automapa_map_services.client import ApiClient


class RoadPermit:
    ROAD_PERMIT_ENVIRONMENT_PROD = "prod"
    ROAD_PERMIT_ENVIRONMENT_TEST = "test"
    ROAD_PERMIT_ENABLED_ENVIRONMENTS = [
        ROAD_PERMIT_ENVIRONMENT_PROD,
        ROAD_PERMIT_ENVIRONMENT_TEST,
    ]

    def __init__(
        self,
        client: "ApiClient",
        environment: str = ROAD_PERMIT_ENVIRONMENT_PROD,
    ) -> None:
        self._client = client
        self._environment = environment

    def list(
        self,
        id: str | None = None,
        document_name: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {} if extra is None else extra
        known = {
            k: v for k, v in {"id": id, "document_name": document_name}.items() if v is not None
        }
        return self._client.call(
            "RoadPermit",
            "list",
            {
                **_extra,
                "enviroment": self._environment,
                **known,
            },
        )

    def add(
        self,
        permissions: builtins.list[Any] | dict[str, Any],
        poly: dict[str, Any] | builtins.list[Any],
        date_start: str | None = None,
        date_end: str | None = None,
        description: str | None = None,
        document_name: str | None = None,
        location: str | None = None,
        is_valid_after_expiry: bool | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        if not permissions:
            raise ValueError("permissions is required and must not be empty")
        if not poly:
            raise ValueError("poly is required and must not be empty")
        _extra: dict[str, Any] = {} if extra is None else extra
        optional = {
            k: v
            for k, v in {
                "date_start": date_start,
                "date_end": date_end,
                "description": description,
                "document_name": document_name,
                "location": location,
                "is_valid_after_expiry": is_valid_after_expiry,
            }.items()
            if v is not None
        }
        params = {
            **_extra,
            "permissions": permissions,
            "poly": poly,
            "enviroment": self._environment,
            **optional,
        }
        if "id" in params and params["id"] is None:
            del params["id"]
        endpoint = "overwrite" if "id" in params else "add"
        return self._client.call("RoadPermit", endpoint, params)

    def overwrite(
        self,
        id: str,
        permissions: builtins.list[Any] | dict[str, Any],
        poly: dict[str, Any] | builtins.list[Any],
        date_start: str | None = None,
        date_end: str | None = None,
        description: str | None = None,
        document_name: str | None = None,
        location: str | None = None,
        is_valid_after_expiry: bool | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {"id": id, **(extra if extra is not None else {})}
        return self.add(
            permissions,
            poly,
            date_start,
            date_end,
            description,
            document_name,
            location,
            is_valid_after_expiry,
            extra=_extra,
        )

    def remove(self, id: str) -> ApiResponse:
        return self._client.call(
            "RoadPermit",
            "remove",
            {"id": id, "enviroment": self._environment},
        )
