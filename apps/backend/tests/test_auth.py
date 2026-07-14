from uuid import uuid4
import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app
from src.core.security import hash_password, verify_password

# ==========================================
# Unit Tests: Security Helpers
# ==========================================

def test_password_hashing() -> None:
    pw = "SuperSecretPassword123"
    hashed = hash_password(pw)
    
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

# ==========================================
# API Endpoint Tests
# ==========================================

@pytest.mark.asyncio
async def test_health_check_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data

@pytest.mark.asyncio
async def test_version_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert data["api_version"] == "v1"
    assert "version" in data
