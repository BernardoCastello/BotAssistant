import logging

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{settings.telegram_bot_token}"


async def send_message(chat_id: int, text: str) -> None:
    """Envia mensagem para um chat do Telegram."""
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            logger.error(f"Erro ao enviar mensagem: {response.text}")
        else:
            logger.info(f"Mensagem enviada para chat_id={chat_id}")


async def set_webhook() -> dict:
    """Registra o webhook no Telegram."""
    url = f"{TELEGRAM_API}/setWebhook"
    webhook_url = f"{settings.webhook_base_url}/webhook/telegram"

    payload = {
        "url": webhook_url,
        "secret_token": settings.telegram_webhook_secret,
        "allowed_updates": ["message"],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=10)
        data = response.json()
        logger.info(f"Webhook configurado: {data}")
        return data


async def delete_webhook() -> dict:
    """Remove o webhook (útil para testes locais com polling)."""
    url = f"{TELEGRAM_API}/deleteWebhook"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, timeout=10)
        return response.json()
