from pydantic import BaseModel, Field


class TelegramUser(BaseModel):
    id: int
    first_name: str
    username: str | None = None
    language_code: str | None = None  # ex: "pt", "en", "es"


class TelegramChat(BaseModel):
    id: int
    type: str


class TelegramMessage(BaseModel):
    message_id: int
    from_: TelegramUser | None = Field(default=None, alias="from")
    chat: TelegramChat
    text: str | None = None
    date: int

    model_config = {"populate_by_name": True}


class TelegramUpdate(BaseModel):
    update_id: int
    message: TelegramMessage | None = None
