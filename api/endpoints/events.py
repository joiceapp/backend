from datetime import datetime
from fastapi import APIRouter
from math import cos, pow, sqrt
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

router = APIRouter(tags=["events"])

"""
Event Erstellen/ Löschen
Eventteilnahme anfragen
Eventteilnehmen auflisten/annehmen/kicken
Fehlt: events suchens
"""


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
                                      lan=event.lan,
                                      long=event.long,
                                      icon_url=event.icon_url,
                                      city=event.city,
                                      max_participants=event.max_participants
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
    if event.owner != user.id:
        return PermissionDeniedError
    await db.delete(event)

    return True


@router.post("/filter/distance/",
             responses=user_responses(
                     list,
             ))
async def filter_distance(event_filter: FilterEvent, user: models.User = get_user(
        require_self_or_admin=True)):  # user: models.User = get_user(require_self_or_admin=True)):
    event_ids = await db.all(f"""
                            SELECT * ,  SQRT(POW(69.1 * (events.lan - {event_filter.lan}), 2) +
                            POW(69.1 * ({event_filter.long} - events.long) * COS(events.lan / 57.3), 2)) AS distance    
                            FROM events HAVING distance < {event_filter.distance} ORDER BY distance LIMIT 50; """
                             )
    events = await Event.get_list_ids(event_ids)
    events_serialized = []
    for event in events:
        event_serialized = event.serialize
        print(event_serialized["lan"])
        event_serialized["destination"] = sqrt(
                pow(69.1 * (float(event_serialized["lan"]) - event_filter.lan), 2) +
                pow(69.1 * (event_filter.long - float(event_serialized["long"])) * cos(
                        float(event_serialized["lan"]) / 57.3), 2))
        event_serialized["lan"] = 0
        event_serialized["long"] = 0
        events_serialized.append(event_serialized)

    print(events_serialized)
    for event in events_serialized:
        event["current_participants"] = len(await models.Participant.get_participants(event["id"]))

    return events_serialized


@router.get("/filter/name/{name}", responses=user_responses(
        list[EventResponse]
))
async def get_event_by_name(name: str, user: models.User = get_user(require_self_or_admin=True)):
    events = await Event.get_list_ids([event async for event in await db.stream(
            f"""SELECT * FROM events WHERE name LIKE '%{name}%' ORDER BY event_time LIMIT 10""")])
    event_serialized = [event.serialize for event in events]
    for event in event_serialized:
        event["lat"] = 0
        event["long"] = 0
        event["current_participants"] = len(await models.Participant.get_participants(event["id"]))

    return event_serialized


@router.get("/filter/city/{city}", responses=user_responses(
        list[EventResponse]

))
async def get_event_by_city(city: str, user: models.User = get_user(require_self_or_admin=True)):  #
    events = await Event.get_list_ids([event async for event in await db.stream(
            f"""SELECT * FROM events WHERE city LIKE '{city}' ORDER BY event_time LIMIT 10""")])
    event_serialized = [event.serialize for event in events]

    for event in event_serialized:
        event["lat"] = 0
        event["long"] = 0
        event["current_participants"] = len(await models.Participant.get_participants(event["id"]))

    return event_serialized


@router.get("/event/{event_id}", responses=user_responses(
        EventResponse,
        EventNotFound
))
async def get_event(event_id: str, user: models.User = get_user(require_self_or_admin=True)):
    event = await models.Event.get_from_id(event_id)
    if event is None:
        return EventNotFound
    event_serialize = event.serialize
    event_participants = await  models.Participant.get_participants(event_id)
    if event.owner != user.id:
        event["lat"] = 0
        event["long"] = 0
    event_serialize["current_participants"] = len(event_participants)
    event_serialize["participants"] = [participant.serialize for participant in event_participants]

    return event_serialize


@router.get("/filter/my_events/",
            responses=user_responses(
                    list[EventResponse],
            ))
async def filter_user(user: models.User = get_user(require_self_or_admin=True)):
    # user: models.User = get_user(require_self_or_admin=True)):
    events = [event.serialize async for event in await db.stream(filter_by(models.Event, owner=user.id))]
    for event in events:
        event_participants = await  models.Participant.get_participants(event["id"])
        event["current_participants"] = len(event_participants)
        event["participants"] = [participant.serialize for participant in event_participants]

    return events


@router.get("/filter/joined_events/",
            responses=user_responses(
                    list[EventResponse],
            ))
async def filter_user_joined_events(user: models.User = get_user(require_self_or_admin=True)):
    # user: models.User = get_user(require_self_or_admin=True)):
    events = [
        event.serialize for event in
        await models.Event.get_list_ids(
                await models.Participant.get_events_where_participant(user.id)
        )]
    for event in events:
        event_participants = await models.Participant.get_participants(event["id"])
        event["current_participants"] = len(event_participants)
        event["participants"] = [participant.serialize for participant in event_participants]
        event["lat"] = 0
        event["long"] = 0
    return events


@router.get("/filter/next/{counts}",
            responses=user_responses(
                    list[EventResponse],
            ))
async def filter_event_time(counts: int, user: models.User = get_user(
        require_self_or_admin=True)):  # user: models.User = get_user(require_self_or_admin=True)):
    # print(await db.all(f"""SELECT id FROM events HAVING event_time >= '{datetime.utcnow()}' ORDER BY event_time"""))
    counts = counts if counts <= 10 else 10

    events = await Event.get_list_ids([event async for event in await db.stream(
            f"""SELECT * FROM events HAVING event_time >= '{datetime.utcnow()}' ORDER BY event_time LIMIT {counts}""")])
    events_serialized = [event.serialize for event in events]
    for event in events_serialized:
        event_participants = await models.Participant.get_participants(event["id"])
        event["current_participants"] = len(event_participants)

        event["lat"]=0
        event["long"]=0

    return events_serialized


@router.post("/request/request/{event_id}/",
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


@router.post("/request/accept/",
             responses=user_responses(
                     bool,
                     PermissionDeniedError,
                     EventNotFound,
                     UserNotFoundError
             ))
async def accept(event_user: EventUserAccept, user: models.User = get_user(require_self_or_admin=True)) -> Any:
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
                participant.remove()

            return True

    return UserNotFoundError


@router.get("/request/get/{event_id}",
            responses=user_responses(
                    list,
                    PermissionDeniedError,
                    EventNotFound,
                    UserNotFoundError
            ))
async def get(event_id: str, user: models.User = get_user(require_self_or_admin=True)) -> Any:
    event = await Event.get_from_id(event_id)

    if event is None:
        return EventNotFound
    if event.owner != user.id:
        return PermissionDeniedError
    participants = await models.Participant.get_participants(event_id)
    participants_serialized = [participant.serialize for participant in participants]
    return participants_serialized
