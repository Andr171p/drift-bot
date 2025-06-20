from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup

from dishka.integrations.aiogram import FromDishka as Depends

from ...core.enums import Role
from ...core.domain import User
from ...core.base import CRUDRepository
from ...core.services import ReferralService
from ...verification import UserVerificationContext, get_user_verification_chain
from ...templates import (
    START_ADMIN_MESSAGE,
    START_JUDGE_MESSAGE,
    START_PILOT_MESSAGE
)

from ..keyboards import register_judge_kb


start_router = Router(name=__name__)


START_MESSAGES: dict[Role, str] = {
    Role.ADMIN: START_ADMIN_MESSAGE,
    Role.JUDGE: START_JUDGE_MESSAGE,
    Role.PILOT: START_PILOT_MESSAGE
}

START_KEYBOARDS: dict[Role, InlineKeyboardMarkup] = {
    Role.JUDGE: register_judge_kb
}


@start_router.message(Command("start"))
async def start(
        message: Message,
        user_repository: Depends[CRUDRepository[User]],
        referral_service: Depends[ReferralService]
) -> None:
    context = UserVerificationContext(
        user_repository=user_repository,
        referral_service=referral_service
    )
    chain = get_user_verification_chain()
    verified_user = await chain.handle(message, context)
    await message.answer(
        text=START_MESSAGES[verified_user.role],
        reply_markup=START_KEYBOARDS.get(verified_user.role)
    )
