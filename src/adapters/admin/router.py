import logging
import secrets
from base64 import b64decode
from functools import wraps

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from src.config import settings
from src.core.retrieval_service import _embedding_to_str, _embed
from src.db.mongo import get_db
from src.db.postgres import get_pool

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBasic()


# ── Auth ──────────────────────────────────────────────────────────────────────

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    ok_user = secrets.compare_digest(credentials.username, settings.admin_user)
    ok_pass = secrets.compare_digest(credentials.password, settings.admin_password)
    if not (ok_user and ok_pass):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# ── Models ────────────────────────────────────────────────────────────────────

class KnowledgeCreate(BaseModel):
    category: str
    keywords: str
    text: str


class KnowledgeUpdate(BaseModel):
    category: str
    keywords: str
    text: str


# ── Knowledge endpoints ───────────────────────────────────────────────────────

@router.get("/knowledge")
async def list_knowledge(_=Depends(verify_admin)):
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, category, keywords, text,
                   embedding IS NOT NULL AS has_embedding,
                   created_at
            FROM knowledge
            ORDER BY created_at DESC
            """
        )
    return [
        {
            "id": r["id"],
            "category": r["category"],
            "keywords": r["keywords"],
            "text": r["text"],
            "has_embedding": r["has_embedding"],
            "created_at": r["created_at"].isoformat(),
        }
        for r in rows
    ]


@router.post("/knowledge")
async def create_knowledge(body: KnowledgeCreate, _=Depends(verify_admin)):
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO knowledge (category, keywords, text)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            body.category, body.keywords, body.text,
        )
    return {"id": row["id"], "message": "Registro criado. Gere o embedding para ativá-lo."}


@router.put("/knowledge/{item_id}")
async def update_knowledge(item_id: int, body: KnowledgeUpdate, _=Depends(verify_admin)):
    pool = get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            UPDATE knowledge
            SET category=$1, keywords=$2, text=$3, embedding=NULL
            WHERE id=$4
            """,
            body.category, body.keywords, body.text, item_id,
        )
    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    return {"message": "Atualizado. Embedding resetado — gere novamente."}


@router.delete("/knowledge/{item_id}")
async def delete_knowledge(item_id: int, _=Depends(verify_admin)):
    pool = get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM knowledge WHERE id=$1", item_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    return {"message": "Registro deletado."}


@router.post("/knowledge/{item_id}/embed")
async def generate_embedding(item_id: int, _=Depends(verify_admin)):
    """Gera embedding para um registro específico."""
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT keywords, text FROM knowledge WHERE id=$1", item_id
        )
    if not row:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    input_text = f"{row['keywords']}\n{row['text']}"
    embedding = await _embed(input_text)
    embedding_str = _embedding_to_str(embedding)

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE knowledge SET embedding=$1::vector WHERE id=$2",
            embedding_str, item_id,
        )
    return {"message": f"Embedding gerado para ID {item_id}."}


@router.post("/knowledge/embed-all")
async def embed_all_pending(_=Depends(verify_admin)):
    """Gera embeddings para todos os registros sem embedding."""
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, keywords, text FROM knowledge WHERE embedding IS NULL"
        )

    if not rows:
        return {"message": "Nenhum registro pendente.", "count": 0}

    count = 0
    for row in rows:
        input_text = f"{row['keywords']}\n{row['text']}"
        embedding = await _embed(input_text)
        embedding_str = _embedding_to_str(embedding)
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE knowledge SET embedding=$1::vector WHERE id=$2",
                embedding_str, row["id"],
            )
        count += 1

    return {"message": f"{count} embeddings gerados com sucesso.", "count": count}


# ── Conversations endpoints ───────────────────────────────────────────────────

@router.get("/conversations")
async def list_conversations(limit: int = 20, _=Depends(verify_admin)):
    db = get_db()
    cursor = db.conversations.find(
        {},
        {"chat_id": 1, "platform": 1, "user_info": 1, "updated_at": 1,
         "summary": 1, "messages": {"$slice": -1}}  # só última msg
    ).sort("updated_at", -1).limit(limit)

    docs = await cursor.to_list(length=limit)
    return [
        {
            "chat_id": d["chat_id"],
            "platform": d["platform"],
            "user_info": d.get("user_info", {}),
            "summary": d.get("summary", ""),
            "updated_at": d["updated_at"].isoformat(),
            "last_message": d["messages"][0]["content"] if d.get("messages") else "",
        }
        for d in docs
    ]


@router.get("/conversations/{chat_id}")
async def get_conversation(chat_id: str, _=Depends(verify_admin)):
    db = get_db()
    doc = await db.conversations.find_one({"chat_id": chat_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    doc.pop("_id", None)
    doc["updated_at"] = doc["updated_at"].isoformat()
    doc["created_at"] = doc["created_at"].isoformat()
    for m in doc.get("messages", []):
        m["timestamp"] = m["timestamp"].isoformat()
    return doc


# ── Metrics endpoints ─────────────────────────────────────────────────────────

@router.get("/metrics")
async def get_metrics(_=Depends(verify_admin)):
    db = get_db()

    total_conversations = await db.conversations.count_documents({})

    pipeline = [
        {"$project": {"message_count": {"$size": "$messages"}, "platform": 1, "user_info": 1, "updated_at": 1}},
        {"$sort": {"message_count": -1}},
        {"$limit": 5},
    ]
    top_users_cursor = db.conversations.aggregate(pipeline)
    top_users = await top_users_cursor.to_list(length=5)

    total_messages_pipeline = [
        {"$project": {"count": {"$size": "$messages"}}},
        {"$group": {"_id": None, "total": {"$sum": "$count"}}},
    ]
    total_msg_result = await db.conversations.aggregate(total_messages_pipeline).to_list(1)
    total_messages = total_msg_result[0]["total"] if total_msg_result else 0

    pool = get_pool()
    async with pool.acquire() as conn:
        knowledge_count = await conn.fetchval("SELECT COUNT(*) FROM knowledge")
        pending_embeddings = await conn.fetchval(
            "SELECT COUNT(*) FROM knowledge WHERE embedding IS NULL"
        )

    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "knowledge_records": knowledge_count,
        "pending_embeddings": pending_embeddings,
        "top_users": [
            {
                "name": u.get("user_info", {}).get("name", "Desconhecido"),
                "chat_id": u["_id"] if "_id" in u else "",
                "message_count": u["message_count"],
            }
            for u in top_users
        ],
    }


# ── HTML Panel ────────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def admin_panel(_=Depends(verify_admin)):
    with open("src/adapters/admin/panel.html", "r", encoding="utf-8") as f:
        return f.read()
