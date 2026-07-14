from datetime import datetime, timedelta, UTC
from typing import Any, Dict, List, Optional
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from src.core.config import settings

# Initialize Argon2 Password Hasher
hasher = PasswordHasher()

SECRET_KEY = "opspilot-secure-jwt-signing-key-default-secret-change-me"
ALGORITHM = "HS256"

# ==========================================
# Password Hashing
# ==========================================

def hash_password(password: str) -> str:
    """
    Hashes a plaintext password using Argon2id.
    """
    return hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against an Argon2id hash.
    """
    try:
        return hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False

# ==========================================
# Token Operations
# ==========================================

def create_access_token(user_id: str, scopes: List[str] = None) -> str:
    """
    Generates a short-lived access JWT token.
    """
    payload = {
        "sub": user_id,
        "exp": datetime.now(UTC) + timedelta(minutes=15),
        "scopes": scopes or [],
        "type": "access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    """
    Generates a long-lived refresh JWT token.
    """
    payload = {
        "sub": user_id,
        "exp": datetime.now(UTC) + timedelta(days=7),
        "type": "refresh",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT token. Raises PyJWT exceptions on invalid signatures or expirations.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
