from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    slug: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class ApplicationCreate(BaseModel):
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    description: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    slug: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class EnvCreate(BaseModel):
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    description: Optional[str] = None

class EnvResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class RepoConnect(BaseModel):
    git_provider_id: UUID
    external_id: str
    name: str
    full_name: str
    clone_url: str
    token: str

class RepoResponse(BaseModel):
    id: UUID
    organization_id: UUID
    application_id: Optional[UUID] = None
    git_provider_id: UUID
    external_id: str
    name: str
    full_name: str
    clone_url: str
    default_branch: str
    webhook_id: Optional[str] = None

    class Config:
        from_attributes = True
