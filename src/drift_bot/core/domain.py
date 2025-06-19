from typing import Optional, Literal

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ..constants import ATTEMPT, Role, Criterion


class File(BaseModel):
    data: bytes
    format: str
    file_name: Optional[str] = None

    @property
    def size(self) -> int:
        return len(self.data) / (1024 * 1024)


class Photo(File):
    format: Literal["png", "jpg", "jpeg"]


class User(BaseModel):
    telegram_id: int
    username: Optional[str]
    role: Role


class Referral(BaseModel):
    event_id: int         # ID мероприятия
    admin_id: int         # ID админа
    code: str             # Реферальный код, сгенерированная админом для приглашения на мероприятие
    expires_at: datetime  # срок истечения ссылки

    model_config = ConfigDict(from_attributes=True)


class Event(BaseModel):
    title: str                         # Название мероприятия
    description: Optional[str] = None  # Описание мероприятия
    file_name: Optional[str] = None    # Название файла в S3
    location: str                      # Место проведения
    map_link: Optional[str] = None     # Ссылка на карты/навигатор
    date: datetime                     # Дата проведения
    active: bool = False               # True если гонка активна, False если завершилась или ещё не доступна

    model_config = ConfigDict(from_attributes=True)


class Referee(BaseModel):
    event_id: int              # ID этапа на котором работает судья
    full_name: str             # ФИО судьи
    file_name: Optional[str]   # Имя файла с фото в S3
    criterion: Criterion       # Оцениваемый критерий


class Pilot(BaseModel):
    event_id: int           # ID этапа в котором принимает участие пилот
    full_name: str          # ФИО пилота
    age: int                # Возраст пилота
    description: str        # Описание пилота (о нём и его машине, полезная информация для комментатора)
    photo: Optional[Photo]  # Фото пилота или его авто
    car: str                # Авто пилота
    number: int             # Номер пилота получаемый при регистрации


class Qualification(BaseModel):
    attempt: ATTEMPT
    points: float


class RefereeScore(BaseModel):
    full_name: str
    criterion: Criterion
    points: float


class RegisteredPilot(Pilot):
    pilot_id: int
    number: int
    date: datetime
