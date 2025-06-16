from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

start_router = Router(name=__name__)


@start_router.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer(
        text="""
        Бот запущен...
        
        Команды:
         * /start
         * /create-event
       """,
        parse_mode="Markdown"
    )
