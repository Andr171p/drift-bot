from typing import Optional

from abc import ABC, abstractmethod
from dataclasses import dataclass

from aiogram.types import Message

from .core.domain import User, Referral
from .core.enums import Role
from .core.base import CRUDRepository
from .constants import ADMIN_USERNAMES


@dataclass
class UserCreationContext:
    user_repository: CRUDRepository[User]
    referral_repository: CRUDRepository[Referral]


class UserHandler(ABC):
    def __init__(self, next_handler: Optional["UserHandler"]) -> None:
        self.next_handler = next_handler

    @abstractmethod
    async def create_user(
            self,
            message: Message,
            context: UserCreationContext
    ) -> Optional[User]: pass

    @staticmethod
    async def _get_or_create_user(
            message: Message,
            role: Role,
            context: UserCreationContext
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
            context: UserCreationContext
    ) -> Optional[User]:
        user = await self.create_user(message, context)
        if user:
            return user
        if self.next_handler:
            return self.next_handler.handle(message, context)
        return None


class AdminHandler(UserHandler):
    async def create_user(
            self, message: Message,
            context: UserCreationContext
    ) -> Optional[User]:
        if message.from_user.username not in ADMIN_USERNAMES:
            return None
        return await self._get_or_create_user(message, Role.ADMIN, context)


class RefereeHandler(UserHandler):
    async def create_user(
            self, message: Message,
            context: UserCreationContext
    ) -> Optional[User]:
        url = message.get_url()
        code = self.parse_referral_code(url)
        referral = await context.referral_repository.read(code)
        if not referral:
            return None
        return await self._get_or_create_user(message, Role.REFEREE, context)

    @staticmethod
    def parse_referral_code(url: str) -> str:
        parts = url.split("start=")
        return parts[-1] if len(parts) > 1 else ""


class PilotHandler(UserHandler):
    async def create_user(
            self,
            message: Message,
            context: UserCreationContext
    ) -> Optional[User]:
        return await self._get_or_create_user(message, Role.PILOT, context)


def get_user_chain() -> UserHandler:
    return AdminHandler(RefereeHandler(PilotHandler(None)))
