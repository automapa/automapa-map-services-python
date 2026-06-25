from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from automapa_map_services.client import ApiClient

_COMPONENT_MAP: dict[str, str] = {
    "locality": "city",
    "route": "street",
    "street_number": "house",
    "postal_code": "pcode",
    "administrative_area_level_1": "province",
    "country": "country",
    "sublocality": "district",
    "neighborhood": "district",
}

_GOOGLE_ONLY_PARAMS: frozenset[str] = frozenset(
    ["address", "components", "language", "key", "region", "result_type", "location_type"]
)

_POSTAL_CODE_RE = re.compile(r"^(\d{2}-\d{3})\s+(.+)$")
_STREET_NUMBER_RE = re.compile(r"^(.+?)\s+(\d+\w*)$")


class GoogleGeocodeAdapter:
    """Drop-in adapter for apps currently using the Google Geocoding API.

    Accepts Google Geocoding API request params (address string, components filter)
    and returns a Google-format response dict - same shape as the real Google API.
    """

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def geocode(self, params: dict[str, Any]) -> dict[str, Any]:
        """Geocode using Google Geocoding API-compatible input and output.

        Accepted params:
          'address'    => str  - "Domaniewska 37, Warszawa" (best-effort parse)
          'address'    => dict - Automapa structured: {'city': 'Warszawa', ...}
          'components' => str  - "locality:Warszawa|route:Domaniewska|street_number:37"
          'language'   => str  - accepted, ignored
          'key'        => str  - accepted, ignored (SDK uses its own credentials)
          'maxResults' => int  - forwarded to Automapa API (default: 1)
        """
        address = self._resolve_address(params)
        forwarded = self._forwardable_params(params)
        max_results = int(forwarded.pop("maxResults", 1))
        extra = {**forwarded, "format": "google"}

        return cast(
            dict[str, Any],
            self._client.geocoder()
            .geocode(
                city=address.get("city", ""),
                country=address.get("country"),
                province=address.get("province"),
                district=address.get("district"),
                community=address.get("community"),
                quarter=address.get("quarter"),
                pcode=address.get("pcode"),
                street=address.get("street"),
                house=address.get("house"),
                max_results=max_results,
                extra=extra,
            )
            .data(),
        )

    def _resolve_address(self, params: dict[str, Any]) -> dict[str, Any]:
        if "components" in params and isinstance(params["components"], str):
            return self._parse_components(params["components"])

        if "address" in params and isinstance(params["address"], dict):
            return cast(dict[str, Any], params["address"])

        if "address" in params and isinstance(params["address"], str):
            return self._parse_address_string(params["address"])

        raise ValueError(
            'Either "address" (string or dict) or "components" (string) must be provided.'
        )

    def _parse_components(self, components: str) -> dict[str, str]:
        """Parse a Google components filter into an Automapa address dict.

        Input:  "locality:Warszawa|route:Domaniewska|street_number:37"
        Output: {'city': 'Warszawa', 'street': 'Domaniewska', 'house': '37'}
        """
        address: dict[str, str] = {}
        for part in components.split("|"):
            colon_pos = part.find(":")
            if colon_pos == -1:
                continue
            key = part[:colon_pos].strip()
            value = part[colon_pos + 1 :].strip()
            if key in _COMPONENT_MAP:
                address[_COMPONENT_MAP[key]] = value
        return address

    def _parse_address_string(self, address: str) -> dict[str, str]:
        """Best-effort parse a free-form address string into an Automapa address dict.

        Handles:
          "Domaniewska 37, Warszawa"
          "Domaniewska 37, 02-672 Warszawa"
          "Warszawa"
        """
        parts = [p.strip() for p in address.split(",")]

        if len(parts) == 1:
            return {"city": parts[0]}

        result: dict[str, str] = {}
        city_part = parts.pop().strip()

        m = _POSTAL_CODE_RE.match(city_part)
        if m:
            result["pcode"] = m.group(1)
            result["city"] = m.group(2)
        else:
            result["city"] = city_part

        if parts:
            street_part = parts[0].strip()
            m2 = _STREET_NUMBER_RE.match(street_part)
            if m2:
                result["street"] = m2.group(1).strip()
                result["house"] = m2.group(2)
            else:
                result["street"] = street_part

        return result

    def _forwardable_params(self, params: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in params.items() if k not in _GOOGLE_ONLY_PARAMS}
