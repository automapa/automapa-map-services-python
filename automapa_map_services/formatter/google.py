from typing import Any


class GoogleFormatter:
    _GEOCODING_METHODS = frozenset(
        [
            "Geocoder.geocode",
            "Geocoder.geocodemulti",
            "Geocoder.revgeocode",
            "Geocoder.revgeocodemulti",
            "Autocomplete.search",
            "Autocomplete.searchAddress",
        ]
    )

    def format(self, raw: dict[str, Any], method: str) -> dict[str, Any]:
        if method not in self._GEOCODING_METHODS:
            return {**raw, "_raw": raw}

        result = raw.get("result")

        if not result:
            return {"status": "ZERO_RESULTS", "results": [], "_raw": raw}

        results = self._map_results(result, method)

        if not results:
            return {"status": "ZERO_RESULTS", "results": [], "_raw": raw}

        return {"status": "OK", "results": results, "_raw": raw}

    def _map_results(self, result: Any, method: str) -> list[dict[str, Any]]:
        if not isinstance(result, dict) and not isinstance(result, list):
            return []

        if isinstance(result, dict) and "items" in result and isinstance(result["items"], list):
            return [self._map_single_result(item) for item in result["items"]]

        if "multi" in method:
            return self._map_multi_results(result)

        if isinstance(result, dict) and ("x" in result or "y" in result or "city" in result):
            return [self._map_single_result(result)]

        if isinstance(result, list):
            return [self._map_single_result(item) for item in result if isinstance(item, dict)]

        return [self._map_single_result(result)]

    def _map_multi_results(self, items: Any) -> list[dict[str, Any]]:
        if not isinstance(items, list):
            return []

        mapped: list[dict[str, Any]] = []

        for item in items:
            if not isinstance(item, dict) and not isinstance(item, list):
                continue

            if isinstance(item, dict):
                if item.get("status") == "ERROR":
                    mapped.append({"status": "ERROR", "message": str(item.get("message", ""))})
                    continue

                if "x" in item or "y" in item or "city" in item:
                    mapped.append(self._map_single_result(item))
                else:
                    for sub in item.values():
                        if isinstance(sub, dict):
                            mapped.append(self._map_single_result(sub))
            elif isinstance(item, list):
                for sub in item:
                    if isinstance(sub, dict):
                        mapped.append(self._map_single_result(sub))

        return mapped

    def _map_single_result(self, result: dict[str, Any]) -> dict[str, Any]:
        if "coords" in result and isinstance(result["coords"], dict):
            return self._map_autocomplete_result(result)

        return {
            "formatted_address": self._build_formatted_address(result),
            "address_components": self._build_address_components(result),
            "geometry": {
                "location": {
                    "lat": float(result["y"]) if result.get("y") is not None else None,
                    "lng": float(result["x"]) if result.get("x") is not None else None,
                },
                "viewport": None,
            },
            "place_id": None,
            "types": [self._quality_to_type(int(result.get("quality", 0)))],
        }

    def _map_autocomplete_result(self, result: dict[str, Any]) -> dict[str, Any]:
        coords = result["coords"]
        lat = float(coords["y"]) if coords.get("y") is not None else None
        lng = float(coords["x"]) if coords.get("x") is not None else None

        subtype = result.get("subtype") or result.get("type") or "place"

        return {
            "formatted_address": self._build_autocomplete_formatted_address(result),
            "address_components": self._build_autocomplete_address_components(result),
            "geometry": {
                "location": {"lat": lat, "lng": lng},
                "viewport": None,
            },
            "place_id": None,
            "types": [str(subtype)],
        }

    def _build_formatted_address(self, result: dict[str, Any]) -> str:
        parts: list[str] = []

        if "street" in result:
            street_part = str(result["street"])
            if "house" in result:
                street_part += " " + str(result["house"])
            parts.append(street_part)

        pcode = str(result["pcode"]) if "pcode" in result else ""
        city = str(result["city"]) if "city" in result else ""

        if pcode and city:
            parts.append(f"{pcode} {city}")
        elif city:
            parts.append(city)

        if "country" in result:
            parts.append(str(result["country"]))

        return ", ".join(parts)

    def _build_address_components(self, result: dict[str, Any]) -> list[dict[str, Any]]:
        components: list[dict[str, Any]] = []

        if "street" in result:
            components.append(self._component(str(result["street"]), ["route"]))
        if "house" in result:
            components.append(self._component(str(result["house"]), ["street_number"]))
        if "city" in result:
            components.append(self._component(str(result["city"]), ["locality", "political"]))
        if "pcode" in result:
            components.append(self._component(str(result["pcode"]), ["postal_code"]))
        if "province" in result:
            components.append(
                self._component(
                    str(result["province"]),
                    ["administrative_area_level_1", "political"],
                )
            )
        if "district" in result:
            components.append(
                self._component(str(result["district"]), ["sublocality", "political"])
            )
        if "country" in result:
            components.append(self._component(str(result["country"]), ["country", "political"]))

        return components

    def _build_autocomplete_formatted_address(self, result: dict[str, Any]) -> str:
        parts: list[str] = []

        if "street" in result:
            street_part = str(result["street"])
            if "number" in result:
                street_part += " " + str(result["number"])
            parts.append(street_part)

        city = str(result.get("place") or result.get("city") or "")
        pcode = str(result.get("postal_code") or result.get("zipcode") or "")

        if pcode and city:
            parts.append(f"{pcode} {city}")
        elif city:
            parts.append(city)

        return ", ".join(parts)

    def _build_autocomplete_address_components(
        self, result: dict[str, Any]
    ) -> list[dict[str, Any]]:
        components: list[dict[str, Any]] = []

        if "street" in result:
            components.append(self._component(str(result["street"]), ["route"]))
        if "number" in result:
            components.append(self._component(str(result["number"]), ["street_number"]))

        city = str(result.get("place") or result.get("city") or "")
        if city:
            components.append(self._component(city, ["locality", "political"]))

        pcode = str(result.get("postal_code") or result.get("zipcode") or "")
        if pcode:
            components.append(self._component(pcode, ["postal_code"]))

        if "province" in result:
            components.append(
                self._component(
                    str(result["province"]),
                    ["administrative_area_level_1", "political"],
                )
            )
        if "district" in result:
            components.append(
                self._component(str(result["district"]), ["sublocality", "political"])
            )

        return components

    def _component(self, name: str, types: list[str]) -> dict[str, Any]:
        return {"long_name": name, "short_name": name, "types": types}

    def _quality_to_type(self, quality: int) -> str:
        if quality <= 2:
            return "country"
        if quality == 3:
            return "administrative_area_level_1"
        if quality <= 5:
            return "locality"
        if quality <= 7:
            return "route"
        return "street_address"
