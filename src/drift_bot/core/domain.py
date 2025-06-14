from typing import Optional, Literal

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ..constants import ATTEMPT, CRITERION


class User(BaseModel):
    telegram_id: int
    username: Optional[str]
    phone_number: str
    role: Literal[
        "admin",
        "referee",
        "pilot"
    ]


class Event(BaseModel):
    title: str  # Название мероприятия
    photo_name: Optional[str] = None  # Изображение/плакат мероприятия
    description: Optional[str] = None  # Описание мероприятия
    location: str  # Место проведения
    map_link: Optional[str] = None  # Ссылка на карты/навигатор
    date: datetime  # Дата проведения
    active: bool = False  # True если гонка активна, False если завершилась или ещё не доступна

    model_config = ConfigDict(from_attributes=True)


class Referee(BaseModel):
    full_name: str  # ФИО судьи
    criterion: CRITERION  # Оцениваемый критерий


class Pilot(BaseModel):
    full_name: str  # ФИО пилота
    age: int  # Возраст пилота
    description: str  # Описание пилота (о нём и его машине, полезная информация для комментатора)
    photo_name: Optional[str] = None  # Фото пилота или его авто
    car: str  # Авто пилота


class Qualification(BaseModel):
    attempt: ATTEMPT
    points: float


class RefereeScore(BaseModel):
    full_name: str
    criterion: CRITERION
    points: float


class RegisteredPilot(Pilot):
    pilot_id: int
    number: int
    date: datetime
