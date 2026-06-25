from typing import TextIO

from .client import HttpClientProtocol
from .request import HttpRequest
from .response import HttpResponse


class DebugHttpClient:
    def __init__(self, inner: HttpClientProtocol, output: TextIO) -> None:
        self._inner = inner
        self._output = output

    def send(self, request: HttpRequest) -> HttpResponse:
        self._write_request(request)
        response = self._inner.send(request)
        self._write_response(response)
        return response

    def _write_request(self, request: HttpRequest) -> None:
        self._output.write("=== REQUEST ===\n")
        self._output.write(f"{request.method} {request.url}\n")
        for key, value in request.headers.items():
            self._output.write(f"{key}: {value}\n")
        self._output.write("\n")
        if request.body:
            self._output.write(request.body + "\n")

    def _write_response(self, response: HttpResponse) -> None:
        self._output.write(f"=== RESPONSE ({response.status_code}) ===\n")
        for key, value in response.headers.items():
            self._output.write(f"{key}: {value}\n")
        self._output.write("\n")
        if response.body:
            self._output.write(response.body + "\n")
