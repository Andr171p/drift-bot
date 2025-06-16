from typing import Optional

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .domain import Event


class CreatedEvent(Event):
    id: int
    created_at: datetime
    updated_at: datetime


class SendingEvent(BaseModel):
    """Отправка мероприятия пользователю"""
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


class SendingPilot(BaseModel):
    """Отправка пилота пользователю"""
    full_name: str
    age: int
    description: str
    photo: bytes
    car: str
    created_at: datetime
