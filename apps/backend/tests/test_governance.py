import hashlib
from uuid import uuid4
import pytest
from src.models.auth import ApiKey
from src.models.governance import AuditLog, FeatureFlag

# ==========================================
# Unit Tests: API Keys Validation
# ==========================================

def test_api_key_hashing_signature() -> None:
    raw_key = "op_test_credentials_key_hash"
    hashed = hashlib.sha256(raw_key.encode()).hexdigest()
    
    org_id = uuid4()
    api_key = ApiKey(
        organization_id=org_id,
        name="Jenkins CI Token",
        prefix="op_test_",
        hash=hashed
    )
    
    assert api_key.name == "Jenkins CI Token"
    assert api_key.hash == hashed
    assert api_key.prefix == "op_test_"

# ==========================================
# Unit Tests: Audit Logs & Feature Flags
# ==========================================

def test_audit_logs_instantiation() -> None:
    project_id = uuid4()
    log = AuditLog(
        project_id=project_id,
        action="secret.rotate",
        details="Rotated deployment secret token."
    )
    assert log.action == "secret.rotate"
    assert "Rotate" in log.details

def test_feature_flag_toggle_model() -> None:
    project_id = uuid4()
    flag = FeatureFlag(
        project_id=project_id,
        key="enable-new-pipeline-scheduler",
        description="Enables concurrent pipeline schedule dispatch loops",
        is_enabled=False
    )
    assert flag.key == "enable-new-pipeline-scheduler"
    assert flag.is_enabled is False
