from pydantic import BaseModel, Field
from typing import Optional

from ..utils import example, get_example


class MessageSent(BaseModel):
    chat_id: str
    message: str


class Message(BaseModel):
    msg_id: str
    chat_id: str
    msg_text: str
    time: str
    system_message: str
    user_id: str


class Messages(BaseModel):
    messages: list[Message]
