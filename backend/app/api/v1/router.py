from fastapi import APIRouter

from app.api.v1 import auth, challenges, institutions, matching, users

v1_router = APIRouter()
v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
v1_router.include_router(users.router, prefix="/users", tags=["Users"])
v1_router.include_router(challenges.router, prefix="/challenges", tags=["Challenges"])
v1_router.include_router(institutions.router, prefix="/institutions", tags=["Institutions"])
v1_router.include_router(matching.router, prefix="/matching", tags=["AI Matching"])
