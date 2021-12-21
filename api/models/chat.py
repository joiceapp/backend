from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, relationship
from typing import Any, TYPE_CHECKING
from uuid import uuid4

from . import Event
from .. import models
from ..database import Base, db
from ..logger import get_logger

if TYPE_CHECKING:
    from .event_participants import Participant
    from .user import User

logger = get_logger(__name__)


class Chat(Base):
    __tablename__ = "chat"
    msg_id: Mapped[str] = Column(String(36), nullable=False, primary_key=True, unique=True)
    chat_id: Mapped[str] = Column(String(36), ForeignKey("events.chat_id"), nullable=False)
    event: Event = relationship("Event", back_populates="chat")
    msg_text: Mapped[str] = Column(Text())
    time: Mapped[datetime] = Column(DateTime, nullable=False)
    system_message: Mapped[bool] = Column(Boolean, default=False)
    sender_id: Mapped[str] = Column(String(36), nullable=False)

    @staticmethod
    async def create(chat_id: str, msg: str, user_id: str, sys_msg: bool = False) -> Chat:
        current_time = datetime.utcnow()
        chat = Chat(
                msg_id=str(uuid4()),
                chat_id=chat_id,
                msg_text=msg,
                time=datetime.utcnow(),
                system_message=sys_msg,
                sender_id=user_id
        )

        await db.add(chat)
        return chat

    @property
    def serialize(self) -> dict[str, Any]:
        return {
            "msg_id": self.msg_id,
            "chat_id": self.chat_id,
            "msg_text": self.msg_text,
            "time": self.time,
            "system_message": self.system_message,
            "user_id": self.sender_id,
        }

    @staticmethod
    async def get_form_ids(ids) -> list:
        msgs = []
        for id in ids:
            db_msg = await db.get(models.Chat, msg_id=id)
            msgs.append(db_msg)
        return msgs
