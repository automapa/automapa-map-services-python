from dataclasses import dataclass, field


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    body: str
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    def get_status_code(self) -> int:
        return self.status_code

    def get_body(self) -> str:
        return self.body

    def get_headers(self) -> dict[str, str]:
        return self.headers
