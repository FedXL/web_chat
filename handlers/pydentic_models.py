import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class Event(str, Enum):
    message = 'message'
    new_token = 'new_token'
    ask_username = 'ask_username'
    download_history = 'download_history'


class MessageType(str, Enum):
    text = 'text'
    photo = 'photo'
    document = 'document'


class MessageDetails(BaseModel):
    message_id: int | None
    is_answer: bool
    user_id: int | None
    message_type: MessageType
    text: str | None
    extension: Optional[str] = None
    time: str = Field(default_factory=datetime.datetime.now().isoformat)


class HistoryDetails(MessageDetails):
    user_name: str




class NewTokenDetails(BaseModel):
    pass


class AskUserNameDetails(BaseModel):
    pass


class HistoryLoad(BaseModel):
    event: Event
    data: List[HistoryDetails]


class MessageLoad(BaseModel):
    """use this model to send and get ws.onmessage with Event message"""
    event: Event
    name: str | None
    details: MessageDetails
