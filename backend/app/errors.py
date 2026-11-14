"""Application-level errors handled by app.core.exception_handlers."""
class AppError(Exception):
    def __init__(self, status_code: int, message: str, headers: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.headers = headers
