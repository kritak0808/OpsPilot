from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

# ==========================================
# Junction Tables
# ==========================================

class ProjectMember(SQLModel, table=True):
    __tablename__ = "project_members"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    user_id: UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    role: str = Field(default="Developer")  # Admin, Developer, Viewer
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ==========================================
# Main Entities
# ==========================================

class Project(SQLModel, table=True):
    __tablename__ = "projects"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organizations.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    slug: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    applications: List["Application"] = Relationship(back_populates="project", cascade_delete=True)

class Application(SQLModel, table=True):
    __tablename__ = "applications"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    slug: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    project: Project = Relationship(back_populates="applications")
    variables: List["ApplicationVariable"] = Relationship(back_populates="application", cascade_delete=True)
    repositories: List["Repository"] = Relationship(back_populates="application", cascade_delete=True)

class ApplicationVariable(SQLModel, table=True):
    __tablename__ = "application_variables"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    application_id: UUID = Field(foreign_key="applications.id", index=True, ondelete="CASCADE")
    key: str = Field(nullable=False)
    value: str = Field(nullable=False)
    is_secret: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    application: Application = Relationship(back_populates="variables")

class Environment(SQLModel, table=True):
    __tablename__ = "environments"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(nullable=False)
    slug: str = Field(unique=True, index=True, nullable=False)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    deployment_targets: List["DeploymentTarget"] = Relationship(back_populates="environment", cascade_delete=True)

class DeploymentTarget(SQLModel, table=True):
    __tablename__ = "deployment_targets"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    environment_id: UUID = Field(foreign_key="environments.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    type: str = Field(nullable=False)  # k8s, helm, server, aws_ecs
    connection_details: str = Field(nullable=False)  # Config JSON (encrypted if containing credentials)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    environment: Environment = Relationship(back_populates="deployment_targets")

# ==========================================
# Git Integration Entities
# ==========================================

class GitProvider(SQLModel, table=True):
    __tablename__ = "git_providers"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(nullable=False)  # e.g. "GitHub Enterprise", "SaaS GitHub"
    provider_type: str = Field(nullable=False)  # github, gitlab, custom
    base_url: str = Field(default="https://api.github.com")
    client_id: Optional[str] = Field(default=None)
    client_secret: Optional[str] = Field(default=None)

class Repository(SQLModel, table=True):
    __tablename__ = "repositories"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organizations.id", index=True, ondelete="CASCADE")
    application_id: Optional[UUID] = Field(default=None, foreign_key="applications.id", index=True, ondelete="SET NULL")
    git_provider_id: UUID = Field(foreign_key="git_providers.id", index=True)
    external_id: str = Field(index=True, nullable=False)  # Git provider internal ID
    name: str = Field(nullable=False)
    full_name: str = Field(nullable=False)
    clone_url: str = Field(nullable=False)
    default_branch: str = Field(default="main")
    webhook_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    application: Optional[Application] = Relationship(back_populates="repositories")
    credentials: List["RepositoryCredential"] = Relationship(back_populates="repository", cascade_delete=True)

class RepositoryCredential(SQLModel, table=True):
    __tablename__ = "repository_credentials"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    repository_id: UUID = Field(foreign_key="repositories.id", index=True, ondelete="CASCADE")
    provider_type: str = Field(nullable=False)  # github, gitlab, etc
    encrypted_token: str = Field(nullable=False)  # Secure AES-encrypted OAuth key
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    repository: Repository = Relationship(back_populates="credentials")

class Webhook(SQLModel, table=True):
    __tablename__ = "webhooks"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    external_id: str = Field(index=True, nullable=False)  # Provider ID
    url: str = Field(nullable=False)
    secret: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
