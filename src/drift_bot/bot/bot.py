from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from dishka.integrations.aiogram import setup_dishka

from ..ioc import container


def create_aiogram_bot() -> Dispatcher:
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_routers(router)
    setup_dishka(container=container, router=dispatcher, auto_inject=True)
    return dispatcher
