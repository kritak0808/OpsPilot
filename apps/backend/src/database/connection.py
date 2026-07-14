from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from redis.asyncio import Redis, from_url
from src.core.config import settings

# PostgreSQL Connection Engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False  # type: ignore
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# Redis Connection Factory
redis_client: Redis = from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis() -> Redis:
    return redis_client

# Health Check Probes
async def verify_db_health() -> bool:
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

async def verify_redis_health() -> bool:
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False
