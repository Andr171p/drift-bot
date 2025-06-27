from typing import Union, Optional
from typing_extensions import TypedDict

from uuid import UUID
from datetime import datetime

from ..core.enums import Criterion

TelegramFileId = Union[str, UUID, None]


class ChampionshipFormData(TypedDict):
    title: str
    description: str
    photo_id: TelegramFileId
    document_id: TelegramFileId
    stages_count: int


class StageFormData(TypedDict):
    championship_id: int
    number: int
    title: str
    description: str
    photo_id: TelegramFileId
    location: str
    map_link: str
    date: datetime


class JudgeFormData(TypedDict):
    stage_id: int
    full_name: str
    photo_id: TelegramFileId
    criterion: Criterion


class FilteredFile(TypedDict):
    skip: bool
    file_id: Optional[TelegramFileId]
