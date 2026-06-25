"""Unit tests for fixture loading helpers and integration test skip behavior."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from tests.support.fixtures import fixture_body, load_fixture, load_fixture_raw

_FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestLoadFixture:
    def test_loads_session_salt(self) -> None:
        data = load_fixture("session_salt")
        assert data["result"]["salt"] == "xNnlXNS3Bq"

    def test_loads_session_generate(self) -> None:
        data = load_fixture("session_generate")
        assert data["result"]["sessionId"] == "qPPdEpdtpb"

    def test_accepts_json_extension(self) -> None:
        a = load_fixture("geocode_success")
        b = load_fixture("geocode_success.json")
        assert a == b

    def test_loads_geocode_success(self) -> None:
        data = load_fixture("geocode_success")
        result = data["result"]
        assert result["city"] == "Warszawa"
        assert result["x"] == pytest.approx(21.0122)
        assert result["unknownFutureField"] == "should be preserved"

    def test_loads_geocode_empty_results(self) -> None:
        data = load_fixture_raw("geocode_empty_results")
        assert data["result"] == []

    def test_loads_error_fixture(self) -> None:
        data = load_fixture("errors/auth_error")
        assert data["message"] == "Invalid API key or credentials"
        assert data["code"] == "AUTH_FAILED"

    def test_loads_all_error_fixtures(self) -> None:
        for name in ("auth_error", "session_error", "rate_limit", "server_error"):
            data = load_fixture(f"errors/{name}")
            assert "message" in data

    def test_fixture_body_returns_valid_json_string(self) -> None:
        raw = fixture_body("session_salt")
        parsed = json.loads(raw)
        assert parsed["result"]["salt"] == "xNnlXNS3Bq"

    def test_missing_fixture_raises_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_fixture("nonexistent_fixture")

    def test_all_expected_fixtures_exist(self) -> None:
        expected = [
            "session_salt.json",
            "session_generate.json",
            "geocode_success.json",
            "geocode_empty_results.json",
            "revgeocode_success.json",
            "geocodemulti_success.json",
            "revgeocodemulti_success.json",
            "autocomplete_search_success.json",
            "autocomplete_search_empty.json",
            "autocomplete_search_address_success.json",
            "road_get_segment_info_success.json",
            "road_speed_check_success.json",
            "road_speed_check_multi_success.json",
            "routes_route_success.json",
            "routes_matrix_success.json",
            "routes_optimize_success.json",
            "routes_optimize_queue_success.json",
            "routes_optimize_queue_result_success.json",
            "google_geocoding_api_reference.json",
            "errors/auth_error.json",
            "errors/session_error.json",
            "errors/rate_limit.json",
            "errors/server_error.json",
        ]
        for name in expected:
            assert (_FIXTURES_DIR / name).exists(), f"Missing fixture: {name}"


class TestIntegrationSkipBehavior:
    def test_requires_live_api_skips_without_key(self) -> None:
        """requires_live_api() returns a skip mark when credentials are absent."""
        with (
            patch("tests.integration.conftest._load_env_file"),
            patch.dict(os.environ, {}, clear=True),
        ):
            from tests.integration.conftest import requires_live_api

            mark = requires_live_api()
            assert mark.name == "skip"

    def test_requires_live_api_skips_without_password(self) -> None:
        with (
            patch("tests.integration.conftest._load_env_file"),
            patch.dict(os.environ, {"AUTOMAPA_API_KEY": "test_key"}, clear=True),
        ):
            from tests.integration.conftest import requires_live_api

            mark = requires_live_api()
            assert mark.name == "skip"
            assert "AUTOMAPA_API_PASSWORD" in str(mark.kwargs.get("reason", ""))

    def test_requires_live_api_skips_for_excluded_suite(self) -> None:
        env = {
            "AUTOMAPA_API_KEY": "k",
            "AUTOMAPA_API_PASSWORD": "p",
            "AUTOMAPA_API_REQUIRED_ACCESS": "geocoder",
        }
        with patch.dict(os.environ, env, clear=True):
            from tests.integration.conftest import requires_live_api

            mark = requires_live_api("routes")
            assert mark.name == "skip"
            assert "routes" in str(mark.kwargs.get("reason", ""))

    def test_requires_live_api_no_skip_when_suite_in_access_list(self) -> None:
        env = {
            "AUTOMAPA_API_KEY": "k",
            "AUTOMAPA_API_PASSWORD": "p",
            "AUTOMAPA_API_REQUIRED_ACCESS": "geocoder,routes",
        }
        with patch.dict(os.environ, env, clear=True):
            from tests.integration.conftest import requires_live_api

            mark = requires_live_api("geocoder")
            assert mark.name != "skip"

    def test_requires_live_api_no_skip_when_no_access_list_restriction(self) -> None:
        env = {
            "AUTOMAPA_API_KEY": "k",
            "AUTOMAPA_API_PASSWORD": "p",
            "AUTOMAPA_API_REQUIRED_ACCESS": "",
        }
        with patch.dict(os.environ, env, clear=True):
            from tests.integration.conftest import requires_live_api

            mark = requires_live_api("any_suite")
            assert mark.name != "skip"
