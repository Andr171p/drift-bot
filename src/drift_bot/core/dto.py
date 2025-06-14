from typing import Optional

from datetime import datetime

from pydantic import BaseModel

from .domain import Race


class RaceCreation(Race):
    image: Optional[bytes] = None  # Изображение/плакат мероприятия


class CreatedRace(Race):
    created_at: datetime
    updated_at: datetime


class RaceRefactoring(BaseModel):
    title: Optional[str] = None
    image: Optional[bytes] = None
    image_file_name: Optional[str] = None
    description: Optional[str] = None
    place: Optional[str] = None
    map_link: Optional[str] = None
    date: Optional[datetime] = None
    check_in: Optional[bool] = None
    active: Optional[bool] = None
