from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class ClusterImport(BaseModel):
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    kubeconfig: str = Field(min_length=1)
    environment_id: Optional[UUID] = None

class ClusterResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    is_healthy: bool
    created_at: datetime

    class Config:
        from_attributes = True

class NodeResponse(BaseModel):
    id: UUID
    name: str
    cpu_capacity: str
    memory_capacity: str
    status: str

    class Config:
        from_attributes = True

class NamespaceResponse(BaseModel):
    id: UUID
    name: str
    status: str

    class Config:
        from_attributes = True

class DeploymentResponse(BaseModel):
    id: UUID
    name: str
    replicas: int
    available_replicas: int

    class Config:
        from_attributes = True

class DeploymentScale(BaseModel):
    replicas: int
