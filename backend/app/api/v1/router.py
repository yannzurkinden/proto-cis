"""Main API router combining all endpoint routers."""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    units,
    beneficiaries,
    pais,
    objectives,
    journal,
    documents,
    dashboard,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(units.router, prefix="/units", tags=["Units"])
api_router.include_router(beneficiaries.router, prefix="/beneficiaries", tags=["Beneficiaries"])
api_router.include_router(pais.router, prefix="/pais", tags=["PAIs"])
api_router.include_router(objectives.router, prefix="/objectives", tags=["Objectives"])
api_router.include_router(journal.router, prefix="/journal", tags=["Journal"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
