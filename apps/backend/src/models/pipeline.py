from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

class Pipeline(SQLModel, table=True):
    __tablename__ = "pipelines"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    slug: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    stages: List["PipelineStage"] = Relationship(back_populates="pipeline", cascade_delete=True)
    runs: List["PipelineRun"] = Relationship(back_populates="pipeline", cascade_delete=True)
    variables: List["PipelineVariable"] = Relationship(back_populates="pipeline", cascade_delete=True)
    secrets: List["PipelineSecretReference"] = Relationship(back_populates="pipeline", cascade_delete=True)

class PipelineStage(SQLModel, table=True):
    __tablename__ = "pipeline_stages"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline_id: UUID = Field(foreign_key="pipelines.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    sequence_order: int = Field(default=0)
    depends_on: Optional[str] = Field(default=None)  # Comma-separated dependencies (string list fallback)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    pipeline: Pipeline = Relationship(back_populates="stages")
    jobs: List["PipelineJob"] = Relationship(back_populates="stage", cascade_delete=True)

class PipelineJob(SQLModel, table=True):
    __tablename__ = "pipeline_jobs"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    stage_id: UUID = Field(foreign_key="pipeline_stages.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    needs: Optional[str] = Field(default=None)  # Dependencies
    runner_image: str = Field(default="ubuntu-latest")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    stage: PipelineStage = Relationship(back_populates="jobs")
    steps: List["PipelineStep"] = Relationship(back_populates="job", cascade_delete=True)

class PipelineStep(SQLModel, table=True):
    __tablename__ = "pipeline_steps"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    job_id: UUID = Field(foreign_key="pipeline_jobs.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    run_command: str = Field(nullable=False)
    sequence_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    job: PipelineJob = Relationship(back_populates="steps")

class PipelineRun(SQLModel, table=True):
    __tablename__ = "pipeline_runs"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline_id: UUID = Field(foreign_key="pipelines.id", index=True, ondelete="CASCADE")
    status: str = Field(default="pending")  # pending, running, success, failed, cancelled
    trigger_type: str = Field(default="manual")  # manual, webhook, cron
    commit_sha: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(default=None)
    finished_at: Optional[datetime] = Field(default=None)

    # Relationships
    pipeline: Pipeline = Relationship(back_populates="runs")
    run_stages: List["PipelineRunStage"] = Relationship(back_populates="run", cascade_delete=True)

class PipelineRunStage(SQLModel, table=True):
    __tablename__ = "pipeline_run_stages"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    run_id: UUID = Field(foreign_key="pipeline_runs.id", index=True, ondelete="CASCADE")
    stage_id: UUID = Field(foreign_key="pipeline_stages.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    status: str = Field(default="pending")  # pending, running, success, failed, skipped
    started_at: Optional[datetime] = Field(default=None)
    finished_at: Optional[datetime] = Field(default=None)

    # Relationships
    run: PipelineRun = Relationship(back_populates="run_stages")
    run_jobs: List["PipelineRunJob"] = Relationship(back_populates="run_stage", cascade_delete=True)

class PipelineRunJob(SQLModel, table=True):
    __tablename__ = "pipeline_run_jobs"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    run_stage_id: UUID = Field(foreign_key="pipeline_run_stages.id", index=True, ondelete="CASCADE")
    job_id: UUID = Field(foreign_key="pipeline_jobs.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    status: str = Field(default="pending")  # pending, running, success, failed, cancelled
    started_at: Optional[datetime] = Field(default=None)
    finished_at: Optional[datetime] = Field(default=None)

    # Relationships
    run_stage: PipelineRunStage = Relationship(back_populates="run_jobs")
    logs: List["PipelineRunLog"] = Relationship(back_populates="run_job", cascade_delete=True)
    artifacts: List["PipelineArtifact"] = Relationship(back_populates="run_job", cascade_delete=True)

class PipelineRunLog(SQLModel, table=True):
    __tablename__ = "pipeline_run_logs"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    run_job_id: UUID = Field(foreign_key="pipeline_run_jobs.id", index=True, ondelete="CASCADE")
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    run_job: PipelineRunJob = Relationship(back_populates="logs")

class PipelineArtifact(SQLModel, table=True):
    __tablename__ = "pipeline_artifacts"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    run_job_id: UUID = Field(foreign_key="pipeline_run_jobs.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    path: str = Field(nullable=False)
    checksum: str = Field(nullable=False)
    size_bytes: int = Field(default=0)
    retention_days: int = Field(default=30)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    run_job: PipelineRunJob = Relationship(back_populates="artifacts")

class PipelineVariable(SQLModel, table=True):
    __tablename__ = "pipeline_variables"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline_id: UUID = Field(foreign_key="pipelines.id", index=True, ondelete="CASCADE")
    key: str = Field(nullable=False)
    value: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    pipeline: Pipeline = Relationship(back_populates="variables")

class PipelineSecretReference(SQLModel, table=True):
    __tablename__ = "pipeline_secret_references"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pipeline_id: UUID = Field(foreign_key="pipelines.id", index=True, ondelete="CASCADE")
    key: str = Field(nullable=False)
    secret_name: str = Field(nullable=False)  # Key lookup reference in Vault / VaultSecrets
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    pipeline: Pipeline = Relationship(back_populates="secrets")

class ExecutionQueue(SQLModel, table=True):
    __tablename__ = "execution_queues"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    run_id: UUID = Field(foreign_key="pipeline_runs.id", index=True, ondelete="CASCADE")
    position: int = Field(default=0)
    status: str = Field(default="queued")  # queued, processing, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
