from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State

from ..core.domain import File

WIDTH = 10  # Ширина прогресс бара


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
