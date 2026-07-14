import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.connection import get_session
from src.dependencies.auth import get_current_user
from src.models.auth import User, ApiKey
from src.models.project import Project
from src.models.governance import AuditLog, FeatureFlag, UsageStatistic
from src.schemas.governance import ApiKeyCreate, ApiKeyResponse, FeatureFlagCreate, FeatureFlagResponse, AuditLogResponse

router = APIRouter(prefix="/api/v1", tags=["Operations & Governance"])

# ==========================================
# Settings APIs
# ==========================================

@router.get("/settings")
async def get_system_settings(
    current_user: User = Depends(get_current_user),
):
    return {
        "theme": "dark",
        "regional_format": "UTC",
        "mfa_enabled": True,
        "vault_kms_status": "synced"
    }

@router.post("/settings")
async def update_system_settings(
    payload: dict,
    current_user: User = Depends(get_current_user),
):
    return {"status": "success", "updated_settings": payload}

# ==========================================
# Notifications Feeds
# ==========================================

@router.get("/notifications")
async def list_notifications(
    current_user: User = Depends(get_current_user),
):
    return [
        {
            "id": str(UUID("00000000-0000-0000-0000-000000000001")),
            "title": "Outage Triggered P0",
            "message": "Billing Database lag exceeded threshold bounds.",
            "channel": "Slack",
            "delivered": True
        }
    ]

# ==========================================
# Audit Trail logs
# ==========================================

@router.get("/audit", response_model=List[AuditLogResponse])
async def list_audit_trail(
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        proj_uuid = UUID(x_project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Project-ID header format.")

    query = select(AuditLog).where(AuditLog.project_id == proj_uuid).order_by(AuditLog.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

# ==========================================
# API Keys Cryptographic Management
# ==========================================

@router.post("/api-keys", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def generate_api_key(
    payload: ApiKeyCreate,
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        proj_uuid = UUID(x_project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Project-ID header format.")

    project = await db.get(Project, proj_uuid)
    if not project:
        raise HTTPException(status_code=404, detail="Project context not found.")

    # Generate secure random token
    raw_token = "op_" + secrets.token_urlsafe(32)
    prefix = raw_token[:8]
    hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()
    
    expires_at = None
    if payload.expires_days:
        expires_at = datetime.utcnow() + timedelta(days=payload.expires_days)

    api_key = ApiKey(
        organization_id=project.organization_id,
        name=payload.name,
        prefix=prefix,
        hash=hashed_token,
        expires_at=expires_at
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    # Log to Audit trail
    audit = AuditLog(
        project_id=proj_uuid,
        user_id=current_user.id,
        action="api_key.create",
        details=f"Generated API Key named: {payload.name}"
    )
    db.add(audit)
    await db.commit()

    return ApiKeyResponse(
        id=api_key.id,
        name=api_key.name,
        scope="admin",
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
        key_preview=raw_token
    )

@router.get("/api-keys", response_model=List[ApiKeyResponse])
async def list_api_keys(
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        proj_uuid = UUID(x_project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Project-ID header format.")

    project = await db.get(Project, proj_uuid)
    if not project:
        raise HTTPException(status_code=404, detail="Project context not found.")

    query = select(ApiKey).where(ApiKey.organization_id == project.organization_id)
    result = await db.execute(query)
    keys = result.scalars().all()
    return [
        ApiKeyResponse(
            id=k.id,
            name=k.name,
            scope="admin",
            created_at=k.created_at,
            expires_at=k.expires_at
        )
        for k in keys
    ]

@router.delete("/api-keys/{id}")
async def revoke_api_key(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    api_key = await db.get(ApiKey, id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API Key not found.")
    
    await db.delete(api_key)
    await db.commit()
    return {"status": "revoked"}

# ==========================================
# Vault Secrets References
# ==========================================

@router.get("/secrets")
async def list_vault_secrets_metadata(
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
):
    return [
        {
            "key": "DATABASE_URL",
            "version": 2,
            "updated_at": str(datetime.utcnow()),
            "kms_encrypted": True
        }
    ]

@router.post("/secrets")
async def register_vault_secret(
    key: str,
    value: str,
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
):
    return {"key": key, "status": "stored_in_vault", "version": 1}

# ==========================================
# Feature Flags Rollouts
# ==========================================

@router.post("/feature-flags", response_model=FeatureFlagResponse, status_code=status.HTTP_201_CREATED)
async def create_feature_flag(
    payload: FeatureFlagCreate,
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        proj_uuid = UUID(x_project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Project-ID header format.")

    flag = FeatureFlag(
        project_id=proj_uuid,
        key=payload.key,
        description=payload.description,
        is_enabled=payload.is_enabled
    )
    db.add(flag)
    await db.commit()
    await db.refresh(flag)
    return flag

@router.get("/feature-flags", response_model=List[FeatureFlagResponse])
async def list_feature_flags(
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        proj_uuid = UUID(x_project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-Project-ID header format.")

    query = select(FeatureFlag).where(FeatureFlag.project_id == proj_uuid)
    result = await db.execute(query)
    return result.scalars().all()

# ==========================================
# SaaS Billing & Usage Analytics
# ==========================================

@router.get("/usage")
async def get_usage_metrics(
    x_project_id: str = Header(..., alias="X-Project-ID"),
    current_user: User = Depends(get_current_user),
):
    return {
        "api_calls_count": 14205,
        "pipeline_runs_count": 86,
        "storage_usage_bytes": 10737418240,  # 10 GB
        "active_users_count": 12,
        "license_tier": "Enterprise SaaS"
    }
