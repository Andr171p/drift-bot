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

    async def handle(
            self,
            message: Message,
            context: UserCreationContext
    ) -> Optional[User]:
        user = await self.create_user(message, context)
        if user:
            return user
        if self.next_handler:
            return self.handle(message, context)
        return None


class AdminHandler(UserHandler):
    async def create_user(
            self, message: Message,
            context: UserCreationContext
    ) -> Optional[User]:
        if message.from_user.username not in ADMIN_USERNAMES:
            return None
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            role=Role.ADMIN
        )
        created_user = await context.user_repository.create(user)
        return created_user


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
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            role=Role.REFEREE
        )
        created_user = await context.user_repository.create(user)
        return created_user

    @staticmethod
    def parse_referral_code(url: str) -> str:
        return url.split("start=")[-1]


class PilotHandler(UserHandler):
    async def create_user(
            self,
            message: Message,
            context: UserCreationContext
    ) -> Optional[User]:
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            role=Role.PILOT
        )
        created_user = await context.user_repository.create(user)
        return created_user


def get_user_chain() -> UserHandler:
    return AdminHandler(RefereeHandler(PilotHandler(None)))
