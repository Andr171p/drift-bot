from typing import Any, Callable, Coroutine, TypeVar
from typing_extensions import ParamSpec
from functools import wraps

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from ..core.domain import File


WIDTH = 10  # Ширина прогресс бара

P = ParamSpec("P")                                    # Параметры оригинальной функции
R = TypeVar("R")                                      # Возвращаемый тип оригинальной функции
MessageHandler = Callable[P, Coroutine[Any, Any, R]]  # Обработчик сообщения пользователя


async def get_file(file_id: str, call: CallbackQuery) -> File:
    file = await call.bot.get_file(file_id=file_id)
    data = await call.bot.download(file)
    file_name = file.file_path
    return File(data=data, file_name=file_name)


def draw_progress_bar(filled: int, total: int, width: int = WIDTH) -> str:
    filled_blocks = round((filled / total) * width)
    empty_blocks = width - filled_blocks
    return "▰" * filled_blocks + "▱" * empty_blocks


def get_form_fields(form: StatesGroup) -> list[str]:
    return [attr for attr in dir(form) if isinstance(getattr(form, attr), State)]


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
