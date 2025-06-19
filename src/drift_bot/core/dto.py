from typing import Optional

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .domain import Event, Pilot, Photo


class EventWithPhoto(BaseModel):
    """Отправка мероприятия пользователю"""
    id: int
    title: str
    description: Optional[str]
    photo: Optional[Photo]
    location: str
    map_link: Optional[str]
    date: datetime
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreatedEvent(Event):
    id: int
    created_at: datetime
    updated_at: datetime

    def attach_photo(self, photo: Photo) -> EventWithPhoto:
        return EventWithPhoto(**self.model_dump(), photo=photo)


class PilotWithPhoto(BaseModel):
    """Отправка пилота пользователю"""
    id: int
    event_id: int
    full_name: str
    age: int
    description: str
    photo: Photo
    car: str
    number: int
    created_at: datetime


class CreatedPilot(Pilot):
    id: int
    created_at: datetime
    updated_at: datetime

    def attach_photo(self, photo: Photo) -> PilotWithPhoto:
        return PilotWithPhoto(**self.model_dump(), photo=photo)


class GivingPointsReferee(BaseModel):
    pilot_id: int
    points: int
