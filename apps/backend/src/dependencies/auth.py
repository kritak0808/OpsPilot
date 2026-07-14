from typing import List, Optional
from uuid import UUID
import jwt
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.security import decode_token
from src.database.connection import get_session
from src.models.auth import User, OrganizationMember, Role, Permission, RolePermission

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

# ==========================================
# Resolve Current User Context
# ==========================================

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
) -> User:
    """
    FastAPI dependency extracting bearer JWT tokens and fetching the User profile.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials.",
        )
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims.",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
        )

    # Fetch User record
    user = await db.get(User, UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated or invalid.",
        )
    return user

# ==========================================
# Granular RBAC Checks
# ==========================================

class RequirementChecker:
    """
    Evaluates role permissions and organization context parameters.
    """
    def __init__(self, required_permissions: List[str], allowed_roles: List[str] = None):
        self.required_permissions = required_permissions
        self.allowed_roles = allowed_roles or []

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        x_org_id: Optional[str] = Header(None, alias="X-Org-ID"),
        db: AsyncSession = Depends(get_session),
    ) -> User:
        if not x_org_id:
            # Allow skipping org checks on global endpoints (e.g. org creation)
            if not self.required_permissions and not self.allowed_roles:
                return current_user
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-Org-ID header required for scoped resource authorization.",
            )

        try:
            org_id = UUID(x_org_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-Org-ID header is not a valid UUID format.",
            )

        # Query Organization Membership and associated Role
        query = select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == current_user.id
        )
        result = await db.execute(query)
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of the specified organization.",
            )

        # Load role details
        role = await db.get(Role, membership.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Membership role is invalid or has been decommissioned.",
            )

        # Global role permission check
        if self.allowed_roles and role.name in self.allowed_roles:
            return current_user

        # Load granular permissions associated with this role
        perm_query = select(Permission.name).join(RolePermission).where(
            RolePermission.role_id == role.id
        )
        perm_result = await db.execute(perm_query)
        user_permissions = perm_result.scalars().all()

        for permission in self.required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User requires '{permission}' permission scope.",
                )

        return current_user

# Utility shortcut helpers
def require_permission(permissions: List[str]) -> RequirementChecker:
    return RequirementChecker(required_permissions=permissions)

def require_role(roles: List[str]) -> RequirementChecker:
    return RequirementChecker(required_permissions=[], allowed_roles=roles)
