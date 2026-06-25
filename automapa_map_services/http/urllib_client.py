import urllib.error
import urllib.request

from ..exceptions import NetworkException
from .request import HttpRequest
from .response import HttpResponse


class UrllibHttpClient:
    def __init__(self, timeout: int = 30) -> None:
        self._timeout = timeout

    def send(self, request: HttpRequest) -> HttpResponse:
        data = request.body.encode("utf-8") if request.body else None
        req = urllib.request.Request(
            request.url,
            data=data,
            headers=dict(request.headers),
            method=request.method,
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return HttpResponse(
                    status_code=resp.status,
                    body=resp.read().decode("utf-8"),
                    headers={k: v for k, v in resp.headers.items()},
                )
        except urllib.error.HTTPError as e:
            fp = e.fp
            body = fp.read().decode("utf-8") if fp is not None else ""
            headers = {k: v for k, v in e.headers.items()} if e.headers else {}
            return HttpResponse(status_code=e.code, body=body, headers=headers)
        except urllib.error.URLError as e:
            raise NetworkException(f"URL error: {e.reason}", 0) from e
