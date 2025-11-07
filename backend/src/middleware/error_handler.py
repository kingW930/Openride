"""
Error handling middleware and exception handlers
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Union


class OpenSeatException(Exception):
    """Base exception for OpenSeat application"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(OpenSeatException):
    """Raised when a resource is not found"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class UnauthorizedException(OpenSeatException):
    """Raised when user is not authorized"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class ForbiddenException(OpenSeatException):
    """Raised when user doesn't have permission"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)


class BadRequestException(OpenSeatException):
    """Raised for bad requests"""
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status_code=400)


class ConflictException(OpenSeatException):
    """Raised when there's a conflict (e.g., duplicate resource)"""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409)


async def openseat_exception_handler(request: Request, exc: OpenSeatException):
    """Handle OpenSeat custom exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "status_code": exc.status_code
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"][1:]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Validation error",
            "errors": errors,
            "status_code": 422
        }
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Database error occurred",
            "status_code": 500
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500
        }
    )
