"""
Script para registrar/remover o webhook no Telegram.
Uso:
    python scripts/setup_webhook.py set    → registra o webhook
    python scripts/setup_webhook.py delete → remove o webhook
"""

import asyncio
import sys

sys.path.insert(0, ".")

from src.adapters.telegram.client import delete_webhook, set_webhook


async def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "set"

    if action == "set":
        result = await set_webhook()
        print(f"✅ Webhook configurado: {result}")
    elif action == "delete":
        result = await delete_webhook()
        print(f"🗑️  Webhook removido: {result}")
    else:
        print("Uso: python scripts/setup_webhook.py [set|delete]")


asyncio.run(main())
