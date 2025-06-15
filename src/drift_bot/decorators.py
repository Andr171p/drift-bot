from functools import wraps

from aiogram.types import Message

from .core.domain import User
from .core.base import CRUDRepository

from .ioc import container


def admin_required(func: ...) -> ...:
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs) -> ...:
        user_repository = await container.get(CRUDRepository[User])
        telegram_id = message.from_user.id
        user = await user_repository.read(telegram_id)
        if user.role == "ADMIN":
            return await message.answer("У вас нет прав администратора")
        return func(message, *args, **kwargs)
    return wrapper
