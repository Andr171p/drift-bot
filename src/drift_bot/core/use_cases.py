from typing import Optional

from uuid import uuid4
from datetime import datetime

from .domain import Championship, File, FileMetadata
from .base import CRUDRepository, FileStorage

from ..constants import CHAMPIONSHIPS_BUCKET


class ChampionshipCreationUseCase:
    def __init__(
            self,
            championship_repository: CRUDRepository[Championship],
            file_storage: FileStorage
    ) -> None:
        self._championship_repository = championship_repository
        self._file_storage = file_storage

    async def execute(
            self,
            championship: Championship,
            files: Optional[list[File]] = None
    ) -> Championship:
        files_metadata: list[FileMetadata] = []
        if files:
            for file in files:
                key = self.generate_key(file.format)
                await self._file_storage.upload_file(data=file.data, key=key, bucket=CHAMPIONSHIPS_BUCKET)
                file_metadata = FileMetadata(
                    key=key,
                    bucket=CHAMPIONSHIPS_BUCKET,
                    size=file.size,
                    format=file.format,
                    type=file.type,
                    uploaded_date=datetime.now()
                )
                files_metadata.append(file_metadata)
        championship.files = files_metadata if files_metadata else championship
        created_championship = await self._championship_repository.create(championship)
        return created_championship

    @staticmethod
    def generate_key(format: str) -> str:
        return f"{uuid4()}.{format}"
