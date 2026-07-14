from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class PipelineCreate(BaseModel):
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    description: Optional[str] = None
    yaml_config: str = Field(min_length=1)

class PipelineResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PipelineRunResponse(BaseModel):
    id: UUID
    pipeline_id: UUID
    status: str
    trigger_type: str
    commit_sha: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ArtifactResponse(BaseModel):
    id: UUID
    run_job_id: UUID
    name: str
    path: str
    checksum: str
    size_bytes: int
    created_at: datetime

    class Config:
        from_attributes = True
