import pytest

from automapa_map_services.http.response import HttpResponse


def test_getters_return_constructor_values() -> None:
    response = HttpResponse(
        status_code=200,
        body='{"result":{"pong":"pong"}}',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.body == '{"result":{"pong":"pong"}}'
    assert response.headers == {"Content-Type": "application/json"}


def test_headers_default_to_empty_dict() -> None:
    response = HttpResponse(status_code=200, body="{}")
    assert response.headers == {}


@pytest.mark.parametrize("status_code", [200, 201, 204, 299])
def test_is_success_returns_true_for_2xx(status_code: int) -> None:
    assert HttpResponse(status_code=status_code, body="").is_success is True


@pytest.mark.parametrize("status_code", [400, 401, 403, 500, 503])
def test_is_success_returns_false_for_non_2xx(status_code: int) -> None:
    assert HttpResponse(status_code=status_code, body="").is_success is False
