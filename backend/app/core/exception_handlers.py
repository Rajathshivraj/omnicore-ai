from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.errors import AppError


def error_response(
    *,
    request: Request,
    status_code: int,
    error_code: str,
    message: str,
    details: object | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error_code": error_code,
            "message": message,
            "details": details or {},
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return error_response(
        request=request,
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(
        request=request,
        status_code=422,
        error_code="VALIDATION_ERROR",
        message="Request validation failed.",
        details=exc.errors(),
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    return error_response(
        request=request,
        status_code=409,
        error_code="DATABASE_CONSTRAINT_VIOLATION",
        message="The requested operation conflicts with database constraints.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
