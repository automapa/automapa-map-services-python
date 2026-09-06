from typing import TYPE_CHECKING

from automapa_map_services.response.api_response import ApiResponse
from automapa_map_services.session.manager import hash_password

if TYPE_CHECKING:
    from automapa_map_services.client import ApiClient


class Session:
    """Raw access to the ``Session`` API service.

    Sessions are normally opened automatically by ``ApiClient``. Use ``ApiClient.open_session()``
    to open one manually; use ``login()`` when you want to call the endpoints yourself with a
    plain-text password.
    """

    def __init__(self, client: "ApiClient") -> None:
        self._client = client

    def getSalt(self, key: str) -> ApiResponse:
        """Fetch a one-time salt for ``key``; the result contains ``salt``."""
        return self._client.call("Session", "getSalt", {"key": key})

    def get_salt(self, key: str) -> ApiResponse:
        return self.getSalt(key)

    def generateSession(self, key: str, pass_: str) -> ApiResponse:
        """Open a session with an already hashed credential.

        ``pass_`` must be ``md5(md5(password) + salt)`` (see ``hash_password``), where ``salt``
        comes from a preceding ``getSalt`` call. Passing the plain-text password results in an
        authentication error from the API. The session returned here is not stored in the
        client's ``SessionManager``.
        """
        return self._client.call("Session", "generateSession", {"key": key, "pass": pass_})

    def generate_session(self, key: str, pass_: str) -> ApiResponse:
        return self.generateSession(key, pass_)

    def login(self, key: str, password: str) -> ApiResponse:
        """Fetch a salt, hash the plain-text ``password`` and call ``generateSession``."""
        salt = str(self.getSalt(key).data()["salt"])
        return self.generateSession(key, hash_password(password, salt))
