from fastapi import APIRouter
from . import auth, users, challenges, institutions, matching, projects, partners, outcomes, analytics, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(challenges.router, prefix="/challenges", tags=["challenges"])
api_router.include_router(institutions.router, prefix="/institutions", tags=["institutions"])
api_router.include_router(matching.router, prefix="/matching", tags=["matching"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(partners.router, prefix="/partners", tags=["partners"])
api_router.include_router(outcomes.router, prefix="/outcomes", tags=["outcomes"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
