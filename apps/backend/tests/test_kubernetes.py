from uuid import uuid4
import pytest
from src.core.kube import KubeClient
from src.models.kubernetes import Cluster, Namespace, Node

# ==========================================
# Unit Tests: Cluster & Node Models
# ==========================================

def test_cluster_model_instantiation() -> None:
    env_id = uuid4()
    cluster = Cluster(
        name="Production Core EKS",
        slug="production-core-eks",
        environment_id=env_id,
        encrypted_kubeconfig="encrypted_kubeconfig_ciphertext_string_123",
        is_healthy=True
    )
    assert cluster.name == "Production Core EKS"
    assert cluster.slug == "production-core-eks"
    assert cluster.environment_id == env_id
    assert cluster.is_healthy is True

# ==========================================
# Unit Tests: KubeClient Parsing RESILIENCE
# ==========================================

def test_kubeclient_resilience_on_invalid_kubeconfig() -> None:
    # Verify client does not throw crash exceptions when an empty or invalid kubeconfig config dict is supplied
    client = KubeClient("invalid_kubeconfig_yaml_content_here")
    assert client.initialized is False
    assert client.test_connection() is False
    
    # Verify fallback discoveries return mock topologies cleanly
    nodes = client.list_nodes()
    assert len(nodes) == 1
    assert nodes[0]["name"] == "mock-node-1"

    namespaces = client.list_namespaces()
    assert "default" in namespaces
