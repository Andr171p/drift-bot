from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State

from .keyboards import (
    admin_stage_actions_kb,
    judge_stage_actions_kb,
    pilot_stage_actions_kb,
)

from ..core.domain import File, Stage
from ..core.enums import Role


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


def get_stage_actions_kb_by_role(role: Role, stage: Stage) -> InlineKeyboardMarkup:
    """Получает клавиатуру с набором действия по роли пользователя."""
    params = stage.model_dump()
    keyboard: InlineKeyboardMarkup = None
    match role:
        case role.ADMIN:
            keyboard = admin_stage_actions_kb(**params)
        case role.JUDGE:
            keyboard = judge_stage_actions_kb(**params)
        case role.PILOT:
            keyboard = pilot_stage_actions_kb(**params)
    return keyboard

