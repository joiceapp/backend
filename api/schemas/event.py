from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..utils import example, get_example

USERNAME_REGEX = r"^[a-zA-Z0-9]{4,32}$"
PASSWORD_REGEX = r"^((?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).{8,})?$"
MFA_CODE_REGEX = r"^\d{6}$"


class Event(BaseModel):
    id: str
    chat_id: str
    name: str
    description: str
    owner: str
    event_created: float
    event_time: float
    tags: Optional[str]
    icon_url: Optional[str]
    lan: float
    long: float
    max_participants:int
    participants: list

    Config = example(
            id="a13e63b1-9830-4604-8b7f-397d2c29955e",
            chat_id="d59f991a-9e9d-4e37-9942-90832f5e3780",
            name="event69",
            description="this is a description",
            owner="8d79558e-fd96-4f74-858e-24d579cfa529",
            event_created=1615725447.182818,
            event_time=1615735459.274742,
            tags="tag1 tag2 vegan vegetarian",
            icon_url="http://127.0.0.1/img.png",
            lan=51.503280237787784,
            long=51.503280237787789,
            max_participants=3,
            participants=[
                """ {user_id: "8826d3c7-5456-43c2-a132-b94a9d3e4121",
                  joined_at: 1615735459.274742,
                  reqeusted_at: 1615735459.274742,
                  accepted: True,
                  }"""
            ]

    )


class CreateEvent(BaseModel):
    name: str
    description: str
    event_time: datetime
    tags: Optional[str]
    icon_url: Optional[str]
    lan: float
    long: float
    max_participants:int


class EventResponse(BaseModel):
    id: str
    chat_id: str
    name: str
    description: str
    owner: str
    event_created: float
    event_time: float
    tags: Optional[str]
    icon_url: Optional[str]
    lan: str
    long: str
    max_participants:int
    participants: list


class EventUserAccept(BaseModel):
    event_id: str
    user_id: str
    accept: bool


class FilterEvent(BaseModel):
    name: Optional[str]
    tags: Optional[str]
    tags: Optional[str]
    lan: float
    long: float
    distance: int
