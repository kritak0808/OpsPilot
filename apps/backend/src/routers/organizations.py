from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.connection import get_session
from src.dependencies.auth import get_current_user, require_role, require_permission
from src.models.auth import User, Organization, OrganizationMember, Role
from src.repositories.org import OrganizationRepository
from src.repositories.user import UserRepository
from src.schemas.auth import OrgCreate, OrgResponse, MemberInvite

router = APIRouter(prefix="/api/v1/organizations", tags=["Organizations"])

class OrgPatch(BaseModel):
    name: Optional[str] = None

# ==========================================
# Create Organization
# ==========================================

@router.post("", response_model=OrgResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrgCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    repo = OrganizationRepository(db)

    # Check unique slug
    existing_org = await repo.get_by_slug(payload.slug)
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An organization with this slug identifier already exists.",
        )

    org = Organization(name=payload.name, slug=payload.slug)
    created_org = await repo.create(org)

    # Assign creating user as OrgOwner role
    role_query = select(Role).where(Role.name == "OrgOwner")
    role_result = await db.execute(role_query)
    owner_role = role_result.scalar_one_or_none()

    if not owner_role:
        # Fallback role auto-provision
        owner_role = Role(name="OrgOwner", description="Organization Owner Role")
        db.add(owner_role)
        await db.commit()
        await db.refresh(owner_role)

    membership = OrganizationMember(
        organization_id=created_org.id,
        user_id=current_user.id,
        role_id=owner_role.id,
    )
    await repo.add_member(membership)

    return created_org

# ==========================================
# List User's Organizations
# ==========================================

@router.get("", response_model=List[OrgResponse])
async def list_user_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    repo = OrganizationRepository(db)
    return await repo.list_for_user(current_user.id)

# ==========================================
# Fetch Organization by ID
# ==========================================

@router.get("/{id}", response_model=OrgResponse)
async def get_organization(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    repo = OrganizationRepository(db)
    org = await repo.get_by_id(id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")
    
    # Security: Verify membership
    membership = await repo.get_membership(id, current_user.id)
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied to this organization.")

    return org

# ==========================================
# Patch Organization settings
# ==========================================

@router.patch("/{id}", response_model=OrgResponse)
async def patch_organization(
    id: UUID,
    payload: OrgPatch,
    current_user: User = Depends(require_role(["OrgOwner", "Admin"])),
    db: AsyncSession = Depends(get_session),
):
    repo = OrganizationRepository(db)
    org = await repo.get_by_id(id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")

    if payload.name is not None:
        org.name = payload.name
    return await repo.update(org)

# ==========================================
# Invite Member (OrgOwner / Admin scope)
# ==========================================

@router.post("/{id}/members", status_code=status.HTTP_201_CREATED)
async def add_organization_member(
    id: UUID,
    payload: MemberInvite,
    current_user: User = Depends(require_role(["OrgOwner", "Admin"])),
    db: AsyncSession = Depends(get_session),
):
    user_repo = UserRepository(db)
    org_repo = OrganizationRepository(db)

    # Locate user by email
    target_user = await user_repo.get_by_email(payload.email)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invited user profile does not exist.",
        )

    # Verify if user is already a member
    existing_membership = await org_repo.get_membership(id, target_user.id)
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this organization.",
        )

    # Load target role
    role_query = select(Role).where(Role.name == payload.role_name)
    role_result = await db.execute(role_query)
    target_role = role_result.scalar_one_or_none()
    if not target_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested role '{payload.role_name}' is not recognized.",
        )

    membership = OrganizationMember(
        organization_id=id,
        user_id=target_user.id,
        role_id=target_role.id,
    )
    await org_repo.add_member(membership)
    return {"message": "Member successfully added to organization."}

# ==========================================
# Delete Member (OrgOwner / Admin scope)
# ==========================================

@router.delete("/{id}/members/{userId}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_organization_member(
    id: UUID,
    userId: UUID,
    current_user: User = Depends(require_role(["OrgOwner", "Admin"])),
    db: AsyncSession = Depends(get_session),
):
    org_repo = OrganizationRepository(db)
    
    # Restrict self-removal to avoid leaving org without owner
    if current_user.id == userId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owners cannot delete themselves from organization membership.",
        )

    deleted = await org_repo.remove_member(id, userId)
    if not deleted:
        raise HTTPException(status_code=404, detail="Member association not found.")
