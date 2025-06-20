from typing import Optional, Literal

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .enums import Role, Criterion

from ..constants import ATTEMPT


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
    user_id: int
    username: Optional[str]
    role: Role


class Referral(BaseModel):
    event_id: int            # ID мероприятия
    admin_id: int            # ID админа
    code: str                # Реферальный код, сгенерированная админом для приглашения на мероприятие
    expires_at: datetime     # срок истечения ссылки
    activated: bool = False  # Активирована ли ссылка

    model_config = ConfigDict(from_attributes=True)


class Competition(BaseModel):
    title: str
    description: Optional[str] = None
    file_name: Optional[str] = None
    is_active: bool = False
    stages_count: int


class Stage(BaseModel):
    competition_id: int  # ID соревнований
    number: int          # Номер этапа
    title: str
    description: Optional[str] = None
    file_name: Optional[str] = None
    location: str
    map_link: str
    date: datetime
    is_active: bool = False


class Event(BaseModel):
    title: str                         # Название мероприятия
    description: Optional[str] = None  # Описание мероприятия
    file_name: Optional[str] = None    # Название файла в S3
    location: str                      # Место проведения
    map_link: Optional[str] = None     # Ссылка на карты/навигатор
    date: datetime                     # Дата проведения
    is_active: bool = False            # True если гонка активна, False если завершилась или ещё не доступна

    model_config = ConfigDict(from_attributes=True)


class Judge(BaseModel):
    user_id: int                     # ID пользователя
    event_id: int                    # ID этапа на котором работает судья
    full_name: str                   # ФИО судьи
    file_name: Optional[str] = None  # Имя файла с фото в S3
    criterion: Criterion             # Оцениваемый критерий


class Pilot(BaseModel):
    user_id: int                     # ID пользователя
    event_id: int                    # ID этапа в котором принимает участие пилот
    full_name: str                   # ФИО пилота
    age: int                         # Возраст пилота
    description: str                 # Описание пилота (о нём и его машине, полезная информация для комментатора)
    team: Optional[str] = None       # Название команды, если пилот выступает в командном зачёте
    file_name: Optional[str] = None  # Фото пилота или его авто
    car: str                         # Авто пилота
    number: int                      # Номер пилота получаемый при регистрации


class Qualification(BaseModel):
    number: int       # Номер пилота
    attempt: ATTEMPT  # Попытка
    points: float     # Количество баллов


class GivingPointsJudge(BaseModel):
    judge_id: int         # ID судьи
    number: int           # Номер пилота
    criterion: Criterion  # Критерий за который ставится оценка
    points: float         # Баллы за критерий


class RegisteredPilot(Pilot):
    pilot_id: int
    number: int
    date: datetime
