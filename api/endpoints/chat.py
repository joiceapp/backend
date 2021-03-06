from datetime import datetime
from fastapi import APIRouter
from math import cos, pow, sqrt
from typing import Any

from .. import models
from ..auth import get_user, user_auth
from ..database import db, filter_by, select
from ..exceptions import responses
from ..exceptions.auth import PermissionDeniedError, user_responses
from ..exceptions.chat import ChatNotFound
from ..exceptions.events import AlreadyParticipantException, EventNotFound
from ..exceptions.user import UserNotFoundError
from ..models.events import Event
from ..models.session import Session
from ..models.user import User
from ..schemas.chat import MessageSent, Messages
from ..schemas.test import TestResponse

router = APIRouter(tags=["chat"])


@router.post(
        "/chat/send/",

        responses=user_responses(
                bool,
                PermissionDeniedError,
                ChatNotFound
        ),
)
async def send_message(message: MessageSent, user: models.User = get_user(require_self_or_admin=True)) -> Any:
    event = await models.Event.get_from_chat_id(message.chat_id)
    if event is None:
        return ChatNotFound
    if event.user_in_event(user_id=user.id) is None:
        return PermissionDeniedError
    msg = await models.Chat.create(chat_id=message.chat_id, msg=message.message, user_id=user.id)
    return True


@router.get(
        "/chat/get/last/{chat_id}",

        responses=user_responses(
                Messages,
                PermissionDeniedError,
                ChatNotFound
        ),
)
async def get_messages(chat_id: str, last_fetch: datetime,
                       user: models.User = get_user(require_self_or_admin=True)) -> Any:
    event = await models.Event.get_from_chat_id(chat_id)
    if event is None:
        return ChatNotFound
    participant = await event.user_in_event(user_id=user.id)
    if participant is None:
        return PermissionDeniedError
    if participant.joined_at > last_fetch:
        last_fetch = participant.joined_at

    print(last_fetch, datetime.utcnow())
    msgs_id = await db.all(f"""
            SELECT * FROM chat WHERE chat.chat_id='{chat_id}'
            AND chat.time >= '{last_fetch}' AND chat.time <='{datetime.utcnow()}' ORDER BY chat.time 
            """)

    msgs = await models.Chat.get_form_ids(msgs_id)
    return [msg.serialize for msg in msgs]
