from typing import Protocol, TypeVar, Optional

from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import FileMetadataOrm

from ...core.domain import FileMetadata


class ModelWithFilesProtocol(Protocol):
    id: int | str | UUID
    files: list[Optional[FileMetadata]]


ModelWithFiles = TypeVar("ModelWithFiles", bound=ModelWithFilesProtocol)


async def create_files(session: AsyncSession, model: ModelWithFiles, parent_type: str) -> None:
    if model.files:
        file_orms = [
            FileMetadataOrm(
                **file.model_dump(exclude={"id"}),
                parent_id=model.id,
                parent_type=parent_type
            )
            for file in model.files
        ]
        session.add_all(file_orms)
