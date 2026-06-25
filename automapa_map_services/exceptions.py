class AutomapaException(Exception):
    def __init__(self, message: str, code: int) -> None:
        super().__init__(message)
        self.code = code


class ValidationException(AutomapaException):
    pass


class AuthenticationException(AutomapaException):
    pass


class SessionException(AutomapaException):
    pass


class NotFoundException(AutomapaException):
    pass


class RateLimitException(AutomapaException):
    pass


class ServerException(AutomapaException):
    pass


class UnknownResponseException(AutomapaException):
    pass


class NetworkException(AutomapaException):
    pass


class ExceptionMapper:
    _STATUS_MAP: dict[int, type[AutomapaException]] = {
        400: ValidationException,
        401: AuthenticationException,
        403: SessionException,
        404: NotFoundException,
        429: RateLimitException,
    }

    def from_http_response(self, status_code: int, body: dict[str, object]) -> AutomapaException:
        exception_class = self._exception_class(status_code)
        message = self._build_message(body, status_code)
        return exception_class(message, status_code)

    def _exception_class(self, status_code: int) -> type[AutomapaException]:
        if status_code >= 500:
            return ServerException
        return self._STATUS_MAP.get(status_code, UnknownResponseException)

    def _build_message(self, body: dict[str, object], status_code: int) -> str:
        api_message = self._message_from_body(body)
        if api_message is None:
            return f"HTTP {status_code}"

        api_code = body.get("code")
        if api_code is not None and str(api_code) != "":
            return f"{api_message} [code: {api_code}]"
        return api_message

    def _message_from_body(self, body: dict[str, object]) -> str | None:
        for key in ("message", "error"):
            value = body.get(key)
            if value is not None and str(value) != "":
                return str(value)
        return None
