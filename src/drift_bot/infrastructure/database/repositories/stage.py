from datetime import datetime
from typing import Optional

from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import StageOrm
from ..utils import create_files

from src.drift_bot.core.domain import Stage
from src.drift_bot.core.base import StageRepository
from src.drift_bot.core.exceptions import (
    CreationError,
    ReadingError,
    UpdateError,
    DeletionError
)


class SQLStageRepository(StageRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, stage: Stage) -> Stage:
        try:
            stage_orm = StageOrm(
                **stage.model_dump(
                    exclude={"files"},
                    exclude_none=True,
                )
            )
            self.session.add(stage_orm)
            await self.session.flush()
            await create_files(
                self.session,
                stage.files,
                parent_id=stage_orm.id,
                parent_type="stage"
            )
            await self.session.commit()
            await self.session.refresh(stage_orm)
            return Stage.model_dump(stage_orm)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(f"Error while creating stage: {e}") from e

    async def read(self, id: int) -> Optional[Stage]:
        try:
            stmt = (
                select(StageOrm)
                .options(selectinload(StageOrm.files))
                .where(StageOrm.id == id)
            )
            result = await self.session.execute(stmt)
            stage_orm = result.scalar_one_or_none()
            return Stage.model_validate(stage_orm) if stage_orm else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ReadingError(f"Error while reading stage: {e}") from e

    async def update(self, id: int, **kwargs) -> Optional[Stage]:
        try:
            stmt = (
                update(StageOrm)
                .values(**kwargs)
                .where(StageOrm.id == id)
                .options(selectinload(StageOrm.files))
                .returning(StageOrm)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            stage_orm = result.scalar_one_or_none()
            return Stage.model_validate(stage_orm) if stage_orm else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise UpdateError(f"Error while updating stage: {e}") from e

    async def delete(self, id: int) -> bool:
        try:
            stmt = (
                delete(StageOrm)
                .where(StageOrm.id == id)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DeletionError(f"Error while deleting stage: {e}") from e

    async def get_nearest(self, date: datetime) -> Optional[Stage]:
        try:
            stmt = (
                select(StageOrm)
                .where(StageOrm.date >= date)
                .order_by(StageOrm.date.asc())
                .limit(1)
            )
            result = await self.session.execute(stmt)
            stage_orm = result.scalar_one_or_none()
            return Stage.model_validate(stage_orm) if stage_orm else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ReadingError(f"Error while reading nearest stage: {e}") from e
