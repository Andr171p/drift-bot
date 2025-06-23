from typing import Optional

from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator, Field

from .enums import Role, Criterion, CarType, FileType

from ..constants import (
    ATTEMPT,
    MAX_TITLE_LENGTH,
    MIN_STAGES_COUNT,
    PHOTO_FORMATS,
    DOCUMENT_FORMATS
)


class FileMetadata(BaseModel):
    id: Optional[int] = None  # ID файла
    key: str                  # Ссылка на S3
    bucket: str               # Имя бакета в S3
    size: int                 # Размер в МБ
    format: str               # Формат файла / расширение
    type: FileType            # Тип файла
    uploaded_date: datetime   # Дата загрузки


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
    pilot_id: int                # ID пилота
    type: CarType                # Тип авто
    name: str                    # Название авто или его марка
    plate: Optional[str] = None  # Гос номер авто
    hp: Optional[int] = None     # Мощность в Л.С (лошадиные силы)

    @model_validator(mode="after")
    def check_is_plate_filled(self) -> "Car":
        if self.plate is None and self.type == CarType.TECHNICAL:
            raise ValueError("Technical car required car plate filling")
        return self


class User(BaseModel):
    user_id: int
    username: Optional[str]
    role: Role


class Referral(BaseModel):
    stage_id: int            # ID этапа
    admin_id: int            # ID админа
    code: str                # Реферальный код, сгенерированная админом для приглашения на мероприятие
    expires_at: datetime     # срок истечения ссылки
    activated: bool = False  # Активирована ли ссылка

    model_config = ConfigDict(from_attributes=True)


class Championship(BaseModel):
    id: Optional[int] = None                                 # ID (генерируется при создании)
    title: str = Field(..., max_length=MAX_TITLE_LENGTH)     # Название / заголовок
    description: Optional[str] = None                        # Описание
    files: list[FileMetadata] = Field(default_factory=list)  # Прикреплённые файлы (фото, регламент ...)
    is_active: bool = Field(default=False)                   # Активен ли чемпионат
    stages_count: int = Field(..., ge=MIN_STAGES_COUNT)      # Количество этапов

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

    model_config = ConfigDict(from_attributes=True)


class Judge(BaseModel):
    user_id: int                                                       # ID пользователя
    stage_id: int                                                      # ID этапа на котором работает судья
    full_name: str                                                     # ФИО судьи
    files: list[Optional[FileMetadata]] = Field(default_factory=list)  # Прикреплённые файлы
    criterion: Criterion                                               # Оцениваемый критерий

    model_config = ConfigDict(from_attributes=True)


class Pilot(BaseModel):
    user_id: int                                                           # ID пользователя
    stage_id: int                                                          # ID этапа в котором принимает участие пилот
    full_name: str                                                         # ФИО пилота
    age: int                                                               # Возраст пилота
    description: str                                                       # Описание пилота (о нём и его машине, полезная информация для комментатора)
    team: Optional[str] = None                                             # Название команды, если пилот выступает в командном зачёте
    files: list[Optional[FileMetadata]] = Field(default_factory=list)      # Фото пилота или его авто
    drift_car: Car                                                         # Авто на котором пилот принимает участие
    technical_car: Optional[Car] = None                                    # Технический авто для тех-парка
    number: int                                                            # Номер пилота получаемый при регистрации

    model_config = ConfigDict(from_attributes=True)


class Qualification(BaseModel):
    stage_id: int      # ID этапа
    pilot_number: int  # Номер пилота
    attempt: ATTEMPT   # Попытка
    score: float       # Количество баллов

    model_config = ConfigDict(from_attributes=True)


class ScoringJudge(BaseModel):
    judge_id: int         # ID судьи
    number: int           # Номер пилота
    criterion: Criterion  # Критерий за который ставится оценка
    score: float          # Баллы за критерий
