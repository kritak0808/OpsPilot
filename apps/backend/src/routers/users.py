from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.connection import get_session
from src.dependencies.auth import get_current_user
from src.models.auth import User
from src.repositories.user import UserRepository
from src.schemas.auth import UserResponse

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

class UserPatch(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

# ==========================================
# Fetch All Users (Admin scope)
# ==========================================

@router.get("", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    repo = UserRepository(db)
    return await repo.list_all(skip=skip, limit=limit)

# ==========================================
# Fetch User by ID
# ==========================================

@router.get("/{id}", response_model=UserResponse)
async def get_user(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    repo = UserRepository(db)
    user = await repo.get_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

# ==========================================
# Patch User Profile
# ==========================================

@router.patch("/{id}", response_model=UserResponse)
async def patch_user(
    id: UUID,
    payload: UserPatch,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    # Security: Users can only edit themselves unless they are a global administrator
    if current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this profile.",
        )

    repo = UserRepository(db)
    user = await repo.get_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.is_active is not None:
        user.is_active = payload.is_active

    return await repo.update(user)
