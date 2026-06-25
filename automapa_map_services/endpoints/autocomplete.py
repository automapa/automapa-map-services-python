from typing import TYPE_CHECKING, Any

from automapa_map_services.response.api_response import ApiResponse

if TYPE_CHECKING:
    from automapa_map_services.client import ApiClient


class Autocomplete:
    def __init__(self, client: "ApiClient") -> None:
        self._client = client

    def search(
        self,
        query: str,
        types: list[str] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {} if extra is None else extra
        known = {k: v for k, v in {"query": query, "types": types}.items() if v is not None}
        return self._client.call("Autocomplete", "search", {**_extra, **known})

    def searchAddress(
        self,
        query: list[Any] | dict[str, Any],
        source: str,
        limit: int | None = None,
        selected: list[Any] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {} if extra is None else extra
        optional = {
            k: v for k, v in {"limit": limit, "selected": selected}.items() if v is not None
        }
        return self._client.call(
            "Autocomplete",
            "searchAddress",
            {
                **_extra,
                "query": query,
                "source": source,
                **optional,
            },
        )

    def search_address(
        self,
        query: list[Any] | dict[str, Any],
        source: str,
        limit: int | None = None,
        selected: list[Any] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        return self.searchAddress(query, source, limit, selected, extra)
