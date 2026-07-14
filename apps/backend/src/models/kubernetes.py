from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

class Cluster(SQLModel, table=True):
    __tablename__ = "clusters"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(nullable=False)
    slug: str = Field(index=True, unique=True, nullable=False)
    environment_id: Optional[UUID] = Field(default=None, foreign_key="environments.id", ondelete="SET NULL")
    encrypted_kubeconfig: str = Field(nullable=False)  # Encrypted using crypto symmetric key
    is_healthy: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    namespaces: List["Namespace"] = Relationship(back_populates="cluster", cascade_delete=True)
    nodes: List["Node"] = Relationship(back_populates="cluster", cascade_delete=True)

class Namespace(SQLModel, table=True):
    __tablename__ = "namespaces"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    cluster_id: UUID = Field(foreign_key="clusters.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    status: str = Field(default="Active")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    cluster: Cluster = Relationship(back_populates="namespaces")
    deployments: List["Deployment"] = Relationship(back_populates="namespace", cascade_delete=True)

class Deployment(SQLModel, table=True):
    __tablename__ = "deployments"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    namespace_id: UUID = Field(foreign_key="namespaces.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    replicas: int = Field(default=1)
    available_replicas: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    namespace: Namespace = Relationship(back_populates="deployments")
    histories: List["DeploymentHistory"] = Relationship(back_populates="deployment", cascade_delete=True)

class DeploymentHistory(SQLModel, table=True):
    __tablename__ = "deployment_histories"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    deployment_id: UUID = Field(foreign_key="deployments.id", index=True, ondelete="CASCADE")
    version: int = Field(nullable=False)
    action: str = Field(nullable=False)  # rollout, rollback, scale
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    deployment: Deployment = Relationship(back_populates="histories")

class Pod(SQLModel, table=True):
    __tablename__ = "pods"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    namespace_id: UUID = Field(foreign_key="namespaces.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    status: str = Field(default="Pending")  # Pending, Running, Succeeded, Failed, Unknown
    node_name: Optional[str] = Field(default=None)
    restart_count: int = Field(default=0)
    cpu_usage: str = Field(default="0m")
    memory_usage: str = Field(default="0Mi")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Service(SQLModel, table=True):
    __tablename__ = "services"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    namespace_id: UUID = Field(foreign_key="namespaces.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    type: str = Field(default="ClusterIP")  # ClusterIP, NodePort, LoadBalancer
    cluster_ip: Optional[str] = Field(default=None)
    ports_config: str = Field(default="[]")  # Config JSON (ports mappings)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Ingress(SQLModel, table=True):
    __tablename__ = "ingresses"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    namespace_id: UUID = Field(foreign_key="namespaces.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    host: Optional[str] = Field(default=None)
    path: str = Field(default="/")
    backend_service: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ConfigMap(SQLModel, table=True):
    __tablename__ = "configmaps"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    namespace_id: UUID = Field(foreign_key="namespaces.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    data: str = Field(default="{}")  # Key-value JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PersistentVolume(SQLModel, table=True):
    __tablename__ = "persistent_volumes"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(nullable=False)
    capacity: str = Field(nullable=False)
    access_modes: str = Field(default="ReadWriteOnce")
    status: str = Field(default="Available")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PersistentVolumeClaim(SQLModel, table=True):
    __tablename__ = "persistent_volume_claims"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    namespace_id: UUID = Field(foreign_key="namespaces.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    status: str = Field(default="Pending")
    volume_name: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Node(SQLModel, table=True):
    __tablename__ = "nodes"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    cluster_id: UUID = Field(foreign_key="clusters.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    cpu_capacity: str = Field(default="2")
    memory_capacity: str = Field(default="4Gi")
    status: str = Field(default="Ready")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    cluster: Cluster = Relationship(back_populates="nodes")

class HelmRelease(SQLModel, table=True):
    __tablename__ = "helm_releases"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    namespace_id: UUID = Field(foreign_key="namespaces.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    chart_name: str = Field(nullable=False)
    version: str = Field(nullable=False)
    status: str = Field(default="deployed")  # deployed, failed, uninstalled
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DeploymentRollback(SQLModel, table=True):
    __tablename__ = "deployment_rollbacks"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    deployment_id: UUID = Field(foreign_key="deployments.id", index=True, ondelete="CASCADE")
    rollback_version: int = Field(nullable=False)
    status: str = Field(default="pending")  # pending, success, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
