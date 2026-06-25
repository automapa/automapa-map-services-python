from automapa_map_services.exceptions import AutomapaException, NetworkException


def test_extends_automapa_exception() -> None:
    assert isinstance(NetworkException("timeout", 28), AutomapaException)


def test_message_and_code_are_propagated() -> None:
    e = NetworkException("Connection refused", 7)
    assert str(e) == "Connection refused"
    assert e.code == 7


def test_url_error_message_format() -> None:
    message = "URL error (28): Operation timed out"
    e = NetworkException(message, 28)
    assert "28" in str(e)
    assert "Operation timed out" in str(e)
    assert e.code == 28


def test_empty_url_message() -> None:
    e = NetworkException("Cannot send request: URL is empty.", 0)
    assert "URL is empty" in str(e)
    assert e.code == 0
