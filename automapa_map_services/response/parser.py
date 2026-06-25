import json
from typing import Any

from ..exceptions import ExceptionMapper, UnknownResponseException
from ..http.response import HttpResponse
from .api_response import ApiResponse


class ResponseParser:
    def __init__(self, exception_mapper: ExceptionMapper) -> None:
        self._mapper = exception_mapper

    def parse(
        self,
        response: HttpResponse,
        meta: dict[str, object] | None = None,
    ) -> ApiResponse:
        try:
            raw: Any = json.loads(response.body)
        except json.JSONDecodeError as e:
            raise UnknownResponseException(
                f"non-JSON response (HTTP {response.status_code})",
                response.status_code,
            ) from e

        if not isinstance(raw, dict):
            raise UnknownResponseException(
                f"non-JSON object response (HTTP {response.status_code})",
                response.status_code,
            )

        if not response.is_success:
            raise self._mapper.from_http_response(response.status_code, raw)

        return ApiResponse(
            raw=raw,
            status_code=response.status_code,
            meta=meta if meta is not None else {},
        )
