from typing import Optional

from sqlalchemy import insert, select, and_, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ChampionshipOrm, FileMetadataOrm

from src.drift_bot.core.dto import ActiveChampionship
from src.drift_bot.core.domain import Championship, FileMetadata
from src.drift_bot.core.base import ChampionshipRepository
from src.drift_bot.core.exceptions import CreationError, ReadingError, DeletionError

PARENT_TYPE = "championship"


class SQLChampionshipRepository(ChampionshipRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, championship: Championship) -> Championship:
        try:
            championship_orm = ChampionshipOrm(**championship.model_dump(exclude={"id", "files"}))
            self.session.add(championship_orm)
            await self.session.flush()
            if championship.files:
                file_values = [
                    {**file.model_dump(exclude={"id"}),
                     "parent_type": "championship",
                     "parent_id": championship_orm.id}
                    for file in championship.files
                ]
                stmt = insert(FileMetadataOrm).values(file_values)
                await self.session.execute(stmt)
            await self.session.commit()
            await self.session.refresh(championship_orm)
            stmt = (
                select(FileMetadataOrm)
                .where(
                    (FileMetadataOrm.parent_id == championship_orm.id) &
                    (FileMetadataOrm.parent_type == PARENT_TYPE)
                )
            )
            results = await self.session.execute(stmt)
            files = results.scalars().all()
            return Championship(
                id=championship_orm.id,
                title=championship_orm.title,
                description=championship_orm.description,
                files=[FileMetadata.model_validate(file) for file in files],
                is_active=championship_orm.is_active,
                stages_count=championship_orm.stages_count
            )
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(f"Error while creating championship: {e}") from e

    async def read(self, id: int) -> Optional[Championship]:
        try:
            stmt = (
                select(ChampionshipOrm)
                .options(selectinload(ChampionshipOrm.files))
                .where(ChampionshipOrm.id == id)
            )
            result = await self.session.execute(stmt)
            championship = result.scalar_one_or_none()
            return Championship.model_validate(championship) if championship else None
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
            raise DeletionError(f"Error while deleting championship: {e}") from e

    async def get_active(self) -> list[ActiveChampionship]:
        try:
            stmt = (
                select(ChampionshipOrm)
                .where(ChampionshipOrm.is_active is True)
            )
            results = await self.session.execute(stmt)
            active_championships = results.scalars().all()
            return [
                ActiveChampionship.model_validate(active_championship)
                for active_championship in active_championships
            ]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ReadingError(f"Error while reading active championships: {e}") from e
