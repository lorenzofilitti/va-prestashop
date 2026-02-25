from datetime import datetime
from typing import Literal, Optional
from uuid import uuid4

from pydantic import BaseModel


class Message(BaseModel):
    conversation_id: str
    author: Literal["assistant", "user"]
    message: Optional[str]
    # turn: int


class ConversationManager:
    def __init__(self):
        pass

    @staticmethod
    def parse_message(
            conversation_id: str,
            role: Literal["assistant", "user"],
            message: str,
    ) -> Message:
        return Message(
            conversation_id=conversation_id,
            role=role,
            message=message,
        )

    @staticmethod
    def format_conversation_history(messages: list[tuple[str, str]]) -> list[str]:
        return [f"<role>{tpl[0]}<role>: <message>{tpl[1]}<message>" for tpl in messages]