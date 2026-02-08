from dataclasses import dataclass

@dataclass
class Message:
    conversation_id: str
    id: str
    author: str
    message: str
