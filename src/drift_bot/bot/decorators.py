from typing import Any, Callable, Coroutine, TypeVar
from typing_extensions import ParamSpec
from functools import wraps

import logging

from aiogram import Bot
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .keyboards import judge_registration_kb
from .utils import get_form_fields, draw_progress_bar, WIDTH

from ..ioc import container
from ..utils import parse_referral_code, parse_role_from_code

from ..core.enums import Role
from ..core.domain import User
from ..core.base import CRUDRepository
from ..core.services import ReferralService
from ..core.exceptions import CreationError, CodeExpiredError

P = ParamSpec("P")                                    # Параметры оригинальной функции
R = TypeVar("R")                                      # Возвращаемый тип оригинальной функции
MessageHandler = Callable[P, Coroutine[Any, Any, R]]  # Обработчик сообщения пользователя

logger = logging.getLogger(__name__)


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


def show_progress_bar(
        form: StatesGroup,
        width: int = WIDTH
) -> Callable[[MessageHandler[P, R]], MessageHandler[P, R] | None]:
    """
        Декоратор для отображения прогресс-бара в FSM

        :param form: FSM форма для заполнения данных
        :param width: Ширина прогресс-бара в символах
        """
    def decorator(handler: MessageHandler[P, R]) -> MessageHandler[P, R | None]:
        @wraps(handler)
        async def wrapper(
                update: Message | CallbackQuery,
                state: FSMContext,
                bot: Bot,
                *args,
                **kwargs
        ) -> R | None:
            steps = get_form_fields(form)
            data = await state.get_data()
            completed_steps = sum(1 for step in steps if step in data)
            progress_bar = draw_progress_bar(completed_steps, len(steps), width=width)
            progress_percent = round(completed_steps / len(steps) * 100, 2)
            result = await handler(update, state, bot, *args, **kwargs)
            text = f"""Заполнено:
            {progress_bar} {progress_percent}%
            """
            if isinstance(update, Message):
                await update.answer(text)
            elif isinstance(update, CallbackQuery):
                await update.message.answer(text)
            return result
        return wrapper
    return decorator


def handle_invited_user() -> Callable[[MessageHandler[P, R]], MessageHandler[P, R] | None]:
    """Декоратор для обработки приглашенных пользователей."""
    def decorator(handler: MessageHandler[P, R]) -> MessageHandler[P, R | None]:
        @wraps(handler)
        async def wrapper(message: Message, *args, **kwargs) -> R | None:
            referral_service = await container.get(ReferralService)
            url = message.get_url()
            code = parse_referral_code(url)
            if not code:
                return await handler(message, *args, **kwargs)
            try:
                referral = await referral_service.login(code)
                role = parse_role_from_code(code)

                @save_user(role)
                async def wrapped_handler(msg: Message, *a, **kw) -> R:
                    await msg.answer(
                        text="Вам необходимо пройти регистрацию на этап...",
                        reply_markup=judge_registration_kb(stage_id=referral.stage_id)
                    )
                    return handler(msg, *a, **kw)

                return wrapped_handler(message, *args, **kwargs)
            except CodeExpiredError as e:
                logger.error(f"Error while login user: {e}")
                await message.answer("⚠️ Ваша реферальная ссылка истекла!")
                return None
        return wrapper
    return decorator
