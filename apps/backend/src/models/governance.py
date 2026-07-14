from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    __table_args__ = {"extend_existing": True}
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    user_id: Optional[UUID] = Field(default=None, foreign_key="users.id", ondelete="SET NULL")
    action: str = Field(nullable=False, index=True)  # user.login, secret.rotate, k8s.sync
    details: str = Field(default="{}")  # Details JSON description metadata
    ip_address: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FeatureFlag(SQLModel, table=True):
    __tablename__ = "feature_flags"
    __table_args__ = {"extend_existing": True}
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    key: str = Field(nullable=False, index=True)
    description: Optional[str] = Field(default=None)
    is_enabled: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UsageStatistic(SQLModel, table=True):
    __tablename__ = "usage_statistics"
    __table_args__ = {"extend_existing": True}
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    metric_name: str = Field(nullable=False, index=True)  # api.calls, pipeline.runs
    value: int = Field(default=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
