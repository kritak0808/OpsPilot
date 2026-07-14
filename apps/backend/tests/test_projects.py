import hmac
import hashlib
from uuid import uuid4
from src.core.crypto import encrypt_token, decrypt_token
from src.models.project import Project, Application
from src.services.git_provider import GitHubProvider

# ==========================================
# Unit Tests: Cryptography
# ==========================================

def test_token_encryption_decryption() -> None:
    token = "ghp_secure_github_oauth_personal_access_token_12345"
    encrypted = encrypt_token(token)
    
    assert encrypted != token
    assert decrypt_token(encrypted) == token

# ==========================================
# Unit Tests: Git Provider Signature Checks
# ==========================================

def test_github_webhook_signature_verification() -> None:
    secret = "my-webhook-signing-secret"
    payload = b'{"ref": "refs/heads/main", "commits": []}'
    
    # Calculate correct signature
    expected_hash = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    sig_header = f"sha256={expected_hash}"

    provider = GitHubProvider()
    assert provider.verify_signature(payload, sig_header, secret) is True
    assert provider.verify_signature(payload, "invalid_sig", secret) is False
    assert provider.verify_signature(payload, sig_header, "wrong_secret") is False

# ==========================================
# Unit Tests: Models
# ==========================================

def test_project_model_creation() -> None:
    org_id = uuid4()
    project = Project(
        organization_id=org_id,
        name="Security API Gateway",
        slug="security-api-gateway",
        description="Core reverse proxy node"
    )
    assert project.name == "Security API Gateway"
    assert project.slug == "security-api-gateway"
    assert project.organization_id == org_id
