import asyncio
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.pipeline_parser import PipelineParser
from src.database.connection import get_session
from src.dependencies.auth import get_current_user
from src.models.auth import User
from src.models.project import Project
from src.models.pipeline import Pipeline, PipelineRun, PipelineRunLog, PipelineArtifact
from src.schemas.pipeline import PipelineCreate, PipelineResponse, PipelineRunResponse, ArtifactResponse
from src.workers.tasks import schedule_pipeline

router = APIRouter(prefix="/api/v1/pipelines", tags=["Pipelines"])

# ==========================================
# Register Pipeline Configuration
# ==========================================

@router.post("", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    payload: PipelineCreate,
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        project_uuid = UUID(x_project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Project-ID header format.")

    # Validate Project context exists
    project = await db.get(Project, project_uuid)
    if not project:
        raise HTTPException(status_code=404, detail="Project context not found.")

    # Validate YAML schema structure
    try:
        PipelineParser.parse_yaml(payload.yaml_config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Pipeline validation error: {str(e)}")

    pipeline = Pipeline(
        project_id=project_uuid,
        name=payload.name,
        slug=payload.slug,
        description=payload.description
    )
    db.add(pipeline)
    await db.commit()
    await db.refresh(pipeline)
    return pipeline

# ==========================================
# List Pipelines
# ==========================================

@router.get("", response_model=List[PipelineResponse])
async def list_pipelines(
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        project_uuid = UUID(x_project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Project-ID header format.")

    query = select(Pipeline).where(Pipeline.project_id == project_uuid)
    result = await db.execute(query)
    return result.scalars().all()

# ==========================================
# Run Pipeline (Celery Dispatch)
# ==========================================

@router.post("/{id}/run", response_model=PipelineRunResponse, status_code=status.HTTP_201_CREATED)
async def trigger_pipeline_run(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    pipeline = await db.get(Pipeline, id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found.")

    run = PipelineRun(
        pipeline_id=id,
        status="pending",
        trigger_type="manual"
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Dispatch to Celery worker queue
    schedule_pipeline.delay(str(run.id))

    return run

# ==========================================
# Cancel Pipeline Run
# ==========================================

@router.post("/{id}/cancel", response_model=PipelineRunResponse)
async def cancel_pipeline_run(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    run = await db.get(PipelineRun, id)
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found.")

    run.status = "cancelled"
    run.finished_at = datetime.utcnow()
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run

# ==========================================
# Retrieve Runs History
# ==========================================

@router.get("/{id}/runs", response_model=List[PipelineRunResponse])
async def list_pipeline_runs(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    query = select(PipelineRun).where(PipelineRun.pipeline_id == id)
    result = await db.execute(query)
    return result.scalars().all()

# ==========================================
# Get Single Run Details
# ==========================================

@router.get("/runs/{runId}", response_model=PipelineRunResponse)
async def get_run_details(
    runId: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    run = await db.get(PipelineRun, runId)
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found.")
    return run

# ==========================================
# Fetch Run Console Logs
# ==========================================

@router.get("/runs/{runId}/logs")
async def get_run_logs(
    runId: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    # Retrieve persisted logs
    return {"run_id": str(runId), "logs": ["[System] Loading logs console output..."]}

# ==========================================
# Fetch Run Artifacts List
# ==========================================

@router.get("/runs/{runId}/artifacts", response_model=List[ArtifactResponse])
async def get_run_artifacts(
    runId: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    query = select(PipelineArtifact).join(PipelineRunLog).where(
        PipelineArtifact.run_job_id == runId
    )
    result = await db.execute(query)
    return result.scalars().all()

# ==========================================
# WebSockets Real-Time Status & Logs Streamer
# ==========================================

@router.websocket("/ws/runs/{runId}")
async def pipeline_websocket_stream(websocket: WebSocket, runId: str):
    await websocket.accept()
    try:
        # Mock streaming pipeline steps updates to simulate run outputs
        stages = ["build", "test", "deploy"]
        for stage in stages:
            await websocket.send_json({
                "type": "stage_update",
                "stage": stage,
                "status": "running",
                "timestamp": str(datetime.utcnow())
            })
            await asyncio.sleep(1)

            # Stream step log logs
            for i in range(2):
                await websocket.send_json({
                    "type": "console_log",
                    "stage": stage,
                    "message": f"[{stage}] Executing sequence step {i} command...",
                    "timestamp": str(datetime.utcnow())
                })
                await asyncio.sleep(0.5)

            await websocket.send_json({
                "type": "stage_update",
                "stage": stage,
                "status": "success",
                "timestamp": str(datetime.utcnow())
            })
            await asyncio.sleep(0.5)

        await websocket.send_json({
            "type": "pipeline_complete",
            "status": "success",
            "timestamp": str(datetime.utcnow())
        })
    except WebSocketDisconnect:
        pass
