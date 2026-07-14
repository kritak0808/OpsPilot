from datetime import datetime, timedelta, UTC
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import jwt

from src.core.exceptions import AppException
from src.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from src.database.connection import get_session
from src.dependencies.auth import get_current_user
from src.models.auth import User, RefreshToken, Session, Role, OrganizationMember
from src.repositories.user import UserRepository
from src.schemas.auth import UserRegister, UserLogin, TokenRefresh, UserResponse, TokenResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# ==========================================
# Register User
# ==========================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_session)):
    repo = UserRepository(db)
    
    # Check duplicate email
    existing_user = await repo.get_by_email(payload.email)
    if existing_user:
        raise AppException(
            error_code="EMAIL_ALREADY_EXISTS",
            message="A user with this email address already exists.",
            status_code=status.HTTP_409_CONFLICT,
        )

    hashed_pw = hash_password(payload.password)
    user = User(
        email=payload.email,
        password_hash=hashed_pw,
        full_name=payload.full_name,
        is_active=True,
    )
    return await repo.create(user)

# ==========================================
# Login User
# ==========================================

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_session)):
    repo = UserRepository(db)
    user = await repo.get_by_email(payload.email)
    
    if not user or not verify_password(payload.password, user.password_hash):
        raise AppException(
            error_code="INVALID_CREDENTIALS",
            message="Invalid email address or password.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        raise AppException(
            error_code="USER_DEACTIVATED",
            message="Your account is deactivated.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # Load user roles scopes to embed in access token
    scopes = []
    member_query = select(OrganizationMember).where(OrganizationMember.user_id == user.id)
    member_result = await db.execute(member_query)
    memberships = member_result.scalars().all()
    for membership in memberships:
        role = await db.get(Role, membership.role_id)
        if role:
            scopes.append(f"org:{membership.organization_id}:{role.name.lower()}")

    # Issue tokens
    access = create_access_token(str(user.id), scopes=scopes)
    refresh = create_refresh_token(str(user.id))

    # Save refresh token in database
    token_record = RefreshToken(
        token=refresh,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(token_record)
    
    # Save active session audit record
    session_record = Session(
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    db.add(session_record)
    
    await db.commit()

    return TokenResponse(access_token=access, refresh_token=refresh)

# ==========================================
# Refresh Token Rotation
# ==========================================

@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(payload: TokenRefresh, db: AsyncSession = Depends(get_session)):
    try:
        claims = decode_token(payload.refresh_token)
        if claims.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type.")
        user_id = UUID(claims.get("sub"))
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    # Retrieve and rotate refresh token
    query = select(RefreshToken).where(
        RefreshToken.token == payload.refresh_token,
        RefreshToken.is_revoked == False
    )
    result = await db.execute(query)
    token_record = result.scalar_one_or_none()

    if not token_record or token_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token has been revoked or expired.")

    # Mark old token as revoked (rotation mechanism)
    token_record.is_revoked = True
    db.add(token_record)

    # Issue new tokens
    access = create_access_token(str(user_id))
    new_refresh = create_refresh_token(str(user_id))

    new_record = RefreshToken(
        token=new_refresh,
        user_id=user_id,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(new_record)
    await db.commit()

    return TokenResponse(access_token=access, refresh_token=new_refresh)

# ==========================================
# Logout (Session Revocation)
# ==========================================

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: TokenRefresh, db: AsyncSession = Depends(get_session)):
    query = select(RefreshToken).where(RefreshToken.token == payload.refresh_token)
    result = await db.execute(query)
    token_record = result.scalar_one_or_none()
    if token_record:
        token_record.is_revoked = True
        db.add(token_record)
        await db.commit()

# ==========================================
# Current User Details
# ==========================================

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
