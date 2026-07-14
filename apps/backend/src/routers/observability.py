import asyncio
import json
import random
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.connection import get_session
from src.dependencies.auth import get_current_user
from src.models.auth import User
from src.models.project import Project
from src.models.observability import Incident, IncidentTimeline, Alert
from src.schemas.observability import IncidentCreate, IncidentResponse, AlertResponse

router = APIRouter(prefix="/api/v1", tags=["Observability"])

# ==========================================
# Metrics Explorer API (Prometheus)
# ==========================================

@router.get("/metrics")
async def query_metrics(
    x_project_id: str = Header(..., alias="X-Project-ID"),
    metric_name: str = "cpu_usage",
    current_user: User = Depends(get_current_user),
):
    # Returns 15-point mock time-series metrics
    now = int(datetime.utcnow().timestamp())
    points = []
    base_val = 45.0 if metric_name == "cpu_usage" else 256.0
    for i in range(15):
        points.append({
            "timestamp": now - (15 - i) * 60,
            "value": round(base_val + random.uniform(-10.0, 10.0), 2)
        })
    return {"metric": metric_name, "points": points}

# ==========================================
# Logs Explorer API (Loki)
# ==========================================

@router.get("/logs")
async def query_logs(
    x_project_id: str = Header(..., alias="X-Project-ID"),
    query: str = "",
    current_user: User = Depends(get_current_user),
):
    # Returns Loki log collection matching filters
    services = ["gateway-service", "auth-service", "billing-service", "kube-system"]
    levels = ["INFO", "WARN", "ERROR", "DEBUG"]
    logs = []
    for i in range(20):
        logs.append({
            "timestamp": str(datetime.utcnow()),
            "service": random.choice(services),
            "level": random.choice(levels),
            "message": f"Simulated Loki container log message line index {i}..."
        })
    return {"logs": logs}

# ==========================================
# APM Traces waterfall API (OpenTelemetry)
# ==========================================

@router.get("/traces")
async def query_traces(
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
):
    # Returns spans trace timeline representation
    trace_id = "4bf92f3577b34da6a3ce929d0e0e4736"
    return {
        "trace_id": trace_id,
        "duration_ms": 350,
        "spans": [
            {"span_id": "0000000000000001", "name": "HTTP GET /api/v1/checkout", "duration_ms": 350, "parent_span_id": None},
            {"span_id": "0000000000000002", "name": "auth-verify", "duration_ms": 80, "parent_span_id": "0000000000000001"},
            {"span_id": "0000000000000003", "name": "db-query-select-cart", "duration_ms": 120, "parent_span_id": "0000000000000001"},
            {"span_id": "0000000000000004", "name": "stripe-process-payment", "duration_ms": 150, "parent_span_id": "0000000000000001"},
        ]
    }

# ==========================================
# Incidents Triage Management API
# ==========================================

@router.post("/incidents", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    payload: IncidentCreate,
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        proj_uuid = UUID(x_project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Project-ID header format.")

    incident = Incident(
        project_id=proj_uuid,
        title=payload.title,
        severity=payload.severity,
        description=payload.description,
        status="triggered",
    )
    db.add(incident)
    await db.commit()
    await db.refresh(incident)

    # Initial timeline log
    timeline = IncidentTimeline(
        incident_id=incident.id,
        event_type="trigger",
        message=f"Incident opened automatically. Severity: {payload.severity}"
    )
    db.add(timeline)
    await db.commit()

    return incident

@router.get("/incidents", response_model=List[IncidentResponse])
async def list_incidents(
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        proj_uuid = UUID(x_project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Project-ID header format.")

    query = select(Incident).where(Incident.project_id == proj_uuid)
    result = await db.execute(query)
    return result.scalars().all()

@router.patch("/incidents/{id}", response_model=IncidentResponse)
async def update_incident(
    id: UUID,
    status_val: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    incident = await db.get(Incident, id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found.")

    incident.status = status_val
    if status_val == "resolved":
        incident.resolved_at = datetime.utcnow()
    
    db.add(incident)
    
    # Append event to timeline log
    timeline = IncidentTimeline(
        incident_id=id,
        event_type="update",
        message=f"Incident status marked as: {status_val}"
    )
    db.add(timeline)
    
    await db.commit()
    await db.refresh(incident)
    return incident

# ==========================================
# Alerts Receiver API (Prometheus Alertmanager)
# ==========================================

@router.get("/alerts", response_model=List[AlertResponse])
async def list_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    query = select(Alert)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/alerts", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def trigger_simulated_alert(
    rule_id: UUID,
    value: float,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    alert = Alert(
        rule_id=rule_id,
        status="firing",
        value=value,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert

# ==========================================
# WebSockets Real-Time Telemetry Streamer
# ==========================================

@router.websocket("/ws/telemetry")
async def telemetry_websocket_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        # Loop to emit live logs and metrics every 2 seconds
        while True:
            await websocket.send_json({
                "type": "metric",
                "name": "cpu_usage",
                "value": round(random.uniform(20.0, 80.0), 2),
                "timestamp": str(datetime.utcnow())
            })
            await asyncio.sleep(1)
            await websocket.send_json({
                "type": "log",
                "service": "api-gateway",
                "level": "INFO",
                "message": "Streamed live container log line checkpoint...",
                "timestamp": str(datetime.utcnow())
            })
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
