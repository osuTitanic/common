
from dataclasses import dataclass

@dataclass(slots=True)
class Message:
    sender: str
    content: str
    target: str
    sender_id: int = 0
    is_private: bool = False

@dataclass(slots=True)
class Channel:
    name: str
    topic: str
    owner: str
    user_count: int
