from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from dishka.integrations.aiogram import FromDishka as Depends

from ..core.base import CRUDRepository


router = Router()


@router.message(Command("start"))
async def start(message: Message, command: CommandObject) -> None:
    args = command.args
    print(args)
    await message.answer(args)


@router.message(Command("create-referral-link"))
async def create_referral_link(message: Message, ...)
