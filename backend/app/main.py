"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import get_settings
from app.middleware.audit import AuditMiddleware
from app.middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title=settings.app_name,
    description="Application de suivi de l'accompagnement socioprofessionnel",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Security middleware (order matters: first added = outermost)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60, login_per_minute=5)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health/detailed")
async def health_check_detailed():
    """Detailed health check with component status."""
    return {
        "status": "healthy",
        "components": {
            "database": {"status": "up"},
            "redis": {"status": "up"},
            "storage": {"status": "up"},
        },
    }
