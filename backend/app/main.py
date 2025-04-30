"""
Main application module for the NewsMonitor API.
This module initializes the FastAPI application and includes all routes.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import auth
from app.core.config import settings
from app.middleware.error_handlers import add_exception_handlers
from app.middleware.rate_limiter import RateLimitMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add rate limiting middleware
    application.add_middleware(
        BaseHTTPMiddleware,
        dispatch=RateLimitMiddleware(
            rate_limit=settings.RATE_LIMIT,
            time_window=settings.RATE_LIMIT_WINDOW,
        ),
    )

    # Add exception handlers
    add_exception_handlers(application)

    # Include routers
    application.include_router(auth.router, prefix="/api/v1")

    @application.get("/api/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok"}

    return application


app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )