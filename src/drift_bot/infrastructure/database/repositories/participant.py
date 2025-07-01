from typing import TypeVar, Generic, Optional

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ParticipantOrm
from ..utils import create_files

from src.drift_bot.core.base import ParticipantRepository, T
from src.drift_bot.core.exceptions import (
    CreationError,
    ReadingError,
    UpdateError,
    DeletionError
)

P = TypeVar("P", bound=ParticipantOrm)


class SQLParticipantRepository(ParticipantRepository[T], Generic[T, P]):
    def __init__(self, session: AsyncSession, orm: type[P], model: type[T]) -> None:
        self.session = session
        self.orm = orm
        self.model = model

    async def create(self, model: T) -> T:
        try:
            orm = self.orm(**model.model_dump(exclude={"files"}, exclude_none=True))
            self.session.add(orm)
            await self.session.flush()
            if model.files:
                await create_files(
                    self.session, model.files, parent_id=orm.id, parent_type="participant"
                )
            await self.session.commit()
            await self.session.refresh(orm)
            stmt = (
                select(self.orm)
                .where(self.orm.id == orm.id)
                .options(selectinload(self.orm.files))
            )
            result = await self.session.execute(stmt)
            orm = result.scalar_one()
            return self.model.model_validate(orm)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(f"Error while creation participant: {e}") from e

    async def read(self, id: int) -> Optional[T]:
        try:
            stmt = (
                select(self.orm)
                .options(selectinload(self.orm.files))
                .where(self.orm.id == id)
            )
            result = await self.session.execute(stmt)
            orm = result.scalar_one_or_none()
            return self.model.model_validate(orm) if orm else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ReadingError(f"Error while reading participant: {e}") from e

    async def update(self, id: int, **kwargs) -> Optional[T]:
        try:
            ...
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise UpdateError(f"Error while updating participant: {e}") from e

    async def delete(self, id: int) -> bool:
        try:
            stmt = (
                delete(self.orm)
                .options(selectinload(self.orm.files))
                .where(self.orm.id == id)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DeletionError(f"Error while deletion participant: {e}") from e

    async def get_by_user_and_stage(self, user_id: int, stage_id: int) -> Optional[T]:
        try:
            stmt = (
                select(self.orm)
                .options(selectinload(self.orm.files))
                .where(
                    (self.orm.user_id == user_id) &
                    (self.orm.stage_id == stage_id)
                )
            )
            result = await self.session.execute(stmt)
            orm = result.scalar_one_or_none()
            return self.model.model_validate(orm) if orm else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ReadingError(f"Error while reading participant: {e}") from e
