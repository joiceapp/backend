from datetime import datetime
from fastapi import APIRouter
from math import pow, sqrt,cos
from typing import Any

from .. import models
from ..auth import get_user, user_auth
from ..database import db, filter_by, select
from ..exceptions import responses
from ..exceptions.auth import PermissionDeniedError, user_responses
from ..exceptions.events import AlreadyParticipantException, EventNotFound
from ..exceptions.user import UserNotFoundError
from ..models.events import Event
from ..models.session import Session
from ..models.user import User
from ..schemas.event import CreateEvent, EventResponse, EventUserAccept, FilterEvent
from ..schemas.test import TestResponse


router = APIRouter(tags=["chat"])

