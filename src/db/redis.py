import logging

import redis.asyncio as aioredis

from src.config import settings

logger = logging.getLogger(__name__)

_redis: aioredis.Redis | None = None


async def connect() -> None:
    global _redis
    _redis = aioredis.from_url(
        settings.redis_uri,
        decode_responses=True,
    )
    await _redis.ping()
    logger.info("✅ Redis conectado")


async def disconnect() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        logger.info("🛑 Redis desconectado")


def get_redis() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis não conectado. Chame connect() primeiro.")
    return _redis
