from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from .config import Config
from .exceptions import ExceptionMapper
from .formatter.google import GoogleFormatter
from .formatter.native import NativeFormatter
from .formatter.registry import FormatterRegistry
from .http.builder import RequestBuilder
from .http.client import HttpClientProtocol
from .http.request import HttpRequest
from .http.urllib_client import UrllibHttpClient
from .response.api_response import ApiResponse
from .response.parser import ResponseParser
from .session.manager import SessionManager
from .session.storage import InMemorySessionStorage

if TYPE_CHECKING:
    from .endpoints.autocomplete import Autocomplete
    from .endpoints.geocoder import Geocoder
    from .endpoints.ping_pong import PingPong
    from .endpoints.road import Road
    from .endpoints.road_permit import RoadPermit
    from .endpoints.routes import Routes
    from .endpoints.session import Session
    from .endpoints.speed import Speed


class ApiClient:
    def __init__(
        self,
        config: Config,
        http_client: HttpClientProtocol | None = None,
        session_manager: SessionManager | None = None,
        formatter_registry: FormatterRegistry | None = None,
    ) -> None:
        self._config = config
        self._http_client = http_client or UrllibHttpClient(config.timeout_seconds)
        self._request_builder = RequestBuilder(config.base_url, config.version)
        self._exception_mapper = ExceptionMapper()
        self._response_parser = ResponseParser(self._exception_mapper)
        self._session_manager = session_manager or SessionManager(
            config,
            self._http_client,
            InMemorySessionStorage(),
        )
        self._formatter_registry = formatter_registry or self._build_default_registry()

    @property
    def config(self) -> Config:
        return self._config

    def get_config(self) -> Config:
        return self._config

    def call(
        self,
        service: str,
        method: str,
        params: dict[str, Any] | None = None,
    ) -> ApiResponse:
        request_params = dict(params or {})
        output_format = str(request_params.pop("format", self._config.default_format))
        session_id: str | None = None

        if self._session_manager.requires_session(service, method):
            session_id = self._session_manager.ensure_session()

        request = self._request_builder.build(service, method, request_params, session_id)
        http_response = self._http_client.send(request)

        if http_response.status_code == 403 and session_id is not None:
            self._session_manager.clear_session()
            session_id = self._session_manager.ensure_session()
            request = self._request_builder.build(service, method, request_params, session_id)
            http_response = self._http_client.send(request)

        api_response = self._response_parser.parse(
            http_response,
            {"service": service, "method": method},
        )

        if output_format != "native" and self._formatter_registry.has(output_format):
            formatted_data = self._formatter_registry.get(output_format).format(
                api_response.raw(),
                f"{service}.{method}",
            )
            return ApiResponse(
                raw=api_response.raw(),
                status_code=api_response.status(),
                formatted_data=formatted_data,
                meta=api_response.meta(),
            )

        return api_response

    def request(
        self,
        http_method: str,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> ApiResponse:
        url = self._config.base_url.rstrip("/") + "/" + path.lstrip("/")
        body = "[]" if not params else json.dumps(params, separators=(",", ":"))
        http_request = HttpRequest(
            method=http_method,
            url=url,
            headers={"Content-Type": "application/json"},
            body=body,
        )
        http_response = self._http_client.send(http_request)
        return self._response_parser.parse(http_response, {"path": path})

    def geocoder(self) -> Geocoder:
        from .endpoints.geocoder import Geocoder

        return Geocoder(self)

    def session(self) -> Session:
        from .endpoints.session import Session

        return Session(self)

    def autocomplete(self) -> Autocomplete:
        from .endpoints.autocomplete import Autocomplete

        return Autocomplete(self)

    def pingPong(self) -> PingPong:
        from .endpoints.ping_pong import PingPong

        return PingPong(self)

    def ping_pong(self) -> PingPong:
        return self.pingPong()

    def road(self) -> Road:
        from .endpoints.road import Road

        return Road(self)

    def roadPermit(self, environment: str = "prod") -> RoadPermit:
        from .endpoints.road_permit import RoadPermit

        return RoadPermit(self, environment)

    def road_permit(self, environment: str = "prod") -> RoadPermit:
        return self.roadPermit(environment)

    def routes(self) -> Routes:
        from .endpoints.routes import Routes

        return Routes(self)

    def speed(self) -> Speed:
        from .endpoints.speed import Speed

        return Speed(self)

    def _build_default_registry(self) -> FormatterRegistry:
        registry = FormatterRegistry()
        registry.register("native", NativeFormatter())
        registry.register("google", GoogleFormatter())
        return registry
