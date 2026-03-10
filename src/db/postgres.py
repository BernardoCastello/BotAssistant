import logging

import asyncpg

from src.config import settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def connect() -> None:
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=settings.postgres_uri,
        min_size=2,
        max_size=10,
    )
    logger.info("✅ PostgreSQL conectado")


async def disconnect() -> None:
    global _pool
    if _pool:
        await _pool.close()
        logger.info("🛑 PostgreSQL desconectado")


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("PostgreSQL não conectado. Chame connect() primeiro.")
    return _pool
