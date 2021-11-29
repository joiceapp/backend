from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship
from typing import Any, TYPE_CHECKING

from .events import Event
from ..database import Base, db
from ..logger import get_logger
from .. import models

if TYPE_CHECKING:
    from . import User
    from .events import Event

logger = get_logger(__name__)


class Participant(Base):
    __tablename__ = "event_participants"

    event_id: Mapped[str] = Column(String(36), ForeignKey("events.id"), nullable=False, primary_key=True)
    event: Event = relationship("Event", back_populates="participants")
    user_id: Mapped[str] = Column(String(36), ForeignKey("user.id"), nullable=False)
    user: User = relationship("User", back_populates="participates")
    joined_at: Mapped[datetime] = Column(DateTime, nullable=True)
    requested_at: Mapped[datetime] = Column(DateTime, nullable=False)
    accepted: Mapped[bool] = Column(Boolean, default=0)

    @staticmethod
    async def create(event_id: str, user_id: str) -> Event:
        joined_at = None
        accepted=False
        if (await models.Event.get_from_id(event_id)).owner == user_id:
            joined_at = datetime.utcnow()
            accepted=True

        event = Participant(
                event_id=event_id,
                user_id=user_id,
                requested_at=datetime.utcnow(),
                joined_at=joined_at,
                accepted=accepted
        )
        await db.add(event)
        return event

    @property
    def serialize(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "user_id": self.user_id,
            "joined_at": self.joined_at,
            "requested_at": self.requested_at,
            "accepted": self.accepted,
        }
