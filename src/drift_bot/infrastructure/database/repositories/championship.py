from typing import Optional

from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ChampionshipOrm
from ..utils import create_files

from src.drift_bot.core.dto import ActiveChampionship
from src.drift_bot.core.domain import Championship
from src.drift_bot.core.base import ChampionshipRepository
from src.drift_bot.core.exceptions import (
    CreationError,
    ReadingError,
    UpdateError,
    DeletionError
)


class SQLChampionshipRepository(ChampionshipRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, championship: Championship) -> Championship:
        try:
            championship_orm = ChampionshipOrm(
                **championship.model_dump(
                    exclude={"files"},
                    exclude_none=True
                )
            )
            self.session.add(championship_orm)
            await self.session.flush()
            await create_files(
                self.session,
                championship.files,
                parent_id=championship_orm.id,
                parent_type="championship"
            )
            await self.session.commit()
            await self.session.refresh(championship_orm)
            stmt = (
                select(ChampionshipOrm)
                .where(ChampionshipOrm.id == championship_orm.id)
                .options(selectinload(ChampionshipOrm.files))
            )
            result = await self.session.execute(stmt)
            championship_orm = result.scalar_one()
            return Championship.model_validate(championship_orm)
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
            championship_orm = result.scalar_one_or_none()
            return Championship.model_validate(championship_orm) if championship_orm else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ReadingError(f"Error while reading championship: {e}") from e

    async def update(self, id: int, **kwargs) -> Optional[Championship]:
        try:
            stmt = (
                update(ChampionshipOrm)
                .values(**kwargs)
                .where(ChampionshipOrm.id == id)
                .options(selectinload(ChampionshipOrm.files))
                .returning(ChampionshipOrm)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            championship_orm = result.scalar_one_or_none()
            return Championship.model_validate(championship_orm) if championship_orm else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise UpdateError(f"Error while updating championship: {e}") from e

    async def delete(self, id: int) -> bool:
        try:
            stmt = (
                delete(ChampionshipOrm)
                .where(ChampionshipOrm.id == id)
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
