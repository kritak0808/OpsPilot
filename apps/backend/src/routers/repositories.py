from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.crypto import encrypt_token, decrypt_token
from src.database.connection import get_session
from src.dependencies.auth import get_current_user
from src.models.auth import User
from src.models.project import Repository, RepositoryCredential, GitProvider
from src.schemas.project import RepoConnect, RepoResponse
from src.services.git_provider import GitHubProvider

router = APIRouter(prefix="/api/v1/repositories", tags=["Repositories"])

# ==========================================
# Connect Repository
# ==========================================

@router.post("/connect", response_model=RepoResponse, status_code=status.HTTP_201_CREATED)
async def connect_repository(
    payload: RepoConnect,
    x_org_id: str = Header(..., alias="X-Org-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    org_uuid = UUID(x_org_id)
    
    # Verify Git Provider exists
    provider = await db.get(GitProvider, payload.git_provider_id)
    if not provider:
        # Fallback bootstrap if none exists
        provider = GitProvider(
            id=payload.git_provider_id,
            name="SaaS GitHub",
            provider_type="github",
            base_url="https://api.github.com"
        )
        db.add(provider)
        await db.commit()
        await db.refresh(provider)

    repo = Repository(
        organization_id=org_uuid,
        git_provider_id=payload.git_provider_id,
        external_id=payload.external_id,
        name=payload.name,
        full_name=payload.full_name,
        clone_url=payload.clone_url,
    )
    db.add(repo)
    await db.commit()
    await db.refresh(repo)

    # Save encrypted credentials
    encrypted = encrypt_token(payload.token)
    cred = RepositoryCredential(
        repository_id=repo.id,
        provider_type=provider.provider_type,
        encrypted_token=encrypted
    )
    db.add(cred)
    await db.commit()

    return repo

# ==========================================
# List Repositories
# ==========================================

@router.get("", response_model=List[RepoResponse])
async def list_repositories(
    x_org_id: str = Header(..., alias="X-Org-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    org_uuid = UUID(x_org_id)
    query = select(Repository).where(Repository.organization_id == org_uuid)
    result = await db.execute(query)
    return result.scalars().all()

# ==========================================
# Get Repository details
# ==========================================

@router.get("/{id}", response_model=RepoResponse)
async def get_repository(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    repo = await db.get(Repository, id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    return repo

# ==========================================
# Sync Repository (Branches & Commits metadata)
# ==========================================

@router.post("/{id}/sync")
async def sync_repository(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    repo = await db.get(Repository, id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    # Load credentials
    cred_query = select(RepositoryCredential).where(RepositoryCredential.repository_id == id)
    cred_result = await db.execute(cred_query)
    cred = cred_result.scalar_one_or_none()

    if not cred:
        raise HTTPException(status_code=400, detail="Repository credentials missing.")

    token = decrypt_token(cred.encrypted_token)

    # Sync using GitHub client helper
    provider = GitHubProvider()
    try:
        branches = await provider.list_branches(token, repo.full_name)
        commits = await provider.list_commits(token, repo.full_name)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Git provider request failed: {str(e)}")

    # Record sync metadata or trigger background tasks (represented as successful check-in)
    return {
        "repository_id": id,
        "default_branch": repo.default_branch,
        "branches": branches,
        "recent_commits_count": len(commits),
        "status": "synchronized"
    }

# ==========================================
# GitHub Webhook Receiver
# ==========================================

@router.post("/webhooks/github", status_code=status.HTTP_200_OK)
async def github_webhook_receiver(
    request: Request,
    x_hub_signature_256: str = Header(..., alias="X-Hub-Signature-256"),
    db: AsyncSession = Depends(get_session),
):
    payload_bytes = await request.body()
    
    # Signature checking
    webhook_secret = "opspilot-webhook-default-secret-signing-change-me"
    provider = GitHubProvider()
    if not provider.verify_signature(payload_bytes, x_hub_signature_256, webhook_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature validation failed."
        )

    # Decode push payload
    payload = await request.json()
    ref = payload.get("ref", "")
    commits = payload.get("commits", [])

    return {
        "status": "accepted",
        "ref": ref,
        "commits_received": len(commits)
    }
