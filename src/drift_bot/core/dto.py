from typing import Optional

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .domain import Event


class CreatedEvent(Event):
    id: int
    created_at: datetime
    updated_at: datetime


class EventWithPhoto(BaseModel):
    """Отправка мероприятия пользователю"""
    id: int
    title: str
    description: Optional[str]
    photo_data: Optional[bytes]
    location: str
    map_link: Optional[str]
    date: datetime
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PilotWithPhoto(BaseModel):
    """Отправка пилота пользователю"""
    full_name: str
    age: int
    description: str
    photo_data: bytes
    car: str
    created_at: datetime


class GivingPointsReferee(BaseModel):
    pilot_id: int
    points: int
