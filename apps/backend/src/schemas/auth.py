from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenRefresh(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_active: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class OrgCreate(BaseModel):
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)

class OrgResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    billing_tier: str

    class Config:
        from_attributes = True

class MemberInvite(BaseModel):
    email: str
    role_name: str

class TeamCreate(BaseModel):
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    description: Optional[str] = None

class TeamResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    slug: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
