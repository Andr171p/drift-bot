from typing import Optional

from datetime import datetime

from pydantic import BaseModel

from ..constants import ATTEMPT, CRITERION


class Race(BaseModel):
    title: str  # Название мероприятия
    image: Optional[bytes]  # Изображение/плакат мероприятия
    description: Optional[str]  # Описание мероприятия
    place: str  # Место проведения
    map_link: Optional[str]  # Ссылка на карты/навигатор
    date: datetime  # Дата проведения
    check_in: bool  # True если регистрация открыта, False ели закрыта или не началась
    active: bool  # True если гонка активна, False если завершилась или ещё не доступна


class Referee(BaseModel):
    full_name: str  # ФИО судьи
    criterion: CRITERION  # Оцениваемый критерий


class Pilot(BaseModel):
    full_name: str  # ФИО пилота
    age: int  # Возраст пилота
    description: str  # Описание пилота (о нём и его машине, полезная информация для комментатора)
    image: Optional[bytes]  # Фот пилота или его авто
    car: str  # Авто пилота


class Qualification(BaseModel):
    attempt: ATTEMPT
    points: float


class RefereePoints(BaseModel):
    full_name: str
    criterion: CRITERION
    points: float


class RegisteredPilot(Pilot):
    number: int
    date: datetime
