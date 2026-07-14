from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

# ==========================================
# Junction Tables
# ==========================================

class OrganizationMember(SQLModel, table=True):
    __tablename__ = "organization_members"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organizations.id", index=True, ondelete="CASCADE")
    user_id: UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    role_id: UUID = Field(foreign_key="roles.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TeamMember(SQLModel, table=True):
    __tablename__ = "team_members"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    team_id: UUID = Field(foreign_key="teams.id", index=True, ondelete="CASCADE")
    user_id: UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RolePermission(SQLModel, table=True):
    __tablename__ = "role_permissions"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    role_id: UUID = Field(foreign_key="roles.id", index=True, ondelete="CASCADE")
    permission_id: UUID = Field(foreign_key="permissions.id", index=True, ondelete="CASCADE")

# ==========================================
# Main Entities
# ==========================================

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)
    full_name: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    mfa_secret: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user", cascade_delete=True)
    sessions: List["Session"] = Relationship(back_populates="user", cascade_delete=True)

class Organization(SQLModel, table=True):
    __tablename__ = "organizations"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(nullable=False)
    slug: str = Field(index=True, unique=True, nullable=False)
    billing_tier: str = Field(default="free")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    teams: List["Team"] = Relationship(back_populates="organization", cascade_delete=True)
    api_keys: List["ApiKey"] = Relationship(back_populates="organization", cascade_delete=True)

class Team(SQLModel, table=True):
    __tablename__ = "teams"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organizations.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    slug: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    organization: Organization = Relationship(back_populates="teams")

class Role(SQLModel, table=True):
    __tablename__ = "roles"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True, nullable=False)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Permission(SQLModel, table=True):
    __tablename__ = "permissions"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True, nullable=False)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ==========================================
# Security & Token Verification Entities
# ==========================================

class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    token: str = Field(index=True, unique=True, nullable=False)
    user_id: UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    expires_at: datetime = Field(nullable=False)
    is_revoked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="refresh_tokens")

class Session(SQLModel, table=True):
    __tablename__ = "sessions"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    expires_at: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="sessions")

class ApiKey(SQLModel, table=True):
    __tablename__ = "api_keys"
    __table_args__ = {"extend_existing": True}
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organizations.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    prefix: str = Field(nullable=False)
    hash: str = Field(index=True, unique=True, nullable=False)
    expires_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    organization: Organization = Relationship(back_populates="api_keys")
