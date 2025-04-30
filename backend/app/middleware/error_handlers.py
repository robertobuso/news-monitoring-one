"""
Global exception handlers for the application.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle database errors.
    
    Args:
        request: FastAPI request
        exc: SQLAlchemy exception
        
    Returns:
        JSONResponse: Error response
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred"},
    )


async def validation_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """
    Handle validation errors.
    
    Args:
        request: FastAPI request
        exc: ValueError exception
        
    Returns:
        JSONResponse: Error response
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle general exceptions.
    
    Args:
        request: FastAPI request
        exc: General exception
        
    Returns:
        JSONResponse: Error response
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"},
    )


def add_exception_handlers(app: FastAPI) -> None:
    """
    Add exception handlers to the FastAPI application.
    
    Args:
        app: FastAPI application
    """
    app.add_exception_handler(SQLAlchemyError, database_error_handler)
    app.add_exception_handler(ValueError, validation_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)