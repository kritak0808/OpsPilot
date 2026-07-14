from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.connection import get_session
from src.dependencies.auth import get_current_user
from src.models.auth import User
from src.models.project import Environment
from src.schemas.project import EnvCreate, EnvResponse

router = APIRouter(prefix="/api/v1/environments", tags=["Environments"])

# ==========================================
# Create Environment
# ==========================================

@router.post("", response_model=EnvResponse, status_code=status.HTTP_201_CREATED)
async def create_environment(
    payload: EnvCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    env = Environment(
        name=payload.name,
        slug=payload.slug,
        description=payload.description
    )
    db.add(env)
    await db.commit()
    await db.refresh(env)
    return env

# ==========================================
# List Environments
# ==========================================

@router.get("", response_model=List[EnvResponse])
async def list_environments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    query = select(Environment)
    result = await db.execute(query)
    return result.scalars().all()
