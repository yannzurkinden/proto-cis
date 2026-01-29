"""Audit logging middleware for tracking sensitive operations."""

import time
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

import structlog

logger = structlog.get_logger(__name__)

# Paths that trigger audit logging
AUDIT_PATHS = {
    "POST": [
        "/api/v1/auth/login",
        "/api/v1/auth/change-password",
        "/api/v1/auth/reset-password",
        "/api/v1/beneficiaries",
        "/api/v1/users",
    ],
    "PUT": [
        "/api/v1/beneficiaries/",
        "/api/v1/users/",
    ],
    "DELETE": [
        "/api/v1/beneficiaries/",
        "/api/v1/users/",
        "/api/v1/documents/",
    ],
}

# Paths containing sensitive data to never log body for
SENSITIVE_PATHS = {
    "/api/v1/auth/login",
    "/api/v1/auth/change-password",
    "/api/v1/auth/reset-password",
    "/api/v1/auth/forgot-password",
}

# Medical data paths requiring special audit
MEDICAL_PATHS = {
    "/medical",
}


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware that logs sensitive operations for compliance."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()
        path = request.url.path
        method = request.method

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Check if this path should be audited
        should_audit = self._should_audit(method, path)
        is_medical = self._is_medical_access(path)

        if should_audit or is_medical:
            client_ip = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")

            log_data = {
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "ip_address": client_ip,
                "user_agent": user_agent[:200],
            }

            if is_medical:
                log_data["data_classification"] = "MEDICAL"
                logger.warning("medical_data_access", **log_data)
            elif response.status_code >= 400:
                logger.warning("audit_failed_operation", **log_data)
            else:
                logger.info("audit_operation", **log_data)

        return response

    def _should_audit(self, method: str, path: str) -> bool:
        """Check if this request should be audited."""
        paths = AUDIT_PATHS.get(method, [])
        for audit_path in paths:
            if path.startswith(audit_path) or path == audit_path:
                return True
        return False

    def _is_medical_access(self, path: str) -> bool:
        """Check if this request accesses medical data."""
        return any(med_path in path for med_path in MEDICAL_PATHS)

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP, considering proxy headers."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        return request.client.host if request.client else "unknown"
