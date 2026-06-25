from typing import Protocol

from .request import HttpRequest
from .response import HttpResponse


class HttpClientProtocol(Protocol):
    def send(self, request: HttpRequest) -> HttpResponse: ...
