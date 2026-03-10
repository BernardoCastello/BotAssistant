import logging
from datetime import datetime, timezone

from openai import AsyncOpenAI

from src.config import settings
from src.db.mongo import get_db
from src.llm.prompt import SYSTEM_PROMPT
from src.models.conversation import ChatMessage, Conversation

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(api_key=settings.openai_api_key)

# Janela deslizante: quantas mensagens recentes são enviadas para a OpenAI
WINDOW_SIZE = settings.memory_window_size

# A cada quantas mensagens gera um novo resumo
SUMMARIZE_EVERY = 20


async def get_or_create_conversation(platform: str, chat_id: str, user_info: dict) -> Conversation:
    """Busca conversa existente ou cria uma nova."""
    db = get_db()
    doc = await db.conversations.find_one({"platform": platform, "chat_id": chat_id})

    if doc:
        doc.pop("_id", None)
        return Conversation(**doc)

    conversation = Conversation(
        platform=platform,
        chat_id=chat_id,
        user_info=user_info,
    )
    await db.conversations.insert_one(conversation.model_dump())
    logger.info(f"Nova conversa criada: {platform}/{chat_id}")
    return conversation


async def save_messages(platform: str, chat_id: str, user_msg: str, assistant_msg: str) -> Conversation:
    """Adiciona par de mensagens (user + assistant) na conversa e atualiza o MongoDB."""
    db = get_db()

    now = datetime.now(timezone.utc)
    new_messages = [
        ChatMessage(role="user", content=user_msg, timestamp=now),
        ChatMessage(role="assistant", content=assistant_msg, timestamp=now),
    ]

    await db.conversations.update_one(
        {"platform": platform, "chat_id": chat_id},
        {
            "$push": {"messages": {"$each": [m.model_dump() for m in new_messages]}},
            "$set": {"updated_at": now},
        },
    )

    # Recarrega para ter o estado atualizado
    doc = await db.conversations.find_one({"platform": platform, "chat_id": chat_id})
    doc.pop("_id", None)
    return Conversation(**doc)


async def build_context(conversation: Conversation) -> list[dict]:
    """
    Monta a lista de mensagens enviada para a OpenAI:
    - system prompt (com resumo se existir)
    - últimas WINDOW_SIZE mensagens
    """
    system_content = SYSTEM_PROMPT
    if conversation.summary:
        system_content += f"\n\n## Resumo do histórico desta conversa\n{conversation.summary}"

    messages = [{"role": "system", "content": system_content}]

    recent = conversation.messages[-WINDOW_SIZE:]
    for msg in recent:
        messages.append({"role": msg.role, "content": msg.content})

    return messages


async def maybe_summarize(conversation: Conversation) -> None:
    """
    Gera um novo resumo quando o total de mensagens é múltiplo de SUMMARIZE_EVERY.
    O resumo captura pontos importantes das mensagens antigas (fora da janela).
    """
    total = len(conversation.messages)
    if total < SUMMARIZE_EVERY or total % SUMMARIZE_EVERY != 0:
        return

    # Mensagens antigas (fora da janela atual)
    old_messages = conversation.messages[:-WINDOW_SIZE]
    if not old_messages:
        return

    logger.info(f"Gerando resumo para {conversation.platform}/{conversation.chat_id}...")

    history_text = "\n".join(
        f"{m.role.upper()}: {m.content}" for m in old_messages
    )

    response = await _client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=500,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um assistente que resume conversas. "
                    "Extraia os pontos mais importantes: o que o usuário perguntou, "
                    "quais informações foram fornecidas, interesses demonstrados e qualquer "
                    "contexto relevante para conversas futuras. Seja conciso."
                ),
            },
            {
                "role": "user",
                "content": f"Resuma esta conversa:\n\n{history_text}",
            },
        ],
    )

    summary = response.choices[0].message.content
    db = get_db()
    await db.conversations.update_one(
        {"platform": conversation.platform, "chat_id": conversation.chat_id},
        {"$set": {"summary": summary}},
    )
    logger.info(f"Resumo salvo para {conversation.platform}/{conversation.chat_id}")
