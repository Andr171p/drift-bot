from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode

start_router = Router(name=__name__)


@start_router.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer(
        text="""
        Бот запущен...
        
        Команды:
         * /start
         * /create_event
       """,
        parse_mode=ParseMode.MARKDOWN
    )
