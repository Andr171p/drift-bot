from typing import Optional

from uuid import uuid4

from .domain import Competition
from .dto import Photo, Document
from .base import CRUDRepository, FileStorage


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
            file_name = self.generate_file_name(photo.format)
            await self._file_storage.upload_file(
                data=photo.data,
                file_name=file_name,
                bucket=...
            )

    @staticmethod
    def generate_file_name(format: str) -> str:
        return f"{uuid4()}.{format}"
