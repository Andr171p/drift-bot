from typing import Optional, Literal

from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator, Field, field_validator

from .enums import Role, Criterion, CarType, FileType, QualificationAttempt

from ..constants import (
    BOT_URL,
    PHOTO_FORMATS,
    MAX_TITLE_LENGTH,
    MIN_STAGES_COUNT,
    DOCUMENT_FORMATS
)


class FileMetadata(BaseModel):
    id: Optional[int] = None  # ID файла
    key: str                  # Ссылка на S3
    bucket: str               # Имя бакета в S3
    size: float               # Размер в МБ
    format: str               # Формат файла / расширение
    type: FileType            # Тип файла
    uploaded_date: datetime   # Дата загрузки

    model_config = ConfigDict(from_attributes=True)


class File(BaseModel):
    data: bytes
    file_name: str

    @property
    def size(self) -> float:
        return round(len(self.data) / (1024 * 1024), 2)

    @property
    def format(self) -> str:
        return self.file_name.split(".")[-1]

    @property
    def type(self) -> FileType:
        if self.format in PHOTO_FORMATS:
            return FileType.PHOTO
        elif self.format in DOCUMENT_FORMATS:
            return FileType.DOCUMENT
        else:
            raise ValueError("Unsupported file format")


class Car(BaseModel):
    pilot_id: Optional[int] = None  # ID пилота
    type: CarType                   # Тип авто
    name: str                       # Название авто или его марка
    plate: Optional[str] = None     # Гос номер авто
    hp: Optional[int] = None        # Мощность в Л.С (лошадиные силы)

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def check_is_plate_filled(self) -> "Car":
        if self.plate is None and self.type == CarType.TECHNICAL:
            raise ValueError("Technical car required car plate filling")
        return self


class User(BaseModel):
    user_id: int
    username: Optional[str]
    role: Role

    model_config = ConfigDict(from_attributes=True)


class Referral(BaseModel):
    stage_id: int            # ID этапа
    admin_id: int            # ID админа
    code: str                # Реферальный код, сгенерированная админом для приглашения на мероприятие
    expires_at: datetime     # срок истечения ссылки
    activated: bool = False  # Активирована ли ссылка

    model_config = ConfigDict(from_attributes=True)

    @property
    def link(self) -> str:
        return f"{BOT_URL}?start={self.code}"


class Championship(BaseModel):
    id: Optional[int] = None                                 # ID (генерируется при создании)
    user_id: int                                             # ID пользователя, который создал чемпионат
    title: str = Field(..., max_length=MAX_TITLE_LENGTH)     # Название / заголовок
    description: Optional[str] = None                        # Описание
    files: list[FileMetadata] = Field(default_factory=list)  # Прикреплённые файлы (фото, регламент ...)
    is_active: bool = Field(default=False)                   # Активен ли чемпионат
    stages_count: int = Field(..., ge=MIN_STAGES_COUNT)      # Количество этапов

    created_at: Optional[datetime] = None                    # Дата создания (присваивается БД)
    updated_at: Optional[datetime] = None                    # Дата обновления (присваивается БД)

    model_config = ConfigDict(from_attributes=True)


class Stage(BaseModel):
    id: Optional[int] = None                                           # ID Этапа
    championship_id: int                                               # ID чемпионата
    number: int                                                        # Номер этапа
    title: str                                                         # Название
    description: Optional[str] = None                                  # Описание этапа
    files: list[Optional[FileMetadata]] = Field(default_factory=list)  # Прикреплённые файлы
    location: str                                                      # Место проведения
    map_link: str                                                      # Ссылка на карты (как добраться)
    date: datetime                                                     # Дата начала
    is_active: bool = False                                            # Активен ли этап

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Participant(BaseModel):
    user_id: int                                                       # ID пользователя
    stage_id: int                                                      # ID этапа
    full_name: str                                                     # ФИО участника
    files: list[Optional[FileMetadata]] = Field(default_factory=list)  # Прикреплённые файлы

    model_config = ConfigDict(from_attributes=True)


class Judge(Participant):
    criterion: Criterion  # Оцениваемый критерий


class Pilot(Participant):
    age: int                    # Возраст пилота
    description: str            # Описание пилота (о нём и его машине, полезная информация для комментатора)
    team: Optional[str] = None  # Название команды, если пилот выступает в командном зачёте
    cars: list[Car]             # Технический авто для тех-парка
    number: int                 # Номер пилота получаемый при регистрации

    @field_validator("cars")
    def check_drift_car(self, cars: list[Car]) -> list[Car]:
        drift_car = next((car for car in cars if car.type == CarType.DRIFT), None)
        if not drift_car:
            raise ValueError("Drift car fill required")
        return cars


class Qualification(BaseModel):
    stage_id: int                  # ID этапа
    pilot_number: int              # Номер пилота
    attempt: QualificationAttempt  # Попытка
    points: float                  # Количество баллов

    model_config = ConfigDict(from_attributes=True)


class ScoringJudge(BaseModel):
    stage_id: int         # Текущий этап
    judge_id: int         # ID судьи
    pilot_number: int     # Номер пилота
    criterion: Criterion  # Критерий за который ставится оценка
    points: float         # Баллы за критерий


class Heat(BaseModel):
    stage_id: int
    first_pilot_number: int
    second_pilot_number: int


class VotingJudge(BaseModel):
    stage_id: int
    judge_id: int
    heat: Heat
    decision: int | Literal["OMT"]
