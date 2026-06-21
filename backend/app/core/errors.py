from typing import Any


class AppError(Exception):
    status_code = 500
    error_code = "INTERNAL_SERVER_ERROR"
    message = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.message
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AppError):
    status_code = 401
    error_code = "AUTHENTICATION_FAILED"
    message = "Authentication failed."


class AuthorizationError(AppError):
    status_code = 403
    error_code = "PERMISSION_DENIED"
    message = "You do not have permission to perform this action."


class NotFoundError(AppError):
    status_code = 404
    error_code = "RESOURCE_NOT_FOUND"
    message = "The requested resource was not found."


class ConflictError(AppError):
    status_code = 409
    error_code = "RESOURCE_CONFLICT"
    message = "The requested operation conflicts with existing state."


class BusinessRuleError(AppError):
    status_code = 400
    error_code = "BUSINESS_RULE_VIOLATION"
    message = "The requested operation violates a business rule."
