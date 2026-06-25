import pytest

from automapa_map_services.exceptions import (
    AuthenticationException,
    AutomapaException,
    ExceptionMapper,
    NotFoundException,
    RateLimitException,
    ServerException,
    SessionException,
    UnknownResponseException,
    ValidationException,
)


@pytest.fixture
def mapper() -> ExceptionMapper:
    return ExceptionMapper()


@pytest.mark.parametrize(
    "status_code,expected_class",
    [
        (400, ValidationException),
        (401, AuthenticationException),
        (403, SessionException),
        (404, NotFoundException),
        (429, RateLimitException),
        (500, ServerException),
        (503, ServerException),
        (418, UnknownResponseException),
        (301, UnknownResponseException),
    ],
)
def test_http_code_maps_to_correct_exception(
    mapper: ExceptionMapper,
    status_code: int,
    expected_class: type,
) -> None:
    exception = mapper.from_http_response(status_code, {})
    assert isinstance(exception, expected_class)


def test_all_mapped_exceptions_are_automapa_exception(mapper: ExceptionMapper) -> None:
    for code in [400, 401, 403, 404, 429, 500, 418]:
        assert isinstance(mapper.from_http_response(code, {}), AutomapaException)


def test_message_extracted_from_body_message_field(mapper: ExceptionMapper) -> None:
    exception = mapper.from_http_response(401, {"message": "Invalid API key"})
    assert str(exception) == "Invalid API key"


def test_message_extracted_from_body_error_field(mapper: ExceptionMapper) -> None:
    exception = mapper.from_http_response(500, {"error": "Something went wrong"})
    assert str(exception) == "Something went wrong"


def test_message_falls_back_to_http_status_when_body_empty(mapper: ExceptionMapper) -> None:
    exception = mapper.from_http_response(429, {})
    assert str(exception) == "HTTP 429"


def test_exception_code_matches_http_status_code(mapper: ExceptionMapper) -> None:
    exception = mapper.from_http_response(403, {})
    assert exception.code == 403


def test_message_includes_api_code_when_present_in_body(mapper: ExceptionMapper) -> None:
    exception = mapper.from_http_response(
        500, {"message": "Something went wrong", "code": "SERVER_ERROR"}
    )
    assert str(exception) == "Something went wrong [code: SERVER_ERROR]"


def test_message_does_not_include_api_code_suffix_when_code_absent(mapper: ExceptionMapper) -> None:
    exception = mapper.from_http_response(500, {"message": "Something went wrong"})
    assert str(exception) == "Something went wrong"


def test_any_http_5xx_maps_to_server_exception(mapper: ExceptionMapper) -> None:
    exception = mapper.from_http_response(501, {"message": "Not implemented"})
    assert isinstance(exception, ServerException)
