"""Main API router combining all endpoint routers."""

from fastapi import APIRouter

from app.api.v1 import (
    admin,
    auth,
    users,
    units,
    beneficiaries,
    pais,
    objectives,
    journal,
    documents,
    dashboard,
    notifications,
    reports,
    skills,
    time_tracking,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(units.router, prefix="/units", tags=["Units"])
api_router.include_router(beneficiaries.router, prefix="/beneficiaries", tags=["Beneficiaries"])
api_router.include_router(pais.router, prefix="/pais", tags=["PAIs"])
api_router.include_router(pais.beneficiary_pais_router, prefix="/beneficiaries", tags=["PAIs"])
api_router.include_router(objectives.router, prefix="/objectives", tags=["Objectives"])
api_router.include_router(journal.router, prefix="/journal", tags=["Journal"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(skills.router, prefix="/skills", tags=["Skills"])
api_router.include_router(time_tracking.router, prefix="/beneficiaries", tags=["Time Tracking"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
