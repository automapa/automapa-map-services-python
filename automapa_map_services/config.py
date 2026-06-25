from dataclasses import dataclass


@dataclass
class Config:
    key: str
    password: str
    base_url: str = "https://api.automapa.pl/"
    version: str = "v3"
    timeout_seconds: int = 30
    user_agent: str = "automapa-python-sdk/1.0"
    default_format: str = "native"

    @property
    def pass_(self) -> str:
        return self.password
