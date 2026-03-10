import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.config import settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect() -> None:
    global _client, _db
    _client = AsyncIOMotorClient(settings.mongo_uri)
    _db = _client[settings.mongo_db_name]
    # Cria índice para busca rápida por platform + chat_id
    await _db.conversations.create_index([("platform", 1), ("chat_id", 1)], unique=True)
    logger.info("✅ MongoDB conectado")


async def disconnect() -> None:
    global _client
    if _client:
        _client.close()
        logger.info("🛑 MongoDB desconectado")


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("MongoDB não conectado. Chame connect() primeiro.")
    return _db
