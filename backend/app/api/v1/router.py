"""Main API v1 router — aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, tenants, workflows, marketplace, billing, admin, workspaces, dashboard

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])
api_router.include_router(marketplace.router, prefix="/marketplace", tags=["Marketplace"])
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(dashboard.router, prefix="", tags=["Dashboard"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])
