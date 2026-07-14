from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class IncidentCreate(BaseModel):
    title: str = Field(min_length=1)
    severity: str = Field(default="P0")
    description: Optional[str] = None

class IncidentResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    severity: str
    status: str
    description: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: UUID
    rule_id: UUID
    status: str
    value: float
    triggered_at: datetime

    class Config:
        from_attributes = True
