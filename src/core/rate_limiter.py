import logging
import time

from src.config import settings
from src.db.redis import get_redis

logger = logging.getLogger(__name__)


async def is_rate_limited(chat_id: str) -> bool:
    """
    Verifica se o chat_id excedeu o limite de mensagens na janela de tempo.
    Usa sliding window com sorted set do Redis:
    - Chave: ratelimit:{chat_id}
    - Score: timestamp da mensagem
    - Limite: settings.rate_limit_messages por settings.rate_limit_window segundos

    Retorna True se o usuário deve ser bloqueado.
    """
    redis = get_redis()
    key = f"ratelimit:{chat_id}"
    now = time.time()
    window_start = now - settings.rate_limit_window

    pipe = redis.pipeline()
    # Remove entradas antigas fora da janela
    pipe.zremrangebyscore(key, "-inf", window_start)
    # Adiciona a mensagem atual
    pipe.zadd(key, {str(now): now})
    # Conta mensagens na janela
    pipe.zcard(key)
    # Expira a chave após a janela (limpeza automática)
    pipe.expire(key, settings.rate_limit_window * 2)
    results = await pipe.execute()

    count = results[2]

    if count > settings.rate_limit_messages:
        logger.warning(f"Rate limit atingido para chat_id={chat_id} ({count} msgs na janela)")
        return True

    return False
