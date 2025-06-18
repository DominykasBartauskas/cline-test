import logging
import sys
from typing import Any, Dict, Optional

import logfire
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from logfire import LogfireHandler
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Skip logging for health check endpoints
        if request.url.path == "/health":
            return response
        
        # Log request and response
        logfire.info(
            "HTTP Request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            client_host=request.client.host if request.client else None,
        )
        
        return response


class LoggingRoute(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except Exception as exc:
                logfire.exception(
                    "Unhandled exception",
                    method=request.method,
                    path=request.url.path,
                    exception=str(exc),
                )
                raise

        return custom_route_handler


def setup_logging() -> None:
    """Configure Logfire for structured logging."""
    
    # Set up logfire
    logfire.configure(
        token=settings.LOGFIRE_TOKEN,
        handlers=[
            LogfireHandler(
                level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
                stream=sys.stdout,
            )
        ],
        service_name="tmdb-api",
        service_version="0.1.0",
        environment=settings.ENVIRONMENT,
    )
    
    # Disable uvicorn access logs since we have our own middleware
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = False


def setup_app_logging(app: FastAPI) -> None:
    """Set up logging for the FastAPI application."""
    
    # Set up logging
    setup_logging()
    
    # Add logging middleware
    app.add_middleware(LoggingMiddleware)
    
    # Use custom route class for exception logging
    app.router.route_class = LoggingRoute
