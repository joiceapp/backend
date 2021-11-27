from fastapi import APIRouter
from typing import Any

from .. import models
from ..auth import get_user, user_auth
from ..database import db, filter_by, select
from ..exceptions import responses
from ..exceptions.auth import PermissionDeniedError, user_responses
from ..schemas.event import CreateEvent,EventResponse
from ..schemas.test import TestResponse

router = APIRouter(tags=["events"])


@router.post(
        "/create",
        responses=user_responses(
                EventResponse,
                PermissionDeniedError
        ),
)
async def create_user(event: CreateEvent, user: models.User = get_user(require_self_or_admin=True)) -> Any:
    print(event)
