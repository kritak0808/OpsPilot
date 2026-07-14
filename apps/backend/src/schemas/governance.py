from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=1)
    scope: str = Field(default="read")  # read, write, admin
    expires_days: Optional[int] = 30

class ApiKeyResponse(BaseModel):
    id: UUID
    name: str
    scope: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    key_preview: Optional[str] = None

    class Config:
        from_attributes = True

class FeatureFlagCreate(BaseModel):
    key: str = Field(min_length=1)
    description: Optional[str] = None
    is_enabled: bool = Field(default=False)

class FeatureFlagResponse(BaseModel):
    id: UUID
    key: str
    description: Optional[str] = None
    is_enabled: bool

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: UUID
    action: str
    details: str
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
