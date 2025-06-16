from typing import Optional

from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import UserOrm

from src.drift_bot.core.domain import User
from src.drift_bot.core.base import CRUDRepository
from src.drift_bot.core.exceptions import (
    CreationError,
    ReadingError
)


class SQLUserRepository(CRUDRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user: User) -> User:
        try:
            stmt = (
                insert(UserOrm)
                .values(**user.model_dump())
                .returning(UserOrm)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            created_user = result.scalar_one()
            return User.model_validate(created_user)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(f"Error while creating user: {e}")

    async def read(self, telegram_id: int) -> Optional[User]:
        try:
            stmt = (
                select(UserOrm)
                .where(UserOrm.telegram_id == telegram_id)
            )
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            return User.model_validate(user) if user else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ReadingError(f"Error while reading user: {e}")
