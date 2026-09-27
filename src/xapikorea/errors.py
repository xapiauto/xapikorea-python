from typing import Any


class XAPIKoreaError(Exception):
    pass


class APIError(XAPIKoreaError):
    def __init__(
        self,
        message: str,
        status_code: int,
        body: Any = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body
        self.retry_after = retry_after

