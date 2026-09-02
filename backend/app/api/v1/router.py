from fastapi import APIRouter

v1_router = APIRouter()

# Mock sub-routers since the individual modules aren't implemented in this setup yet
auth_router = APIRouter()
users_router = APIRouter()
challenges_router = APIRouter()
institutions_router = APIRouter()
matching_router = APIRouter()
projects_router = APIRouter()
partners_router = APIRouter()
outcomes_router = APIRouter()
analytics_router = APIRouter()
admin_router = APIRouter()

v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
v1_router.include_router(users_router, prefix="/users", tags=["Users"])
v1_router.include_router(challenges_router, prefix="/challenges", tags=["Challenges"])
v1_router.include_router(institutions_router, prefix="/institutions", tags=["Institutions"])
v1_router.include_router(matching_router, prefix="/matching", tags=["AI Matching"])
v1_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
v1_router.include_router(partners_router, prefix="/partners", tags=["Partners"])
v1_router.include_router(outcomes_router, prefix="/outcomes", tags=["Outcomes"])
v1_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
v1_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
