from dataclasses import dataclass


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    headers: dict[str, str]
    body: str = ""

    def get_method(self) -> str:
        return self.method

    def get_url(self) -> str:
        return self.url

    def get_headers(self) -> dict[str, str]:
        return self.headers

    def get_body(self) -> str:
        return self.body
