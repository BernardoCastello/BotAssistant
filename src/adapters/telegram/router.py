import logging

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from src.adapters.telegram.client import send_message
from src.config import settings
from src.core.memory_service import (
    build_context,
    get_or_create_conversation,
    maybe_summarize,
    save_messages,
)
from src.core.rate_limiter import is_rate_limited
from src.llm.openai_client import get_response
from src.models.telegram import TelegramUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


async def process_message(chat_id: str, text: str, user_name: str, user_info: dict) -> None:
    logger.info(f"Processando mensagem de {user_name} (chat_id={chat_id}): {text!r}")

    # Verifica rate limit antes de qualquer processamento
    if await is_rate_limited(chat_id):
        await send_message(
            int(chat_id),
            f"⚠️ Você enviou muitas mensagens em pouco tempo. "
            f"Aguarde {settings.rate_limit_window} segundos e tente novamente.",
        )
        return

    conversation = await get_or_create_conversation(
        platform="telegram",
        chat_id=chat_id,
        user_info=user_info,
    )

    context = await build_context(conversation)
    context.append({"role": "user", "content": text})

    answer = await get_response(context_messages=context, user_name=user_name)

    updated_conversation = await save_messages(
        platform="telegram",
        chat_id=chat_id,
        user_msg=text,
        assistant_msg=answer,
    )

    await maybe_summarize(updated_conversation)
    await send_message(int(chat_id), answer)


@router.post("/telegram")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        logger.warning("Webhook recebido com secret inválido!")
        raise HTTPException(status_code=403, detail="Forbidden")

    body = await request.json()
    update = TelegramUpdate.model_validate(body)

    if not update.message or not update.message.text:
        return {"ok": True}

    message = update.message
    chat_id = str(message.chat.id)
    text = message.text
    user_name = message.from_.first_name if message.from_ else "Desconhecido"
    user_info = {
        "name": user_name,
        "username": message.from_.username if message.from_ else None,
        "telegram_id": message.from_.id if message.from_ else None,
    }

    background_tasks.add_task(process_message, chat_id, text, user_name, user_info)

    return {"ok": True}
