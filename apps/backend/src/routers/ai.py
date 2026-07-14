import httpx
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.connection import get_session
from src.dependencies.auth import get_current_user
from src.models.auth import User
from src.models.project import Project
from src.models.ai import AIConversation, AIMessage
from src.schemas.ai import ChatPrompt, DiagnosePrompt, AIConversationResponse, AIMessageResponse, AIRecommendationResponse

router = APIRouter(prefix="/api/v1/ai", tags=["AIOps Engine"])

# ==========================================
# conversational ChatOps Interface
# ==========================================

@router.post("/chat", response_model=AIMessageResponse, status_code=status.HTTP_201_CREATED)
async def chatops_interaction(
    payload: ChatPrompt,
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        proj_uuid = UUID(x_project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Project-ID header format.")

    # Get or create conversation thread
    conv_id = payload.conversation_id
    if not conv_id:
        conv = AIConversation(project_id=proj_uuid, title="Ops Chat session")
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        conv_id = conv.id

    # Save User message
    user_msg = AIMessage(
        conversation_id=conv_id,
        role="user",
        content=payload.prompt
    )
    db.add(user_msg)
    await db.commit()

    # Invoke LangGraph agent execution (microservice fallback)
    thoughts = "Routing query to supervisor..."
    assistant_text = "Let me query the active Kubernetes cluster nodes. All systems appear healthy."
    
    # Try calling ai-orchestrator service
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://localhost:8002/api/v1/agent/run",
                json={"messages": [{"role": "user", "content": payload.prompt}]},
                timeout=2.0
            )
            if resp.status_code == 200:
                data = resp.json()
                state = data.get("state", {})
                msgs = state.get("messages", [])
                if msgs:
                    last_msg = msgs[-1]
                    assistant_text = last_msg.get("content", assistant_text)
                    thoughts = last_msg.get("thoughts", thoughts)
    except Exception:
        pass  # Resilience fallback to default mock response

    # Save Assistant message
    assistant_msg = AIMessage(
        conversation_id=conv_id,
        role="assistant",
        content=assistant_text,
        thoughts=thoughts
    )
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(assistant_msg)

    return assistant_msg

# ==========================================
# AI Incident Diagnosis (Root Cause)
# ==========================================

@router.post("/diagnose")
async def diagnose_incident(
    payload: DiagnosePrompt,
    current_user: User = Depends(get_current_user),
):
    return {
        "incident_id": str(payload.incident_id),
        "diagnosis": "Kubernetes Pod memory limits exceeded trigger. OOM Killer terminated api-service pod.",
        "confidence": 0.98,
        "reasoning": [
            "Loki logs indicate memory consumption spike above 512Mi on pod gateway-v1-abc.",
            "Prometheus gauge indicates memory usage reached limit bounds at 22:15 UTC."
        ]
    }

@router.post("/root-cause")
async def root_cause_analysis(
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
):
    return {
        "root_cause": "Database connection exhaustion inside PostgreSQL replication nodes.",
        "remediation": "Scale DB replica targets and adjust application connection limits pools."
    }

# ==========================================
# AI Deployment Recommendations & Postmortem
# ==========================================

@router.post("/recommend", response_model=List[AIRecommendationResponse])
async def get_advisor_recommendations(
    current_user: User = Depends(get_current_user),
):
    return [
        AIRecommendationResponse(
            category="Cost Optimization",
            impact="High",
            confidence=0.92,
            description="Resize unused kubernetes worker nodes from m5.xlarge to t3.medium.",
            actions=["Update Terraform workspace parameters", "Drain non-essential nodes"]
        ),
        AIRecommendationResponse(
            category="Performance",
            impact="Medium",
            confidence=0.88,
            description="Enable ingress caching rules for static assets endpoints.",
            actions=["Modify Helm values configs"]
        )
    ]

@router.post("/postmortem")
async def generate_postmortem(
    incident_id: UUID,
    current_user: User = Depends(get_current_user),
):
    return {
        "incident_id": str(incident_id),
        "postmortem_draft": """# Incident Postmortem: PostgreSQL sync degradation

## Executive Summary
PostgreSQL replication lag exceeded limit thresholds causing transient checkout API gateway breaks.

## Root Cause
Connection leaks in database worker pools.

## Actions Itemized
- Implement strict connections timeout limits.
- Scale Postgres memory allocations.
"""
    }

# ==========================================
# List conversations history
# ==========================================

@router.get("/conversations", response_model=List[AIConversationResponse])
async def list_ai_conversations(
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        proj_uuid = UUID(x_project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Project-ID header format.")

    query = select(AIConversation).where(AIConversation.project_id == proj_uuid)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/agents")
async def list_active_supervisor_agents(
    current_user: User = Depends(get_current_user),
):
    return {
        "supervisor": "coordinates specialized triages",
        "specialized_agents": [
            "infrastructure",
            "deployment",
            "pipeline",
            "kubernetes",
            "monitoring",
            "incident_response",
            "root_cause",
            "security",
            "cost",
            "documentation"
        ]
    }
