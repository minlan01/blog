"""Custom exception hierarchy for the blog application.

Business code should raise these instead of HTTPException directly.
The global exception handler in main.py maps them to HTTP responses.
"""
from fastapi import HTTPException


class BlogError(Exception):
    """Base exception for all blog business errors."""

    status_code: int = 500
    detail: str = "服务器内部错误"

    def __init__(self, detail: str | None = None, status_code: int | None = None):
        self.detail = detail or self.__class__.detail
        if status_code:
            self.status_code = status_code
        super().__init__(self.detail)

    def to_http_exception(self) -> HTTPException:
        return HTTPException(status_code=self.status_code, detail=self.detail)


class NotFoundError(BlogError):
    """Resource not found."""

    status_code = 404
    detail = "资源不存在"


class PermissionDeniedError(BlogError):
    """User lacks permission for this action."""

    status_code = 403
    detail = "权限不足"


class ValidationError(BlogError):
    """Business validation failed (not schema validation)."""

    status_code = 422
    detail = "数据验证失败"


class ConflictError(BlogError):
    """Resource already exists or conflicts with current state."""

    status_code = 409
    detail = "资源冲突"
