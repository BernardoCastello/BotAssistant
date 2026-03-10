import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.adapters.admin.router import router as admin_router
from src.adapters.telegram.router import router as telegram_router
from src.db.mongo import connect as mongo_connect
from src.db.mongo import disconnect as mongo_disconnect
from src.db.postgres import connect as pg_connect
from src.db.postgres import disconnect as pg_disconnect
from src.db.redis import connect as redis_connect
from src.db.redis import disconnect as redis_disconnect

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🤖 Bot iniciando...")
    await mongo_connect()
    await pg_connect()
    await redis_connect()
    yield
    await mongo_disconnect()
    await pg_disconnect()
    await redis_disconnect()
    logger.info("🛑 Bot encerrado.")


app = FastAPI(title="Personal Assistant Bot", lifespan=lifespan)
app.include_router(telegram_router, prefix="/webhook")
app.include_router(admin_router, prefix="/admin")


@app.get("/health")
async def health():
    return {"status": "ok"}
