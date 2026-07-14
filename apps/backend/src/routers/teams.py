from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.connection import get_session
from src.dependencies.auth import get_current_user, require_role
from src.models.auth import User, Team
from src.repositories.team import TeamRepository
from src.schemas.auth import TeamCreate, TeamResponse

router = APIRouter(prefix="/api/v1/teams", tags=["Teams"])

class TeamPatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# ==========================================
# Create Team
# ==========================================

@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    payload: TeamCreate,
    x_org_id: str = Header(..., alias="X-Org-ID"),
    current_user: User = Depends(require_role(["OrgOwner", "Admin", "DevOpsEngineer"])),
    db: AsyncSession = Depends(get_session),
):
    try:
        org_uuid = UUID(x_org_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Org-ID header format.")

    repo = TeamRepository(db)
    team = Team(
        organization_id=org_uuid,
        name=payload.name,
        slug=payload.slug,
        description=payload.description
    )
    return await repo.create(team)

# ==========================================
# List Teams (Scoped to Org)
# ==========================================

@router.get("", response_model=List[TeamResponse])
async def list_teams(
    x_org_id: str = Header(..., alias="X-Org-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        org_uuid = UUID(x_org_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Org-ID header format.")

    repo = TeamRepository(db)
    return await repo.list_for_org(org_uuid)

# ==========================================
# Patch Team details
# ==========================================

@router.patch("/{id}", response_model=TeamResponse)
async def patch_team(
    id: UUID,
    payload: TeamPatch,
    current_user: User = Depends(require_role(["OrgOwner", "Admin", "DevOpsEngineer"])),
    db: AsyncSession = Depends(get_session),
):
    repo = TeamRepository(db)
    team = await repo.get_by_id(id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found.")

    if payload.name is not None:
        team.name = payload.name
    if payload.description is not None:
        team.description = payload.description

    return await repo.update(team)

# ==========================================
# Delete Team
# ==========================================

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    id: UUID,
    current_user: User = Depends(require_role(["OrgOwner", "Admin"])),
    db: AsyncSession = Depends(get_session),
):
    repo = TeamRepository(db)
    deleted = await repo.delete(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Team not found.")
