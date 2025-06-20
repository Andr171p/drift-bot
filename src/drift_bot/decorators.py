from typing import Any, Callable, Coroutine, TypeVar
from typing_extensions import ParamSpec
from functools import wraps

import logging

from aiogram.types import Message

from .core.enums import Role
from .core.domain import User
from .core.base import CRUDRepository
from .core.exceptions import CreationError
from .ioc import container


logger = logging.getLogger(__name__)


P = ParamSpec("P")  # Параметры оригинальной функции
R = TypeVar("R")    # Возвращаемый тип оригинальной функции
MessageHandler = Callable[P, Coroutine[Any, Any, R]]


def role_required(
        role: Role,
        error_message: str
) -> Callable[[MessageHandler[P, R]], MessageHandler[P, R] | None]:
    """Декоратор для проверки прав доступа."""
    def decorator(func: MessageHandler[P, R]) -> MessageHandler[P, R | None]:
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs) -> R | None:
            user_repository = await container.get(CRUDRepository[User])
            user_id = message.from_user.id
            user = await user_repository.read(user_id)
            if user.role != role:
                logger.warning(f"Required role: {role}")
                await message.answer(error_message)
            return func(message, *args, **kwargs)
        return wrapper
    return decorator


def save_user(role: Role) -> Callable[[MessageHandler[P, R]], MessageHandler[P, R] | None]:
    """Декоратор для сохранения пользователя после регистрации"""
    def decorator(func: MessageHandler[P, R]) -> MessageHandler[P, R | None]:
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs) -> R | None:
            user_repository = await container.get(CRUDRepository[User])
            user = User(
                user_id=message.from_user.id,
                username=message.from_user.username,
                role=role
            )
            try:
                _ = await user_repository.create(user)
            except CreationError as e:
                logger.error(f"Error while user saving: {e}")
                await message.answer("⚠️ Произошла ошибка, попробуйте позже. Приносим свои извинения.")
            return func(message, *args, **kwargs)
        return wrapper
    return decorator
