from typing import Optional

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .domain import Event


class CreatedEvent(Event):
    id: int
    created_at: datetime
    updated_at: datetime


class SendingEvent(BaseModel):
    """Отправка события пользователю"""
    id: int
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
