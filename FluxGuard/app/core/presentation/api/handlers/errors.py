import logging
from fastapi import Request,status,FastAPI
from fastapi.responses import JSONResponse
from app.core.presentation.api.schemas.errors import ErrorResponse
from app.core.application.exceptions import ApplicationError,UnauthorizedError,ConflictError,ForbiddenError
from app.core.domain.exceptions import DomainError,InvalidValueObjectError,BusinessRuleViolationError,EntityNotFoundError
from app.core.presentation.exceptions import PresentationError
from app.core.presentation.exceptions import PresentationError
from fastapi.exceptions import RequestValidationError

EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    EntityNotFoundError: status.HTTP_404_NOT_FOUND,
    InvalidValueObjectError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    BusinessRuleViolationError: status.HTTP_400_BAD_REQUEST,
    UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
    ForbiddenError: status.HTTP_403_FORBIDDEN,
    ConflictError: status.HTTP_409_CONFLICT,
}

def _resolve_status_code(exc : Exception,default : int = status.HTTP_400_BAD_REQUEST):
    for exc_type,status_code in EXCEPTION_STATUS_MAP.items():
        if isinstance(exc,exc_type):
            return status_code
    return default

def build_error_response(message : str,status_code : int,error : str) -> JSONResponse:
    payload = ErrorResponse(
        message=message,
        error=error,
    )
    return JSONResponse(status_code=status_code,content=payload.model_dump())

async def domain_error_response(request : Request,exc : DomainError) -> JSONResponse:
    return build_error_response(
        message=exc.message,
        status_code=_resolve_status_code(exc),
        error=exc.code,
    )

async def application_error_response(request : Request,exc : ApplicationError) -> JSONResponse:
    return build_error_response(
        message=exc.message,
        status_code=_resolve_status_code(exc),
        error=exc.code,
    )

async def presentation_error_response(request : Request,exc : PresentationError) -> JSONResponse:
    return build_error_response(
        message=exc.message,
        status_code=_resolve_status_code(exc),
        error=exc.code,
    )

async def request_validation_error_response(request : Request,exc : RequestValidationError) -> JSONResponse:
    return build_error_response(
        message=str(exc.errors()),
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        error="VALIDATION_ERROR",
    )

async def exception_error_response(request : Request,exc : Exception) -> JSONResponse:
    logger.exception("Unhandled server error: %s", exc)
    return build_error_response(
        message="Internal server error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="INTERNAL_SERVER_ERROR"
    )


def register_exception(app : FastAPI) -> None:
    app.add_exception_handler(DomainError,domain_error_response)
    app.add_exception_handler(ApplicationError,application_error_response)
    app.add_exception_handler(RequestValidationError,request_validation_error_response)
    app.add_exception_handler(Exception,exception_error_response)
    app.add_exception_handler(PresentationError,presentation_error_response)

    