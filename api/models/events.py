from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship
from typing import Any, TYPE_CHECKING
from uuid import uuid4

from .. import models
from ..database import Base, db
from ..logger import get_logger

if TYPE_CHECKING:
    from .event_participants import Participant
    from .user import User

logger = get_logger(__name__)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = Column(String(36), primary_key=True, unique=True, nullable=False)
    chat_id: Mapped[str] = Column(String(36), unique=True, nullable=False)
    name: Mapped[str] = Column(String(45), nullable=False)
    description: Mapped[str] = Column(String(256), nullable=False)
    owner: Mapped[str] = Column(String(36), ForeignKey("user.id"), nullable=False)
    user: User = relationship("User", back_populates="events")
    event_created: Mapped[datetime] = Column(DateTime, nullable=False)
    event_time: Mapped[datetime] = Column(DateTime, nullable=False)
    tags: Mapped[str] = Column(String(256), nullable=True)
    icon_url: Mapped[str] = Column(String(1024), nullable=True)
    lan: Mapped[float] = Column(Float(14))
    long: Mapped[float] = Column(Float(14))
    max_participants: Mapped[int] = Column(Integer())
    participants: list[Participant] = relationship(
            "Participant",
            back_populates="event",
            cascade="all, delete,delete-orphan",
    )
    chat: list[Event] = relationship(
            "Chat",
            back_populates="event",
    )

    @staticmethod
    async def create(name: str, description: str, owner_id: str, event_time: datetime, tags: str,
                     lan: float, long: float, icon_url: str, max_participants) -> Event:
        current_time = datetime.utcnow()
        event = Event(
                id=str(uuid4()),
                chat_id=str(uuid4()),
                name=name,
                description=description,
                owner=owner_id,
                event_created=current_time,
                event_time=event_time,
                tags=tags,
                lan=lan,
                long=long,
                icon_url=icon_url,
                max_participants=max_participants
        )

        await db.add(event)
        return event

    @property
    def serialize(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "name": self.name,
            "description": self.description,
            "owner": self.owner,
            "event_created": self.event_created,
            "event_time": self.event_time,
            "tags": self.tags,
            "lan": self.lan,
            "long": self.long,
            "icon": self.icon_url,
            "max_participants": self.max_participants
            # "participants": self.participants
        }

    @staticmethod
    async def get_from_id(id: str) -> dict[str, Any]:
        event = await db.get(Event, id=id)
        return event

    @staticmethod
    async def get_from_chat_id(id: str) -> dict[str, Any]:
        event = await db.get(Event, chat_id=id)
        return event

    @staticmethod
    async def get_list_ids(ids: list) -> dict[str, Any]:
        events = []
        for id in ids:
            events.append(await db.get(Event, id=id))
        return events

    async def user_in_event(self, user_id: str) -> Participant:
        event_participants = await models.Participant.get_participants(self.id)
        for participant in event_participants:
            if participant.user_id == user_id and participant.accepted:
                return participant
        return None
