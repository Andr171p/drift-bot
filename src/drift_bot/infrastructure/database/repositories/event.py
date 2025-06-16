from typing import Optional

from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import EventOrm

from src.drift_bot.core.domain import Event
from src.drift_bot.core.dto import CreatedEvent
from src.drift_bot.core.base import EventRepository
from src.drift_bot.core.exceptions import (
    CreationError,
    ReadingError
)


class SQLEventRepository(EventRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, event: Event) -> CreatedEvent:
        try:
            stmt = (
                insert(EventOrm)
                .values(**event.model_dump())
                .returning(EventOrm)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            created_event = result.scalar_one()
            return CreatedEvent.model_validate(created_event)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(f"Error while creating event: {e}") from e

    async def get_last(self) -> Optional[CreatedEvent]:
        try:
            stmt = (
                select(EventOrm)
                .order_by(EventOrm.id.desc())
                .limit(1)
            )
            result = await self.session.execute(stmt)
            event = result.scalar_one_or_none()
            return CreatedEvent.model_validate(event) if event else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ReadingError(f"Error while reading last event: {e}") from e
