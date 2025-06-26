from typing import Optional

from sqlalchemy import insert, select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ReferralOrm

from src.drift_bot.core.domain import Referral
from src.drift_bot.core.base import CRUDRepository
from src.drift_bot.core.exceptions import CreationError, ReadingError, DeletionError


class SQLReferralRepository(CRUDRepository[Referral]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, referral: Referral) -> Referral:
        try:
            stmt = (
                insert(ReferralOrm)
                .values(**referral.model_dump())
                .returning(ReferralOrm)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            referral = result.scalar_one()
            return Referral.model_validate(referral)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise CreationError(f"Error while creating referral: {e}")

    async def read(self, code: str) -> Optional[Referral]:
        try:
            stmt = (
                select(ReferralOrm)
                .where(ReferralOrm.code == code)
            )
            result = await self.session.execute(stmt)
            referral = result.scalar_one_or_none()
            return Referral.model_validate(referral) if referral else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ReadingError(f"Error while reading referral: {e}")

    async def delete(self, code: str) -> bool:
        try:
            stmt = (
                delete(ReferralOrm)
                .where(ReferralOrm.code == code)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DeletionError(f"Error while deleting referral: {e}")
