from sqlalchemy.ext.asyncio import AsyncSession

from .models import FileMetadataOrm

from ...core.domain import FileMetadata


async def create_files(
        session: AsyncSession,
        files: list[FileMetadata],
        parent_id: int,
        parent_type: str
) -> None:
    file_orms = [
        FileMetadataOrm(
            **file.model_dump(exclude={"id"}),
            parent_id=parent_id,
            parent_type=parent_type
        )
        for file in files
    ]
    session.add_all(file_orms)
