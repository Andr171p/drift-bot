from typing import Optional

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .domain import Event


class CreatedEvent(Event):
    created_at: datetime
    updated_at: datetime


class ReceivedEvent(BaseModel):
    title: str
    description: Optional[str]
    photo: Optional[bytes]
    location: str
    map_link: Optional[str]
    date: datetime
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
