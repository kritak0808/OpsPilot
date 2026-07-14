from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.connection import get_session
from src.dependencies.auth import get_current_user, require_role
from src.models.auth import User, OrganizationMember
from src.models.project import Project, Application
from src.schemas.project import ProjectCreate, ProjectResponse, ApplicationCreate, ApplicationResponse

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])

class ProjectPatch(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# ==========================================
# Organization Membership Check
# ==========================================

async def verify_org_membership(user_id: UUID, org_id: UUID, db: AsyncSession) -> None:
    query = select(OrganizationMember).where(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == user_id
    )
    result = await db.execute(query)
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of the specified organization context."
        )

# ==========================================
# Create Project
# ==========================================

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    x_org_id: str = Header(..., alias="X-Org-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    org_uuid = UUID(x_org_id)
    await verify_org_membership(current_user.id, org_uuid, db)

    project = Project(
        organization_id=org_uuid,
        name=payload.name,
        slug=payload.slug,
        description=payload.description
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

# ==========================================
# List Projects (Scoped to Org)
# ==========================================

@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    x_org_id: str = Header(..., alias="X-Org-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    org_uuid = UUID(x_org_id)
    await verify_org_membership(current_user.id, org_uuid, db)

    query = select(Project).where(Project.organization_id == org_uuid)
    result = await db.execute(query)
    return result.scalars().all()

# ==========================================
# Get Project Details
# ==========================================

@router.get("/{id}", response_model=ProjectResponse)
async def get_project(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    project = await db.get(Project, id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    await verify_org_membership(current_user.id, project.organization_id, db)
    return project

# ==========================================
# Patch Project
# ==========================================

@router.patch("/{id}", response_model=ProjectResponse)
async def patch_project(
    id: UUID,
    payload: ProjectPatch,
    current_user: User = Depends(require_role(["OrgOwner", "Admin"])),
    db: AsyncSession = Depends(get_session),
):
    project = await db.get(Project, id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description

    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

# ==========================================
# Delete Project
# ==========================================

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    id: UUID,
    current_user: User = Depends(require_role(["OrgOwner", "Admin"])),
    db: AsyncSession = Depends(get_session),
):
    project = await db.get(Project, id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    await db.delete(project)
    await db.commit()

# ==========================================
# Applications under Projects
# ==========================================

@router.post("/{id}/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    id: UUID,
    payload: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    project = await db.get(Project, id)
    if not project:
        raise HTTPException(status_code=404, detail="Project context not found.")

    await verify_org_membership(current_user.id, project.organization_id, db)

    app = Application(
        project_id=id,
        name=payload.name,
        slug=payload.slug,
        description=payload.description
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app

@router.get("/{id}/applications", response_model=List[ApplicationResponse])
async def list_project_applications(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    project = await db.get(Project, id)
    if not project:
        raise HTTPException(status_code=404, detail="Project context not found.")

    await verify_org_membership(current_user.id, project.organization_id, db)

    query = select(Application).where(Application.project_id == id)
    result = await db.execute(query)
    return result.scalars().all()
