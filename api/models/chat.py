from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, String
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


class Chat(Base):
    __tablename__ = "chat"



