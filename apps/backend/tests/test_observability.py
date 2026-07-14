from uuid import uuid4
import pytest
from src.models.observability import Metric, MetricSeries, Incident, IncidentTimeline

# ==========================================
# Unit Tests: Metric Models
# ==========================================

def test_metric_model_instantiation() -> None:
    project_id = uuid4()
    metric = Metric(
        project_id=project_id,
        name="container_cpu_usage",
        type="counter",
        unit="cores"
    )
    assert metric.name == "container_cpu_usage"
    assert metric.type == "counter"
    assert metric.unit == "cores"
    assert metric.project_id == project_id

# ==========================================
# Unit Tests: Incidents timeline tracking
# ==========================================

def test_incident_timeline_event_creation() -> None:
    project_id = uuid4()
    incident = Incident(
        project_id=project_id,
        title="PostgreSQL replica sync breakdown",
        severity="P0",
        status="triggered",
        description="Write nodes replication lag exceeds threshold"
    )
    assert incident.title == "PostgreSQL replica sync breakdown"
    assert incident.severity == "P0"
    assert incident.status == "triggered"

    timeline_event = IncidentTimeline(
        incident_id=uuid4(),
        event_type="note",
        message="SRE acknowledged alert message and assigned thread"
    )
    assert timeline_event.event_type == "note"
    assert "assigned" in timeline_event.message
