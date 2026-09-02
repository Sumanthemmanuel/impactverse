from typing import Set
from fastapi import Depends

from app.core.constants import UserRole
from app.core.exceptions import ForbiddenError
# This is imported locally in functions to avoid circular dependencies if needed
# from app.api.deps import get_current_user

ROLE_PERMISSIONS = {
    UserRole.CITIZEN: {
        "challenges:read", "challenges:create", "challenges:comment"
    },
    UserRole.VERIFIER: {
        "challenges:read", "challenges:verify", "challenges:comment"
    },
    UserRole.HEI_ADMIN: {
        "challenges:read", "projects:read", "projects:manage", "institutions:manage", "users:manage_local"
    },
    UserRole.FACULTY: {
        "challenges:read", "projects:read", "projects:create", "projects:update", "challenges:accept"
    },
    UserRole.STUDENT: {
        "challenges:read", "projects:read", "projects:participate"
    },
    UserRole.INDUSTRY: {
        "challenges:read", "projects:read", "projects:fund", "projects:mentor"
    },
    UserRole.CSR: {
        "challenges:read", "projects:read", "projects:fund"
    },
    UserRole.GOVERNMENT: {
        "challenges:read", "projects:read", "reports:read", "challenges:create"
    },
    UserRole.PLATFORM_ADMIN: {
        "admin:all", "challenges:manage", "projects:manage", "users:manage", "institutions:manage"
    }
}

def require_role(*roles: UserRole):
    """Dependency to check if user has one of the specified roles"""
    async def role_checker(current_user: dict = Depends(get_current_user_dependency)):
        user_role = current_user.get("role")
        if not user_role or user_role not in [role.value for role in roles]:
            raise ForbiddenError(f"Role not permitted. Required one of: {[r.value for r in roles]}")
        return current_user
    return role_checker

def require_permission(permission: str):
    """Dependency to check if user has specific permission based on their role"""
    async def permission_checker(current_user: dict = Depends(get_current_user_dependency)):
        user_role_str = current_user.get("role")
        
        # Admin has all permissions
        if user_role_str == UserRole.PLATFORM_ADMIN.value:
            return current_user
            
        try:
            user_role = UserRole(user_role_str)
            role_perms = ROLE_PERMISSIONS.get(user_role, set())
            
            if permission not in role_perms:
                raise ForbiddenError(f"Missing required permission: {permission}")
                
            return current_user
        except ValueError:
            raise ForbiddenError("Invalid user role")
            
    return permission_checker

# Helper to break circular dependency
def get_current_user_dependency():
    from app.api.deps import get_current_user
    return get_current_user
