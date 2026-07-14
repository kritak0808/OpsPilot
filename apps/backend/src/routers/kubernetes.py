import asyncio
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.crypto import encrypt_token, decrypt_token
from src.core.kube import KubeClient
from src.database.connection import get_session
from src.dependencies.auth import get_current_user
from src.models.auth import User
from src.models.kubernetes import Cluster, Node, Namespace, Deployment
from src.schemas.kubernetes import ClusterImport, ClusterResponse, NodeResponse, NamespaceResponse, DeploymentResponse, DeploymentScale
from src.workers.tasks import sync_cluster_resources, execute_helm_deployment, rollback_release

router = APIRouter(prefix="/api/v1/clusters", tags=["Kubernetes"])

# ==========================================
# Import Cluster Config
# ==========================================

@router.post("/import", response_model=ClusterResponse, status_code=status.HTTP_201_CREATED)
async def import_cluster(
    payload: ClusterImport,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    # Encrypt raw kubeconfig string
    encrypted = encrypt_token(payload.kubeconfig)
    
    cluster = Cluster(
        name=payload.name,
        slug=payload.slug,
        environment_id=payload.environment_id,
        encrypted_kubeconfig=encrypted,
    )
    db.add(cluster)
    await db.commit()
    await db.refresh(cluster)

    # Sync namespaces/nodes asynchronously
    sync_cluster_resources.delay(str(cluster.id))

    return cluster

# ==========================================
# List Clusters
# ==========================================

@router.get("", response_model=List[ClusterResponse])
async def list_clusters(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    query = select(Cluster)
    result = await db.execute(query)
    return result.scalars().all()

# ==========================================
# Cluster Detail & Sync
# ==========================================

@router.get("/{id}", response_model=ClusterResponse)
async def get_cluster_details(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    cluster = await db.get(Cluster, id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found.")
    return cluster

@router.post("/{id}/sync")
async def trigger_cluster_sync(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    cluster = await db.get(Cluster, id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found.")
    
    sync_cluster_resources.delay(str(id))
    return {"status": "sync_triggered"}

# ==========================================
# Topology Resource Discoveries
# ==========================================

@router.get("/{id}/nodes", response_model=List[NodeResponse])
async def list_cluster_nodes(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    cluster = await db.get(Cluster, id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found.")

    kubeconfig = decrypt_token(cluster.encrypted_kubeconfig)
    client = KubeClient(kubeconfig)
    
    # Query capacity info from cluster client SDK wrapper
    nodes = client.list_nodes()
    
    # Map nodes to standard responses
    return [
        NodeResponse(
            id=id,
            name=n["name"],
            cpu_capacity=n["cpu"],
            memory_capacity=n["memory"],
            status=n["status"],
        )
        for n in nodes
    ]

@router.get("/{id}/namespaces", response_model=List[NamespaceResponse])
async def list_cluster_namespaces(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    cluster = await db.get(Cluster, id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found.")

    kubeconfig = decrypt_token(cluster.encrypted_kubeconfig)
    client = KubeClient(kubeconfig)
    namespaces = client.list_namespaces()
    return [NamespaceResponse(id=id, name=name, status="Active") for name in namespaces]

@router.get("/{id}/pods")
async def list_cluster_pods(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    cluster = await db.get(Cluster, id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found.")

    kubeconfig = decrypt_token(cluster.encrypted_kubeconfig)
    client = KubeClient(kubeconfig)
    return client.list_pods()

@router.get("/{id}/services")
async def list_cluster_services(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    cluster = await db.get(Cluster, id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found.")

    kubeconfig = decrypt_token(cluster.encrypted_kubeconfig)
    client = KubeClient(kubeconfig)
    return client.list_services()

@router.get("/{id}/deployments", response_model=List[DeploymentResponse])
async def list_cluster_deployments(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    cluster = await db.get(Cluster, id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found.")

    kubeconfig = decrypt_token(cluster.encrypted_kubeconfig)
    client = KubeClient(kubeconfig)
    deploys = client.list_deployments()
    return [
        DeploymentResponse(
            id=id,
            name=d["name"],
            replicas=d["replicas"],
            available_replicas=d["available_replicas"],
        )
        for d in deploys
    ]

# ==========================================
# Deployments Scaling and Rollbacks controls
# ==========================================

@router.post("/deployments/{id}/scale")
async def scale_deployment(
    id: UUID,
    payload: DeploymentScale,
    current_user: User = Depends(get_current_user),
):
    return {"deployment_id": str(id), "scaled_to": payload.replicas, "status": "scale_triggered"}

@router.post("/deployments/{id}/rollback")
async def rollback_deployment(
    id: UUID,
    current_user: User = Depends(get_current_user),
):
    rollback_release.delay(str(id), 1)
    return {"deployment_id": str(id), "target_version": 1, "status": "rollback_triggered"}

# ==========================================
# WebSocket Rollout Monitor
# ==========================================

@router.websocket("/ws/rollout/{deploymentId}")
async def rollout_websocket_stream(websocket: WebSocket, deploymentId: str):
    await websocket.accept()
    try:
        # Mock rollout tracking updates
        stages = ["pre-deploy", "rolling-update", "ready-checks", "complete"]
        for stg in stages:
            await websocket.send_json({
                "deployment_id": deploymentId,
                "stage": stg,
                "status": "processing" if stg != "complete" else "success",
                "timestamp": str(datetime.utcnow())
            })
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
