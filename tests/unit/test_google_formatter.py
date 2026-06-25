import pytest

from automapa_map_services.formatter.google import GoogleFormatter


@pytest.fixture()
def formatter() -> GoogleFormatter:
    return GoogleFormatter()


def test_maps_geocode_result_to_google_format(formatter: GoogleFormatter) -> None:
    raw = {
        "result": {
            "x": 21.0122,
            "y": 52.2297,
            "city": "Warszawa",
            "street": "Domaniewska",
            "house": "17A",
            "pcode": "02-672",
            "country": "Polska",
            "province": "mazowieckie",
            "district": "Mokotów",
            "quality": 9,
        }
    }

    output = formatter.format(raw, "Geocoder.geocode")

    assert output["status"] == "OK"
    assert len(output["results"]) == 1

    result = output["results"][0]
    assert result["formatted_address"] == "Domaniewska 17A, 02-672 Warszawa, Polska"
    assert result["place_id"] is None
    assert result["geometry"]["viewport"] is None
    assert result["types"] == ["street_address"]


def test_sets_lat_from_y_and_lng_from_x(formatter: GoogleFormatter) -> None:
    raw = {
        "result": {
            "x": 21.0122,
            "y": 52.2297,
            "city": "Warszawa",
            "quality": 9,
        }
    }

    output = formatter.format(raw, "Geocoder.geocode")

    location = output["results"][0]["geometry"]["location"]
    assert location["lat"] == 52.2297
    assert location["lng"] == 21.0122


def test_returns_zero_results_for_empty_result(formatter: GoogleFormatter) -> None:
    raw = {"result": []}
    output = formatter.format(raw, "Geocoder.geocode")

    assert output["status"] == "ZERO_RESULTS"
    assert output["results"] == []
    assert "_raw" in output


def test_returns_zero_results_for_none_result(formatter: GoogleFormatter) -> None:
    raw = {"result": None}
    output = formatter.format(raw, "Geocoder.geocode")

    assert output["status"] == "ZERO_RESULTS"
    assert output["results"] == []


def test_raw_attached_to_formatted_output(formatter: GoogleFormatter) -> None:
    raw = {
        "result": {
            "x": 21.0122,
            "y": 52.2297,
            "city": "Warszawa",
            "quality": 9,
        }
    }

    output = formatter.format(raw, "Geocoder.geocode")

    assert "_raw" in output
    assert output["_raw"] is raw


def test_raw_preserves_unknown_fields(formatter: GoogleFormatter) -> None:
    raw = {
        "result": {
            "x": 21.0122,
            "y": 52.2297,
            "city": "Warszawa",
            "quality": 9,
            "unknownFutureField": "preserved",
            "mapLink": "https://api.automapa.pl/map",
        }
    }

    output = formatter.format(raw, "Geocoder.geocode")

    assert output["_raw"]["result"]["unknownFutureField"] == "preserved"
    assert output["_raw"]["result"]["mapLink"] == "https://api.automapa.pl/map"


def test_non_geocoding_method_passes_through(formatter: GoogleFormatter) -> None:
    raw = {
        "result": {
            "distance": 123,
            "duration": 456,
        }
    }

    output = formatter.format(raw, "Routes.route")

    assert output["result"]["distance"] == raw["result"]["distance"]
    assert output["_raw"] is raw


def test_viewport_and_place_id_are_always_none(formatter: GoogleFormatter) -> None:
    raw = {
        "result": {
            "x": 18.0,
            "y": 50.0,
            "city": "Katowice",
            "quality": 5,
        }
    }

    output = formatter.format(raw, "Geocoder.geocode")
    geometry = output["results"][0]["geometry"]

    assert output["results"][0]["place_id"] is None
    assert geometry["viewport"] is None


def test_maps_address_components_correctly(formatter: GoogleFormatter) -> None:
    raw = {
        "result": {
            "x": 21.0,
            "y": 52.0,
            "city": "Warszawa",
            "street": "Marszałkowska",
            "house": "10",
            "pcode": "00-590",
            "province": "mazowieckie",
            "district": "Śródmieście",
            "country": "Polska",
            "quality": 9,
        }
    }

    output = formatter.format(raw, "Geocoder.geocode")
    components = output["results"][0]["address_components"]

    types_list = [c["types"] for c in components]

    assert ["route"] in types_list
    assert ["street_number"] in types_list
    assert ["locality", "political"] in types_list
    assert ["postal_code"] in types_list
    assert ["administrative_area_level_1", "political"] in types_list
    assert ["sublocality", "political"] in types_list
    assert ["country", "political"] in types_list


def test_revgeocode_method_is_mapped_as_geocoding(formatter: GoogleFormatter) -> None:
    raw = {
        "result": {
            "x": 19.94,
            "y": 50.06,
            "city": "Kraków",
            "quality": 7,
        }
    }

    output = formatter.format(raw, "Geocoder.revgeocode")

    assert output["status"] == "OK"
    assert len(output["results"]) == 1


# --- quality_to_type ---


@pytest.mark.parametrize(
    ("quality", "expected_type"),
    [
        (0, "country"),
        (1, "country"),
        (2, "country"),
        (3, "administrative_area_level_1"),
        (4, "locality"),
        (5, "locality"),
        (6, "route"),
        (7, "route"),
        (8, "street_address"),
        (9, "street_address"),
        (10, "street_address"),
    ],
)
def test_quality_to_type_mapping(
    formatter: GoogleFormatter, quality: int, expected_type: str
) -> None:
    raw = {"result": {"x": 19.0, "y": 50.0, "city": "X", "quality": quality}}
    output = formatter.format(raw, "Geocoder.geocode")
    assert output["results"][0]["types"] == [expected_type]


# --- Autocomplete ---


def test_maps_autocomplete_search_result_to_google_format(formatter: GoogleFormatter) -> None:
    raw = {
        "result": {
            "items": [
                {
                    "type": "place",
                    "subtype": "building",
                    "name": "Domaniewska 37, 02-672 Warszawa",
                    "place": "Warszawa",
                    "street": "Domaniewska",
                    "number": "37",
                    "postal_code": "02-672",
                    "province": "mazowieckie",
                    "district": "Warszawa",
                    "coords": {"x": 21.0071318, "y": 52.18284},
                }
            ]
        }
    }

    output = formatter.format(raw, "Autocomplete.search")

    assert output["status"] == "OK"
    assert len(output["results"]) == 1

    result = output["results"][0]
    assert result["formatted_address"] == "Domaniewska 37, 02-672 Warszawa"
    assert result["types"] == ["building"]
    assert result["place_id"] is None
    assert result["geometry"]["viewport"] is None


def test_autocomplete_search_sets_lat_from_coords_y_and_lng_from_coords_x(
    formatter: GoogleFormatter,
) -> None:
    raw = {
        "result": {
            "items": [
                {
                    "type": "place",
                    "subtype": "building",
                    "place": "Warszawa",
                    "street": "Domaniewska",
                    "number": "37",
                    "postal_code": "02-672",
                    "coords": {"x": 21.0071318, "y": 52.18284},
                }
            ]
        }
    }

    output = formatter.format(raw, "Autocomplete.search")
    location = output["results"][0]["geometry"]["location"]

    assert location["lat"] == 52.18284
    assert location["lng"] == 21.0071318


def test_maps_autocomplete_search_address_result_to_google_format(
    formatter: GoogleFormatter,
) -> None:
    raw = {
        "result": {
            "items": [
                {
                    "city": "Warszawa",
                    "street": "Domaniewska",
                    "zipcode": "02-672",
                    "count": 1,
                    "coords": {"x": 21.0071318, "y": 52.18284},
                }
            ]
        }
    }

    output = formatter.format(raw, "Autocomplete.searchAddress")

    assert output["status"] == "OK"
    assert len(output["results"]) == 1

    result = output["results"][0]
    location = result["geometry"]["location"]
    assert location["lat"] == 52.18284
    assert location["lng"] == 21.0071318
    assert result["formatted_address"] == "Domaniewska, 02-672 Warszawa"


def test_autocomplete_search_address_without_coords_has_null_location(
    formatter: GoogleFormatter,
) -> None:
    raw = {
        "result": {
            "items": [
                {
                    "city": "Warszawa",
                    "street": "Domaniewska",
                    "zipcode": "02-672",
                    "count": 3,
                    "coords": {"x": None, "y": None},
                }
            ]
        }
    }

    output = formatter.format(raw, "Autocomplete.searchAddress")
    location = output["results"][0]["geometry"]["location"]

    assert location["lat"] is None
    assert location["lng"] is None


def test_returns_zero_results_for_empty_autocomplete_items(formatter: GoogleFormatter) -> None:
    raw = {"result": {"items": []}}
    output = formatter.format(raw, "Autocomplete.search")

    assert output["status"] == "ZERO_RESULTS"
    assert output["results"] == []
    assert "_raw" in output


def test_raw_attached_for_autocomplete_search(formatter: GoogleFormatter) -> None:
    raw = {
        "result": {
            "items": [
                {
                    "type": "place",
                    "subtype": "building",
                    "place": "Warszawa",
                    "street": "Domaniewska",
                    "number": "37",
                    "postal_code": "02-672",
                    "coords": {"x": 21.0071318, "y": 52.18284},
                    "unknownFutureField": "should be preserved",
                }
            ]
        }
    }

    output = formatter.format(raw, "Autocomplete.search")

    assert "_raw" in output
    assert output["_raw"] is raw
    assert output["_raw"]["result"]["items"][0]["unknownFutureField"] == "should be preserved"


# --- geocodemulti ---


def test_geocodemulti_maps_list_of_results(formatter: GoogleFormatter) -> None:
    raw = {
        "result": [
            [{"x": 21.0, "y": 52.0, "city": "Warszawa", "quality": 9}],
            [{"x": 19.94, "y": 50.06, "city": "Kraków", "quality": 5}],
        ]
    }

    output = formatter.format(raw, "Geocoder.geocodemulti")

    assert output["status"] == "OK"
    assert len(output["results"]) == 2
    assert output["results"][0]["geometry"]["location"]["lat"] == 52.0
    assert output["results"][1]["geometry"]["location"]["lat"] == 50.06


def test_geocodemulti_error_item_preserved(formatter: GoogleFormatter) -> None:
    raw = {
        "result": [
            {"status": "ERROR", "message": "Not found"},
            [{"x": 21.0, "y": 52.0, "city": "Warszawa", "quality": 9}],
        ]
    }

    output = formatter.format(raw, "Geocoder.geocodemulti")

    assert output["status"] == "OK"
    assert output["results"][0] == {"status": "ERROR", "message": "Not found"}
    assert output["results"][1]["geometry"]["location"]["lat"] == 52.0
