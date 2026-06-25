from typing import Any

import pytest

from automapa_map_services.endpoints.autocomplete import Autocomplete
from automapa_map_services.endpoints.geocoder import Geocoder
from automapa_map_services.endpoints.ping_pong import PingPong
from automapa_map_services.endpoints.road import Road
from automapa_map_services.endpoints.road_permit import RoadPermit
from automapa_map_services.endpoints.routes import Routes
from automapa_map_services.endpoints.session import Session
from automapa_map_services.endpoints.speed import Speed
from automapa_map_services.response.api_response import ApiResponse


class RecordingClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def call(self, service: str, method: str, params: dict[str, Any]) -> ApiResponse:
        self.calls.append((service, method, params))
        return ApiResponse(raw={"result": "ok"}, status_code=200)


def test_ping_pong_ping_dispatches_message() -> None:
    client = RecordingClient()
    PingPong(client).ping("hello")
    assert client.calls == [("PingPong", "ping", {"msg": "hello"})]


def test_geocoder_geocode_dispatches_with_correct_params() -> None:
    client = RecordingClient()
    Geocoder(client).geocode(city="Warszawa")
    assert client.calls == [("Geocoder", "geocode", {"address": {"city": "Warszawa"}})]


def test_geocoder_geocode_filters_none_and_empty_string() -> None:
    client = RecordingClient()
    Geocoder(client).geocode(city="Warszawa", street="Domaniewska", house="", country=None)
    assert client.calls == [
        ("Geocoder", "geocode", {"address": {"city": "Warszawa", "street": "Domaniewska"}})
    ]


def test_geocoder_geocode_with_max_results() -> None:
    client = RecordingClient()
    Geocoder(client).geocode(city="Warszawa", max_results=3)
    assert client.calls == [
        ("Geocoder", "geocode", {"address": {"city": "Warszawa"}, "maxResults": 3})
    ]


def test_geocoder_geocodemulti_dispatches_with_correct_params() -> None:
    client = RecordingClient()
    Geocoder(client).geocodemulti(addresses=[{"city": "Warszawa"}])
    assert client.calls == [("Geocoder", "geocodemulti", {"addresses": [{"city": "Warszawa"}]})]


def test_geocoder_revgeocode_dispatches_with_correct_params() -> None:
    client = RecordingClient()
    Geocoder(client).revgeocode(point=[21.0, 52.0])
    assert client.calls == [("Geocoder", "revgeocode", {"point": [21.0, 52.0]})]


def test_geocoder_revgeocode_with_optional_params() -> None:
    client = RecordingClient()
    Geocoder(client).revgeocode(point=[21.0, 52.0], snap_to_bld=True, snap_to_bld_radius=50)
    assert client.calls == [
        (
            "Geocoder",
            "revgeocode",
            {
                "point": [21.0, 52.0],
                "params": {"snapToBld": True, "snapToBldRadius": 50},
            },
        )
    ]


def test_geocoder_revgeocodemulti_dispatches_with_correct_params() -> None:
    client = RecordingClient()
    Geocoder(client).revgeocodemulti(points=[[21.0, 52.0]])
    assert client.calls == [
        ("Geocoder", "revgeocodemulti", {"points": [[21.0, 52.0]], "params": {}})
    ]


def test_session_methods_dispatch() -> None:
    client = RecordingClient()
    session = Session(client)

    session.getSalt("key")
    session.generateSession("key", "pass-hash")

    assert client.calls == [
        ("Session", "getSalt", {"key": "key"}),
        ("Session", "generateSession", {"key": "key", "pass": "pass-hash"}),
    ]


def test_autocomplete_search_dispatches_with_correct_params() -> None:
    client = RecordingClient()
    Autocomplete(client).search(query="Warszawa")
    assert client.calls == [("Autocomplete", "search", {"query": "Warszawa"})]


def test_autocomplete_search_with_types() -> None:
    client = RecordingClient()
    Autocomplete(client).search(query="Warszawa", types=["place"])
    assert client.calls == [("Autocomplete", "search", {"query": "Warszawa", "types": ["place"]})]


def test_autocomplete_search_address_dispatches_with_correct_params() -> None:
    client = RecordingClient()
    Autocomplete(client).searchAddress(query={"city": "Warszawa"}, source="street")
    assert client.calls == [
        ("Autocomplete", "searchAddress", {"query": {"city": "Warszawa"}, "source": "street"}),
    ]


def test_autocomplete_search_address_snake_case_alias() -> None:
    client = RecordingClient()
    Autocomplete(client).search_address(query={"city": "Warszawa"}, source="street")
    assert client.calls == [
        ("Autocomplete", "searchAddress", {"query": {"city": "Warszawa"}, "source": "street"}),
    ]


@pytest.mark.parametrize(
    ("method_name", "api_method"),
    [
        ("getSegmentInfo", "getSegmentInfo"),
        ("get_segment_info", "getSegmentInfo"),
        ("speedCheck", "speedCheck"),
        ("speed_check", "speedCheck"),
        ("speedCheckMulti", "speedCheckMulti"),
        ("speed_check_multi", "speedCheckMulti"),
    ],
)
def test_road_methods_dispatch(method_name: str, api_method: str) -> None:
    client = RecordingClient()
    getattr(Road(client), method_name)({"x": 21.0, "y": 52.0})
    assert client.calls == [("Road", api_method, {"x": 21.0, "y": 52.0})]


def test_routes_matrix_dispatches_with_correct_params() -> None:
    client = RecordingClient()
    Routes(client).matrix(points=[[1, 2]], type=1)
    assert client.calls == [
        ("Routes", "matrix", {"points": [[1, 2]], "type": 1, "precise": False, "simple": False}),
    ]


def test_routes_optimize_dispatches_with_correct_params() -> None:
    client = RecordingClient()
    Routes(client).optimize(points=[[1, 2]], type=1)
    assert client.calls == [
        ("Routes", "optimize", {"points": [[1, 2]], "type": 1, "fixedEnd": True}),
    ]


def test_routes_optimize_with_optional_params() -> None:
    client = RecordingClient()
    Routes(client).optimize(
        points=[[1, 2]],
        type=1,
        fixed_end=False,
        route=["r"],
        object={"type": "car"},
    )
    assert client.calls == [
        (
            "Routes",
            "optimize",
            {
                "points": [[1, 2]],
                "type": 1,
                "fixedEnd": False,
                "route": ["r"],
                "object": {"type": "car"},
            },
        )
    ]


def test_routes_optimize_queue_dispatches_with_correct_params() -> None:
    client = RecordingClient()
    Routes(client).optimizeQueue(points=[[1, 2]], optimize_by="time")
    assert client.calls == [
        ("Routes", "optimizeQueue", {"points": [[1, 2]], "optimizeBy": "time", "fixedEnd": True}),
    ]


def test_routes_optimize_queue_snake_case_alias() -> None:
    client = RecordingClient()
    Routes(client).optimize_queue(points=[[1, 2]], optimize_by="time")
    assert client.calls == [
        ("Routes", "optimizeQueue", {"points": [[1, 2]], "optimizeBy": "time", "fixedEnd": True}),
    ]


def test_routes_optimize_queue_result_dispatches_with_correct_params() -> None:
    client = RecordingClient()
    Routes(client).optimizeQueueResult(request_id="req-123")
    assert client.calls == [("Routes", "optimizeQueueResult", {"requestId": "req-123"})]


def test_routes_optimize_queue_result_snake_case_alias() -> None:
    client = RecordingClient()
    Routes(client).optimize_queue_result(request_id="req-123")
    assert client.calls == [("Routes", "optimizeQueueResult", {"requestId": "req-123"})]


def test_routes_route_dispatches_with_correct_params() -> None:
    client = RecordingClient()
    Routes(client).route(points=[[1, 2]], route={"type": "short"}, object={"type": "car"})
    assert client.calls == [
        (
            "Routes",
            "route",
            {
                "points": [[1, 2]],
                "route": {"type": "short"},
                "object": {"type": "car"},
            },
        )
    ]


def test_speed_report_dispatches_with_correct_params() -> None:
    client = RecordingClient()
    Speed(client).speedReport(obj_id="v1", obj_name="Vehicle", obj_group="Group", points=[{"x": 1}])
    assert client.calls == [
        (
            "Speed",
            "speedReport",
            {
                "objID": "v1",
                "objName": "Vehicle",
                "objGroup": "Group",
                "points": [{"x": 1}],
            },
        )
    ]


def test_speed_report_snake_case_alias() -> None:
    client = RecordingClient()
    Speed(client).speed_report(
        obj_id="v1",
        obj_name="Vehicle",
        obj_group="Group",
        points=[{"x": 1}],
    )
    assert client.calls == [
        (
            "Speed",
            "speedReport",
            {
                "objID": "v1",
                "objName": "Vehicle",
                "objGroup": "Group",
                "points": [{"x": 1}],
            },
        )
    ]


def test_speed_report_result_dispatches_with_correct_params() -> None:
    client = RecordingClient()
    Speed(client).speedReportResult(request_id="abc")
    assert client.calls == [("Speed", "speedReportResult", {"requestID": "abc", "limit": 1})]


def test_speed_report_result_snake_case_alias() -> None:
    client = RecordingClient()
    Speed(client).speed_report_result(request_id="abc")
    assert client.calls == [("Speed", "speedReportResult", {"requestID": "abc", "limit": 1})]


def test_road_permit_list_add_overwrite_remove_dispatch_and_preserve_enviroment_typo() -> None:
    client = RecordingClient()
    permit = RoadPermit(client, "test")

    permit.list()
    permit.add(permissions=["x"], poly=[[1, 2]], description="new")
    permit.overwrite("permit-id", ["x"], [[1, 2]])
    permit.remove("permit-id")

    assert client.calls == [
        ("RoadPermit", "list", {"enviroment": "test"}),
        (
            "RoadPermit",
            "add",
            {
                "permissions": ["x"],
                "poly": [[1, 2]],
                "description": "new",
                "enviroment": "test",
            },
        ),
        (
            "RoadPermit",
            "overwrite",
            {
                "id": "permit-id",
                "permissions": ["x"],
                "poly": [[1, 2]],
                "enviroment": "test",
            },
        ),
        ("RoadPermit", "remove", {"id": "permit-id", "enviroment": "test"}),
    ]


def test_road_permit_add_removes_null_id_and_uses_add_endpoint() -> None:
    client = RecordingClient()

    RoadPermit(client).add(permissions=["x"], poly=[[1, 2]], extra={"id": None})

    assert client.calls == [
        ("RoadPermit", "add", {"permissions": ["x"], "poly": [[1, 2]], "enviroment": "prod"})
    ]


@pytest.mark.parametrize(
    ("permissions", "poly"),
    [
        ([], [[1, 2]]),
        (["x"], []),
    ],
)
def test_road_permit_add_validates_required_fields(permissions: list[Any], poly: list[Any]) -> None:
    with pytest.raises(ValueError):
        RoadPermit(RecordingClient()).add(permissions=permissions, poly=poly)
