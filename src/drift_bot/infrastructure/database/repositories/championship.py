from typing import Optional

from sqlalchemy import insert, select, and_, delete
from sqlalchemy.orm import aliased
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ChampionshipOrm, FileMetadataOrm

from src.drift_bot.core.domain import Championship, FileMetadata
from src.drift_bot.core.base import CRUDRepository
from src.drift_bot.core.exceptions import CreationError, ReadingError, DeletingError


PARENT_TYPE = "championship"


class SQLChampionshipRepository(CRUDRepository[Championship]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, championship: Championship) -> Championship:
        try:
            stmt = (
                insert(ChampionshipOrm)
                .values(**championship.model_dump(exclude={"id", "files"}))
                .returning(ChampionshipOrm)
            )
            result = await self.session.execute(stmt)
            created_championship = result.scalar_one()
            created_files: list[FileMetadataOrm] = []
            if championship.files:
                file_values = [
                    {
                        **file.model_dump(exclude={"id"}),
                        "parent_type": "championship",
                        "parent_id": created_championship.id
                    }
                    for file in championship.files
                ]
                stmt = (
                    insert(FileMetadataOrm)
                    .values(file_values)
                    .returning(FileMetadataOrm)
                )
                results = await self.session.execute(stmt)
                created_files = results.scalars().all()
            await self.session.commit()
            return Championship(
                id=created_championship.id,
                title=created_championship.title,
                description=created_championship.description,
                files=[FileMetadata.model_validate(created_file) for created_file in created_files],
                is_active=created_championship.is_active,
                stages_count=created_championship.stages_count
            )
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(f"Error while creating championship: {e}") from e

    async def read(self, id: int) -> Optional[Championship]:
        try:
            FileMetadataAlias = aliased(FileMetadataOrm)
            stmt = (
                select(ChampionshipOrm, FileMetadataAlias)
                .outerjoin(
                    FileMetadataAlias,
                    and_(
                        FileMetadataAlias.parent_id == ChampionshipOrm.id,
                        FileMetadataAlias.parent_type == PARENT_TYPE
                    )
                )
                .where(ChampionshipOrm.id == id)
                .order_by(ChampionshipOrm.id, FileMetadataAlias.id)
            )
            result = await self.session.execute(stmt)
            rows = result.all()
            championship = rows[0][0]
            files: list[FileMetadataOrm] = []
            seen_files: set[int] = set()
            for row in rows:
                file = row[1]
                if file and file.id not in seen_files:
                    seen_files.add(file.id)
                    files.append(file)
            return Championship(
                id=championship.id,
                title=championship.title,
                description=championship.description,
                files=[FileMetadata.model_validate(file) for file in files],
                is_active=championship.is_active,
                stages_count=championship.stages_count
            )
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ReadingError(f"Error while reading championship: {e}") from e

    async def delete(self, id: int) -> bool:
        try:
            cte = (
                delete(FileMetadataOrm)
                .where(
                    and_(
                        FileMetadataOrm.parent_type == PARENT_TYPE,
                        FileMetadataOrm.parent_id == id
                    )
                )
                .returning(FileMetadataOrm.id)
                .cte("delete_file_metadata")
            )
            stmt = (
                delete(ChampionshipOrm)
                .where(ChampionshipOrm.id == id)
                .where(ChampionshipOrm.id.in_(select(cte.c.parent_id)))
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DeletingError(f"Error while deleting championship: {e}") from e
