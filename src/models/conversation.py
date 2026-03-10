from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Conversation(BaseModel):
    platform: str  # "telegram" | "whatsapp"
    chat_id: str
    user_info: dict = {}
    summary: str = ""  # Resumo gerado pela OpenAI quando histórico fica grande
    messages: list[ChatMessage] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
