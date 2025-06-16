from typing import Any, Callable, Coroutine, TypeVar
from typing_extensions import ParamSpec
from functools import wraps

from aiogram.types import Message

from .core.domain import User
from .core.base import CRUDRepository
from .constants import Role
from .ioc import container


P = ParamSpec("P")  # Параметры оригинальной функции
R = TypeVar("R")    # Возвращаемый тип оригинальной функции
MessageHandler = Callable[P, Coroutine[Any, Any, R]]


def admin_required(func: MessageHandler[P, R]) -> MessageHandler[P, R | None]:
    """
        Декоратор для проверки прав администратора.
        Если пользователь не админ, возвращает сообщение об ошибке.
    """
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs) -> R | None:
        user_repository = await container.get(CRUDRepository[User])
        telegram_id = message.from_user.id
        user = await user_repository.read(telegram_id)
        if user.role != Role.ADMIN:
            return await message.answer("У вас нет прав администратора")
        return func(message, *args, **kwargs)
    return wrapper
