from typing import TYPE_CHECKING, Any

from automapa_map_services.response.api_response import ApiResponse

if TYPE_CHECKING:
    from automapa_map_services.client import ApiClient


class Geocoder:
    def __init__(self, client: "ApiClient") -> None:
        self._client = client

    def geocode(
        self,
        city: str,
        country: str | None = None,
        province: str | None = None,
        district: str | None = None,
        community: str | None = None,
        quarter: str | None = None,
        pcode: str | None = None,
        street: str | None = None,
        house: str | None = None,
        max_results: int | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {} if extra is None else extra
        address = {
            k: v
            for k, v in {
                "city": city,
                "country": country,
                "province": province,
                "district": district,
                "community": community,
                "quarter": quarter,
                "pcode": pcode,
                "street": street,
                "house": house,
            }.items()
            if v is not None and v != ""
        }
        params: dict[str, Any] = {}
        if address:
            params["address"] = address
        if max_results is not None:
            params["maxResults"] = max_results
        return self._client.call("Geocoder", "geocode", {**_extra, **params})

    def geocodemulti(
        self,
        addresses: list[Any],
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {} if extra is None else extra
        return self._client.call("Geocoder", "geocodemulti", {**_extra, "addresses": addresses})

    def revgeocode(
        self,
        point: list[float] | dict[str, float],
        snap_to_bld: bool | None = None,
        snap_to_bld_radius: int | None = None,
        get_postal_code: bool | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {} if extra is None else extra
        rev_params = {
            k: v
            for k, v in {
                "snapToBld": snap_to_bld,
                "snapToBldRadius": snap_to_bld_radius,
                "getPostalCode": get_postal_code,
            }.items()
            if v is not None
        }
        known: dict[str, Any] = {"point": point}
        if rev_params:
            known["params"] = rev_params
        return self._client.call("Geocoder", "revgeocode", {**_extra, **known})

    def revgeocodemulti(
        self,
        points: list[Any],
        snap_to_bld: bool | None = None,
        snap_to_bld_radius: int | None = None,
        get_postal_code: bool | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ApiResponse:
        _extra: dict[str, Any] = {} if extra is None else extra
        rev_params = {
            k: v
            for k, v in {
                "snapToBld": snap_to_bld,
                "snapToBldRadius": snap_to_bld_radius,
                "getPostalCode": get_postal_code,
            }.items()
            if v is not None
        }
        known: dict[str, Any] = {"points": points, "params": rev_params}
        return self._client.call("Geocoder", "revgeocodemulti", {**_extra, **known})
