from fastapi import APIRouter
from typing import Any
from datetime import datetime

from .. import models
from ..auth import get_user, user_auth
from ..database import db, filter_by, select
from ..exceptions import responses
from ..exceptions.auth import PermissionDeniedError, user_responses
from ..exceptions.events import AlreadyParticipantException, EventNotFound
from ..models.events import Event
from ..models.session import Session
from ..models.user import User
from ..exceptions.user import UserNotFoundError
from ..schemas.event import CreateEvent, EventResponse, EventUserAccept
from ..schemas.test import TestResponse

router = APIRouter(tags=["events"])


@router.post(
        "/create",

        responses=user_responses(
                EventResponse,
        ),
)
async def create_event(event: CreateEvent, user: models.User = get_user(require_self_or_admin=True)) -> Any:
    event = await models.Event.create(name=event.name,
                                      description=event.description,
                                      owner_id=user.id,
                                      event_time=event.event_time,
                                      tags=event.tags,
                                      position=event.position,
                                      icon_url=event.icon_url
                                      )
    await models.Participant.create(event_id=event.id, user_id=user.id)

    return event.serialize


@router.delete(
        "/delete/{event_id}/",

        responses=user_responses(
                bool,
                PermissionDeniedError,
                EventNotFound
        ),
)
async def delete_event(event_id: str, user: models.User = get_user(require_self_or_admin=True)) -> Any:
    event = await Event.get_from_id(event_id)
    if event is None:
        return EventNotFound

    await db.delete(event)

    return True


@router.post("/request/{event_id}/",
             responses=user_responses(
                     bool,
                     PermissionDeniedError,
                     EventNotFound,
                     AlreadyParticipantException
             ))
async def request(event_id: str, user: models.User = get_user(require_self_or_admin=True)) -> Any:
    event = await Event.get_from_id(event_id)
    if event is None:
        return EventNotFound
    participants = await models.Participant.get_participants(event_id)
    if any(participant.user_id == user.id for participant in participants):
        return AlreadyParticipantException

    await models.Participant.create(event_id, user.id);
    return True


@router.post("/accept/",
             responses=user_responses(
                     bool,
                     PermissionDeniedError,
                     EventNotFound,
                     UserNotFoundError
             ))
async def request(event_user: EventUserAccept, user: models.User = get_user(require_self_or_admin=True)) -> Any:
    event = await Event.get_from_id(event_user.event_id)

    if event is None:
        return EventNotFound
    if event.owner != user.id:
        return PermissionDeniedError
    participants = await models.Participant.get_participants(event_user.event_id)
    for participant in participants:
        if participant.user_id == event_user.user_id:
            print(participant.serialize)
            if not participant.accepted:
                participant.accepted = True
                participant.joined_at = datetime.utcnow()
            else:
                participant.accepted = True
                participant.joined_at = None

            return True

    return UserNotFoundError

