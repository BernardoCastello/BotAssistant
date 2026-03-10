"""
Script para gerar embeddings de todos os registros da tabela knowledge.
Rode uma vez após popular o banco com seus dados:
    docker compose exec bot python scripts/generate_embeddings.py
"""

import asyncio
import sys

sys.path.insert(0, ".")

import asyncpg
from openai import AsyncOpenAI

from src.config import settings

EMBEDDING_MODEL = "text-embedding-3-small"


def embedding_to_str(embedding: list[float]) -> str:
    """Converte lista de floats para string no formato esperado pelo pgvector."""
    return "[" + ",".join(str(x) for x in embedding) + "]"


async def generate_embeddings():
    conn = await asyncpg.connect(dsn=settings.postgres_uri)
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    rows = await conn.fetch(
        "SELECT id, keywords, text FROM knowledge WHERE embedding IS NULL"
    )

    if not rows:
        print("✅ Todos os registros já possuem embedding.")
        await conn.close()
        return

    print(f"🔄 Gerando embeddings para {len(rows)} registros...")

    for row in rows:
        input_text = f"{row['keywords']}\n{row['text']}"

        response = await client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=input_text,
        )
        embedding_str = embedding_to_str(response.data[0].embedding)

        # Passa como string com cast explícito para vector
        await conn.execute(
            "UPDATE knowledge SET embedding = $1::vector WHERE id = $2",
            embedding_str,
            row["id"],
        )
        print(f"  ✓ ID {row['id']} processado")

    await conn.close()
    print("✅ Embeddings gerados com sucesso!")


asyncio.run(generate_embeddings())
