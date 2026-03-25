from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.config.settings import settings


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API key from X-API-Key header."""

    async def dispatch(self, request: Request, call_next):
        # Skip auth for health and metrics endpoints
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid API key"},
            )

        if api_key != settings.api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid API key"},
            )

        return await call_next(request)
