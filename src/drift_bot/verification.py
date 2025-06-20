from typing import Optional

from abc import ABC, abstractmethod

from aiogram.types import Message

from pydantic import BaseModel

from .core.enums import Role
from .core.domain import User
from .core.base import CRUDRepository
from .core.services import ReferralService
from .core.exceptions import CodeExpiredError
from .constants import ADMIN_USERNAMES
from .utils import parse_referral_code


class UserVerificationContext(BaseModel):
    user_repository: CRUDRepository[User]
    referral_service: ReferralService


class VerifiedUser(BaseModel):
    role: Role
    event_id: Optional[int] = None


class UserVerifierHandler(ABC):
    def __init__(self, next_handler: Optional["UserVerifierHandler"]) -> None:
        self.next_handler = next_handler

    @abstractmethod
    async def verify_user(
            self,
            message: Message,
            context: UserVerificationContext
    ) -> Optional[VerifiedUser]: pass

    @staticmethod
    async def _get_or_create_user(
            message: Message,
            role: Role,
            context: UserVerificationContext
    ) -> Optional[User]:
        existing_user = await context.user_repository.read(message.from_user.id)
        if existing_user:
            return existing_user
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            role=role
        )
        created_user = await context.user_repository.create(user)
        return created_user

    async def handle(
            self,
            message: Message,
            context: UserVerificationContext
    ) -> Optional[VerifiedUser]:
        user = await self.verify_user(message, context)
        if user:
            return user
        if self.next_handler:
            return self.next_handler.handle(message, context)
        return None


class AdminVerifierHandler(UserVerifierHandler):
    async def verify_user(
            self, message: Message,
            context: UserVerificationContext
    ) -> Optional[VerifiedUser]:
        if message.from_user.username not in ADMIN_USERNAMES:
            return None
        user = await self._get_or_create_user(message, Role.ADMIN, context)
        return VerifiedUser(role=user.role)


class JudgeVerifierHandler(UserVerifierHandler):
    async def verify_user(
            self, message: Message,
            context: UserVerificationContext
    ) -> Optional[User]:
        url = message.get_url()
        code = parse_referral_code(url)
        try:
            referral = await context.referral_service.get_referral(code)
            if not referral:
                return None
            user = await self._get_or_create_user(message, Role.JUDGE, context)
            return VerifiedUser(role=user.role, event_id=referral.event_id)
        except CodeExpiredError:
            await message.answer("⛔ Ваша реферальная ссылка истекла, попросите администратора создать новую")
            return None


class PilotVerifierHandler(UserVerifierHandler):
    async def verify_user(
            self,
            message: Message,
            context: UserVerificationContext
    ) -> Optional[User]:
        user = await self._get_or_create_user(message, Role.PILOT, context)
        return VerifiedUser(role=user.role)


def get_user_verification_chain() -> UserVerifierHandler:
    return AdminVerifierHandler(JudgeVerifierHandler(PilotVerifierHandler(None)))
