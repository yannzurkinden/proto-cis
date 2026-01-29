"""Security middleware for headers, CSRF, and input sanitization."""

import re
import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        # Cache control for API responses
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter."""

    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        login_per_minute: int = 5,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.login_per_minute = login_per_minute
        self._requests: Dict[str, list] = defaultdict(list)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        client_ip = self._get_client_ip(request)
        path = request.url.path
        now = time.time()

        # Determine rate limit
        if path == "/api/v1/auth/login" and request.method == "POST":
            limit = self.login_per_minute
            key = f"login:{client_ip}"
        elif path.startswith("/api/"):
            limit = self.requests_per_minute
            key = f"api:{client_ip}"
        else:
            return await call_next(request)

        # Clean old entries (older than 60 seconds)
        self._requests[key] = [
            t for t in self._requests[key] if now - t < 60
        ]

        # Check limit
        if len(self._requests[key]) >= limit:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Trop de requêtes. Veuillez réessayer plus tard."},
                headers={"Retry-After": "60"},
            )

        # Record request
        self._requests[key].append(now)

        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


# XSS pattern for input sanitization
XSS_PATTERNS = [
    re.compile(r"<script[^>]*>", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),
]


def sanitize_string(value: str) -> str:
    """Sanitize a string to prevent XSS."""
    if not value:
        return value
    # Remove potential XSS vectors
    sanitized = value
    sanitized = sanitized.replace("<script", "&lt;script")
    sanitized = sanitized.replace("</script", "&lt;/script")
    return sanitized


def check_xss(value: str) -> bool:
    """Check if a string contains potential XSS patterns."""
    for pattern in XSS_PATTERNS:
        if pattern.search(value):
            return True
    return False
