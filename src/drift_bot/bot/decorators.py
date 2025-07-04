from typing import Any, Callable, Coroutine, TypeVar, Protocol
from typing_extensions import ParamSpec
from functools import wraps

import logging

from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from dishka import Scope

from pydantic import BaseModel

from .keyboards import judge_registration_kb
from .utils import get_form_fields, draw_progress_bar

from ..ioc import container
from ..utils import parse_referral_code, parse_role_from_code

from ..core.enums import Role
from ..core.domain import User, Judge, Pilot
from ..core.services import ReferralService
from ..core.base import CRUDRepository, ParticipantRepository
from ..core.exceptions import CreationError, UpdateError, CodeExpiredError

WIDTH = 10  # Ширина прогресс бара

P = ParamSpec("P")                                    # Параметры оригинальной функции
R = TypeVar("R")                                      # Возвращаемый тип оригинальной функции
MessageHandler = Callable[P, Coroutine[Any, Any, R]]  # Обработчик сообщения пользователя

ROLE2TYPE: dict[Role, type[BaseModel]] = {
    Role.JUDGE: type[Judge],
    Role.PILOT: type[Pilot]
}

logger = logging.getLogger(__name__)


def role_required(
        *roles: Role,
        error_message: str
) -> Callable[[MessageHandler[P, R]], MessageHandler[P, R] | None]:
    """Декоратор для проверки прав доступа."""
    def decorator(func: MessageHandler[P, R]) -> MessageHandler[P, R | None]:
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs) -> R | None:
            async with container(scope=Scope.REQUEST) as request_container:
                user_repository = await request_container.get(CRUDRepository[User])
                user_id = message.from_user.id
                user = await user_repository.read(user_id)
                if user.role not in roles:
                    logger.warning(f"Access denied for user: {user_id}")
                    await message.answer(error_message)
            return await func(message, *args, **kwargs)
        return wrapper
    return decorator


def save_user(role: Role) -> Callable[[MessageHandler[P, R]], MessageHandler[P, R] | None]:
    """Декоратор для сохранения пользователя после регистрации"""
    def decorator(func: MessageHandler[P, R]) -> MessageHandler[P, R | None]:
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs) -> R | None:
            async with container(scope=Scope.REQUEST) as request_container:
                user_repository = await request_container.get(CRUDRepository[User])
                existed_user = await user_repository.read(message.from_user.id)
                if existed_user:
                    try:
                        await user_repository.update(message.from_user.id, role=role)
                    except UpdateError as e:
                        logger.error(f"Error while user updating: {e}")
                        await message.answer("⚠️ Произошла ошибка, попробуйте позже. Приносим свои извинения.")
                    return await func(message, *args, **kwargs)
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
            return await func(message, *args, **kwargs)
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
        async def wrapper(update: Message | CallbackQuery, state: FSMContext, *args,  **kwargs) -> R | None:
            steps = get_form_fields(form)
            data = await state.get_data()
            completed_steps = sum(1 for step in steps if step in data) + 2
            progress_bar = draw_progress_bar(completed_steps, len(steps), width=width)
            progress_percent = round(completed_steps / len(steps) * 100, 2)
            result = await handler(update, state, *args, **kwargs)
            text = f"{progress_bar} {progress_percent}%"
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
            async with container(scope=Scope.REQUEST) as request_container:
                referral_service = await request_container.get(ReferralService)
                url = message.get_url()
                if not url:
                    return await handler(message, *args, **kwargs)
                code = parse_referral_code(url)
                if not code:
                    return await handler(message, *args, **kwargs)
                try:
                    referral = await referral_service.login(code)
                    role = parse_role_from_code(code)
                    if referral.activated:
                        await message.answer("⚠️ Ваша реферальная ссылка уже использована!")
                        return await handler(message, *args, **kwargs)

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


class ParticipantStageActionCallback(Protocol):
    id: int  # ID этапа


def check_participant_registration(
        role: Role
) -> Callable[[MessageHandler[P, R]], MessageHandler[P, R] | None]:
    """Проверят зарегистрирован ли участник на этап."""
    def decorator(handler: MessageHandler[P, R]) -> MessageHandler[P, R | None]:
        @wraps(handler)
        async def wrapper(
                call: CallbackQuery,
                callback_data: ParticipantStageActionCallback,
                *args, **kwargs
        ) -> R | None:
            participant_type = ROLE2TYPE[role]
            async with container(scope=Scope.REQUEST) as request_container:
                participant_repository = await request_container.get(ParticipantRepository[participant_type])
                participant = await participant_repository.get_by_user_and_stage(
                    user_id=call.from_user.id,
                    stage_id=callback_data.id
                )
                if participant:
                    await call.answer(text="Вы уже зарегистрированы...", show_alert=True)
                    return None
            return handler(call, callback_data, *args, **kwargs)
        return wrapper
    return decorator
