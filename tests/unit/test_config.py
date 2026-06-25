from automapa_map_services.config import Config


def test_default_values_are_set() -> None:
    config = Config(key="my-key", password="my-pass")

    assert config.base_url == "https://api.automapa.pl/"
    assert config.version == "v3"
    assert config.timeout_seconds == 30
    assert config.user_agent == "automapa-python-sdk/1.0"
    assert config.default_format == "native"


def test_getters_return_constructor_values() -> None:
    config = Config(
        key="test-key",
        password="test-pass",
        base_url="https://custom.example.com/",
        version="v2",
        timeout_seconds=10,
        user_agent="my-agent/2.0",
        default_format="google",
    )

    assert config.key == "test-key"
    assert config.password == "test-pass"
    assert config.base_url == "https://custom.example.com/"
    assert config.version == "v2"
    assert config.timeout_seconds == 10
    assert config.user_agent == "my-agent/2.0"
    assert config.default_format == "google"


def test_key_and_password_are_mandatory() -> None:
    config = Config("k", "p")

    assert config.key == "k"
    assert config.password == "p"


def test_pass_alias_returns_password() -> None:
    config = Config(key="k", password="secret")

    assert config.pass_ == "secret"
