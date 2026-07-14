from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

class Metric(SQLModel, table=True):
    __tablename__ = "metrics"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    type: str = Field(default="gauge")  # gauge, counter, histogram
    unit: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    series: List["MetricSeries"] = Relationship(back_populates="metric", cascade_delete=True)

class MetricSeries(SQLModel, table=True):
    __tablename__ = "metric_series"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    metric_id: UUID = Field(foreign_key="metrics.id", index=True, ondelete="CASCADE")
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    value: float = Field(nullable=False)
    labels: str = Field(default="{}")  # JSON metadata labels
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    metric: Metric = Relationship(back_populates="series")

class LogEntry(SQLModel, table=True):
    __tablename__ = "log_entries"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    service_name: str = Field(nullable=False, index=True)
    level: str = Field(default="info", index=True)  # info, warn, error, debug
    message: str = Field(nullable=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    labels: str = Field(default="{}")  # Loki labels configuration

class Trace(SQLModel, table=True):
    __tablename__ = "traces"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    trace_id: str = Field(nullable=False, index=True)  # W3C trace id hex representation
    duration_ms: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    spans: List["Span"] = Relationship(back_populates="trace", cascade_delete=True)

class Span(SQLModel, table=True):
    __tablename__ = "spans"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    trace_uuid: UUID = Field(foreign_key="traces.id", index=True, ondelete="CASCADE")
    span_id: str = Field(nullable=False)
    parent_span_id: Optional[str] = Field(default=None)
    name: str = Field(nullable=False)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: int = Field(default=0)
    status: str = Field(default="unset")  # unset, ok, error

    # Relationships
    trace: Trace = Relationship(back_populates="spans")

class AlertRule(SQLModel, table=True):
    __tablename__ = "alert_rules"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    query: str = Field(nullable=False)  # PromQL or LogQL query representation
    threshold: float = Field(default=0.0)
    duration_seconds: int = Field(default=60)
    severity: str = Field(default="critical")  # critical, warning, info
    is_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    alerts: List["Alert"] = Relationship(back_populates="rule", cascade_delete=True)

class Alert(SQLModel, table=True):
    __tablename__ = "alerts"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    rule_id: UUID = Field(foreign_key="alert_rules.id", index=True, ondelete="CASCADE")
    status: str = Field(default="firing")  # firing, resolved
    value: float = Field(default=0.0)
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = Field(default=None)

    # Relationships
    rule: AlertRule = Relationship(back_populates="alerts")

class Incident(SQLModel, table=True):
    __tablename__ = "incidents"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    title: str = Field(nullable=False)
    severity: str = Field(default="P0")  # P0, P1, P2, P3
    status: str = Field(default="triggered")  # triggered, acknowledged, resolved
    assignee_id: Optional[UUID] = Field(default=None, foreign_key="users.id", ondelete="SET NULL")
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = Field(default=None)

    # Relationships
    timeline: List["IncidentTimeline"] = Relationship(back_populates="incident", cascade_delete=True)

class IncidentTimeline(SQLModel, table=True):
    __tablename__ = "incident_timelines"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    incident_id: UUID = Field(foreign_key="incidents.id", index=True, ondelete="CASCADE")
    event_type: str = Field(nullable=False)  # trigger, ack, note, resolve, diagnosis
    message: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    incident: Incident = Relationship(back_populates="timeline")

class HealthCheck(SQLModel, table=True):
    __tablename__ = "health_checks"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    type: str = Field(default="http")  # http, tcp, ping
    target: str = Field(nullable=False)  # Endpoint URL or host
    status: str = Field(default="healthy")  # healthy, unhealthy
    latency_ms: int = Field(default=0)
    last_checked_at: datetime = Field(default_factory=datetime.utcnow)

class ServiceDependency(SQLModel, table=True):
    __tablename__ = "service_dependencies"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    source_service: str = Field(nullable=False)
    target_service: str = Field(nullable=False)
    type: str = Field(default="http")  # http, grpc, redis, database
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SLO(SQLModel, table=True):
    __tablename__ = "slos"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    target_percentage: float = Field(default=99.9)
    time_window_days: int = Field(default=30)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    slis: List["SLI"] = Relationship(back_populates="slo", cascade_delete=True)

class SLI(SQLModel, table=True):
    __tablename__ = "slis"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    slo_id: UUID = Field(foreign_key="slos.id", index=True, ondelete="CASCADE")
    type: str = Field(default="availability")  # availability, latency
    numerator: int = Field(default=0)
    denominator: int = Field(default=0)
    current_value: float = Field(default=100.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    slo: SLO = Relationship(back_populates="slis")

class NotificationChannel(SQLModel, table=True):
    __tablename__ = "notification_channels"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(foreign_key="projects.id", index=True, ondelete="CASCADE")
    name: str = Field(nullable=False)
    type: str = Field(default="slack")  # slack, email, webhook, pagerduty
    config: str = Field(default="{}")  # Channel configurations JSON
    is_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
