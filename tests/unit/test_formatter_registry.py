import pytest

from automapa_map_services.formatter.google import GoogleFormatter
from automapa_map_services.formatter.native import NativeFormatter
from automapa_map_services.formatter.registry import FormatterRegistry


def test_register_and_get() -> None:
    registry = FormatterRegistry()
    native = NativeFormatter()
    registry.register("native", native)

    assert registry.get("native") is native


def test_has_returns_true_for_registered() -> None:
    registry = FormatterRegistry()
    registry.register("native", NativeFormatter())

    assert registry.has("native") is True


def test_has_returns_false_for_unregistered() -> None:
    registry = FormatterRegistry()

    assert registry.has("unknown") is False


def test_get_unknown_raises_key_error_or_value_error() -> None:
    registry = FormatterRegistry()
    registry.register("native", NativeFormatter())

    with pytest.raises((KeyError, ValueError)) as exc_info:
        registry.get("nonexistent")

    assert "nonexistent" in str(exc_info.value)


def test_get_error_message_includes_available_formatters() -> None:
    registry = FormatterRegistry()
    registry.register("native", NativeFormatter())
    registry.register("google", GoogleFormatter())

    with pytest.raises((KeyError, ValueError)) as exc_info:
        registry.get("unknown")

    message = str(exc_info.value)
    assert "unknown" in message


def test_register_overwrites_existing() -> None:
    registry = FormatterRegistry()
    first = NativeFormatter()
    second = NativeFormatter()

    registry.register("native", first)
    registry.register("native", second)

    assert registry.get("native") is second
