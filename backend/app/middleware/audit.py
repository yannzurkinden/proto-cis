"""Audit logging middleware for tracking sensitive operations."""

import time

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

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

            # Write audit log to database
            try:
                await self._write_audit_to_db(
                    method=method,
                    path=path,
                    status_code=response.status_code,
                    client_ip=client_ip,
                    user_agent=user_agent[:200],
                    is_medical=is_medical,
                )
            except Exception:
                logger.error("audit_db_write_failed", path=path, method=method)

        return response

    async def _write_audit_to_db(
        self,
        method: str,
        path: str,
        status_code: int,
        client_ip: str,
        user_agent: str,
        is_medical: bool = False,
    ) -> None:
        """Write audit log entry to database."""
        from app.database import AsyncSessionLocal
        from app.models.audit import AuditLog

        action = f"{method} {path}"
        resource_type = self._extract_resource_type(path)
        resource_id = self._extract_resource_id(path)

        async with AsyncSessionLocal() as session:
            try:
                log = AuditLog(
                    user_id=None,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    old_values=None,
                    new_values={"status_code": status_code, "medical": True} if is_medical else None,
                    ip_address=client_ip,
                    user_agent=user_agent,
                )
                session.add(log)
                await session.commit()
            except Exception:
                await session.rollback()

    def _extract_resource_type(self, path: str) -> str:
        """Extract the resource type from the URL path."""
        parts = path.replace("/api/v1/", "").split("/")
        return parts[0] if parts else "unknown"

    def _extract_resource_id(self, path: str) -> int | None:
        """Extract numeric resource ID from the URL path."""
        parts = path.split("/")
        for part in parts:
            try:
                return int(part)
            except ValueError:
                continue
        return None

    def _should_audit(self, method: str, path: str) -> bool:
        """Check if this request should be audited."""
        paths = AUDIT_PATHS.get(method, [])
        return any(path.startswith(audit_path) or path == audit_path for audit_path in paths)

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
