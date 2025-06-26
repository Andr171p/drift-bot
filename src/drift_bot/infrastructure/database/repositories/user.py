from typing import Optional

from sqlalchemy import insert, select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import UserOrm

from src.drift_bot.core.domain import User
from src.drift_bot.core.base import CRUDRepository
from src.drift_bot.core.exceptions import (
    CreationError,
    ReadingError,
    UpdateError,
    DeletionError
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

    async def read(self, user_id: int) -> Optional[User]:
        try:
            stmt = (
                select(UserOrm)
                .where(UserOrm.user_id == user_id)
            )
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            return User.model_validate(user) if user else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ReadingError(f"Error while reading user: {e}")

    async def update(self, user_id: int, **kwargs) -> Optional[User]:
        try:
            stmt = (
                update(UserOrm)
                .values(**kwargs)
                .where(UserOrm.user_id == user_id)
                .returning(UserOrm)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            user = result.scalar_one_or_none()
            return User.model_validate(user) if user else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise UpdateError(f"Error while updating user: {e}") from e

    async def delete(self, user_id: int) -> bool:
        try:
            stmt = (
                delete(UserOrm)
                .where(UserOrm.user_id == user_id)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DeletionError(f"Error while deleting user: {e}") from e
