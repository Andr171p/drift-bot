from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State

from ..core.domain import File


async def get_file(file_id: str, call: CallbackQuery) -> File:
    """
        Получает объект файла из telegram диалога.
        :param file_id - ID файла из диалога.
        :param call - Callback бота.
    """
    file = await call.bot.get_file(file_id=file_id)
    data = await call.bot.download(file)
    file_name = file.file_path
    return File(data=data.read(), file_name=file_name)


def draw_progress_bar(filled: int, total: int, width: int) -> str:
    """Рисует полоску с прогрессом."""
    filled_blocks = round((filled / total) * width)
    empty_blocks = width - filled_blocks
    return "▰" * filled_blocks + "▱" * empty_blocks


def get_form_fields(form: StatesGroup) -> list[str]:
    """Получает поля формы для заполнения."""
    return [attr for attr in dir(form) if isinstance(getattr(form, attr), State)]


async def loading(update: Message | CallbackQuery) -> None:
    ...
