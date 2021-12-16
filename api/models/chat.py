from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, Boolean
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
    event: Event = relationship("Event", back_populates="chat_id")
    msg_text: Mapped[str] = Column(Text())
    time: Mapped[datetime] = Column(DateTime, nullable=False)
    system_message: Mapped[bool] = Column(Boolean, default=False)
    sender_id: Mapped[str] = Column(String(36), nullable=False)
