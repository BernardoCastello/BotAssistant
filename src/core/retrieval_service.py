import logging

from openai import AsyncOpenAI

from src.config import settings
from src.db.postgres import get_pool

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(api_key=settings.openai_api_key)

EMBEDDING_MODEL = "text-embedding-3-small"
TOP_K = 3


def _embedding_to_str(embedding: list[float]) -> str:
    return "[" + ",".join(str(x) for x in embedding) + "]"


async def _embed(text: str) -> str:
    response = await _client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return _embedding_to_str(response.data[0].embedding)


async def semantic_search(query: str, category: str | None = None) -> str:
    pool = get_pool()
    query_embedding = await _embed(query)

    if category:
        sql = """
            SELECT text, category, 1 - (embedding <=> $1::vector) AS similarity
            FROM knowledge
            WHERE embedding IS NOT NULL
              AND category = $2
            ORDER BY embedding <=> $1::vector
            LIMIT $3
        """
        params = [query_embedding, category, TOP_K]
    else:
        sql = """
            SELECT text, category, 1 - (embedding <=> $1::vector) AS similarity
            FROM knowledge
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> $1::vector
            LIMIT $2
        """
        params = [query_embedding, TOP_K]

    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *params)

    if not rows:
        return "Nenhuma informação relevante encontrada."

    results = []
    for row in rows:
        results.append(f"[{row['category'].upper()}] {row['text']}")
        logger.info(f"Retrieval: category={row['category']} similarity={row['similarity']:.3f}")

    return "\n\n".join(results)
