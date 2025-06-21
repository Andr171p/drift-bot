from typing import Optional

from uuid import uuid4

from .domain import Competition
from .dto import Photo, Document
from .base import CRUDRepository, FileStorage

from ..constants import COMPETITIONS_BUCKET


class CompetitionCreationUseCase:
    def __init__(
            self,
            competition_repository: CRUDRepository[Competition],
            file_storage: FileStorage
    ) -> None:
        self._competition_repository = competition_repository
        self._file_storage = file_storage

    async def execute(
            self,
            competition: Competition,
            photo: Optional[Photo],
            document: Optional[Document]
    ) -> ...:
        if photo:
            photo_key = self.generate_file_name(photo.format)
            await self._file_storage.upload_file(
                data=photo.data,
                key=photo_key,
                bucket=COMPETITIONS_BUCKET
            )
            competition.photo_key = photo_key
        if document:
            document_key = self.generate_file_name(document.format)
            await self._file_storage.upload_file(
                data=document.data,
                key=document_key,
                bucket=COMPETITIONS_BUCKET
            )
            competition.document_key = document_key
        created_competition = await self._competition_repository.create(competition)
        return ...

    @staticmethod
    def generate_file_name(format: str) -> str:
        return f"{uuid4()}.{format}"
