from dataclasses import dataclass, field

from marshmallow import EXCLUDE
from typing import List, Optional


@dataclass
class Sender:
    id: int
    is_bot: bool
    first_name: str
    username: str
    language_code: Optional[str]


@dataclass
class Chat:
    id: int
    first_name: str
    username: str
    type: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class Entity:
    offset: int
    length: int
    type: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class Message:
    message_id: int
    # sender: Sender = field(metadata={"data_key": "from"})
    chat: Chat
    date: int
    text: str
    # entities: Optional[List[Entity]]

    class Meta:
        unknown = EXCLUDE


@dataclass
class UpdateObj:
    update_id: int
    message: Message

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetUpdatesResponse:
    ok: bool
    result: Optional[List[UpdateObj]]

    class Meta:
        unknown = EXCLUDE


@dataclass
class SendMessageResponse:
    ok: bool
    result: Message

    class Meta:
        unknown = EXCLUDE
