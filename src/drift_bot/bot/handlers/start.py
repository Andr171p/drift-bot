from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from dishka.integrations.aiogram import FromDishka as Depends

from ...chain import UserCreationContext, get_user_chain
from ...core.domain import User, Referral
from ...core.base import CRUDRepository
from ...templates import (
    START_ADMIN_MESSAGE,
    START_REFEREE_MESSAGE,
    START_PILOT_MESSAGE
)


start_router = Router(name=__name__)


START_MESSAGES = {
    "ADMIN": START_ADMIN_MESSAGE,
    "REFEREE": START_REFEREE_MESSAGE,
    "PILOT": START_PILOT_MESSAGE
}


@start_router.message(Command("start"))
async def start(
        message: Message,
        user_repository: Depends[CRUDRepository[User]],
        referral_repository: Depends[CRUDRepository[Referral]]
) -> None:
    context = UserCreationContext(user_repository, referral_repository)
    chain = get_user_chain()
    user = await chain.handle(message, context)
    text = START_MESSAGES[user.role]
    await message.answer(text)
