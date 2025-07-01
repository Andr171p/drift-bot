from typing import Union

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from pydantic import PositiveInt

from .enums import (
    Confirmation,
    AdminChampionshipAction,
    AdminStageAction,
    ChampionshipAction,
    JudgeStageAction,
    PilotStageAction
)
from .callbacks import (
    StartCallback,
    CriterionChoiceCallback,
    AdminChampionshipActionCallback,
    AdminStageActionCallback,
    ChampionshipCallback,
    ChampionshipPageCallback,
    ChampionshipActionCallback,
    ConfirmChampionshipCreationCallback,
    ConfirmJudgeRegistrationCallback,
    ConfirmStageDeletionCallback,
    ConfirmStageCreationCallback,
    JudgeStageActionCallback,
    PilotStageActionCallback
)

from ..core.enums import Role
from ..core.domain import Championship
from ..constants import CRITERION2TEXT

ConfirmCallback = Union[
    ConfirmChampionshipCreationCallback,
    ConfirmJudgeRegistrationCallback,
    ConfirmStageCreationCallback,
    ConfirmStageDeletionCallback,
]


def start_keyboard() -> InlineKeyboardMarkup:
    """Стартовая клавиатура для выбора роли."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🏎️ Участник", callback_data=StartCallback(role=Role.PILOT).pack())
    builder.button(text="⚖️ Судья", callback_data=StartCallback(role=Role.JUDGE).pack())
    builder.button(text="📋👨‍💼 Администратор", callback_data=StartCallback(role=Role.ADMIN).pack())
    builder.adjust(1)
    return builder.as_markup()


def confirm_kb(callback: type[ConfirmCallback]) -> InlineKeyboardMarkup:
    """
        Клавиатура для подтверждения создания ресурса.
         - `Да` для создания
         - `нет` для отмены создания
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Да ✅",
        callback_data=callback(confirmation=Confirmation.YES).pack()
    )
    builder.button(
        text="Нет ❌",
        callback_data=callback(confirmation=Confirmation.NO).pack()
    )
    return builder.as_markup()


def admin_championship_actions_kb(championship_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Клавиатура администратора для взаимодействия с чемпионатом."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🗑️ Удалить",
        callback_data=AdminChampionshipActionCallback(
            id=championship_id,
            action=AdminChampionshipAction.DELETE
        ).pack()
    )
    builder.button(
        text="➕ Добавить этап",
        callback_data=AdminChampionshipActionCallback(
            id=championship_id,
            action=AdminChampionshipAction.ADD_STAGE
        ).pack()
    )
    builder.button(
        text="🟢 Сделать активным" if not is_active else "🔴 Закрыть",
        callback_data=AdminChampionshipActionCallback(
            id=championship_id,
            action=AdminChampionshipAction.TOGGLE_ACTIVATION
        ).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_stage_actions_kb(stage_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Клавиатура для взаимодействия с этапом чемпионата."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🗑️ Удалить",
        callback_data=AdminStageActionCallback(
            id=stage_id,
            action=AdminStageAction.DELETE
        ).pack()
    )
    builder.button(
        text="🔓 Открыть регистрацию" if not is_active else "🔐 Закрыть регистрацию",
        callback_data=AdminStageActionCallback(
            id=stage_id,
            action=AdminStageAction.TOGGLE_REGISTRATION
        ).pack()
    )
    builder.button(
        text="📨 Пригласить судью",
        callback_data=AdminStageActionCallback(
            id=stage_id,
            action=AdminStageAction.INVITE_JUDGE
        ).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


def choose_criterion_kb() -> InlineKeyboardMarkup:
    """Клавиатура для выбора судейского критерия."""
    builder = InlineKeyboardBuilder()
    for criterion in CRITERION2TEXT.keys():
        builder.button(
            text=CRITERION2TEXT[criterion],
            callback_data=CriterionChoiceCallback(criterion=criterion).pack()
        )
    return builder.as_markup()


def numeric_kb(numbers: int) -> ReplyKeyboardMarkup:
    """Клавиатура для ввода цифр."""
    builder = ReplyKeyboardBuilder()
    for number in range(1, numbers + 1):
        builder.button(text=str(number))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def judge_registration_kb(stage_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для начала процедуры регистрации судьи на этап."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📝 Зарегистрироваться",
        callback_data=JudgeStageActionCallback(
            id=stage_id,
            action=JudgeStageAction.REGISTRATION
        ).pack()
    )
    return builder.as_markup()


def paginate_championships_kb(
        page: PositiveInt,
        total: PositiveInt,
        championships: list[Championship]
) -> InlineKeyboardMarkup:
    """Клавиатура для пагинации активных чемпионатов."""
    builder = InlineKeyboardBuilder()
    for championship in championships:
        builder.button(
            text=f"{championship.title}",
            callback_data=ChampionshipCallback(id=championship.id).pack()
        )
    buttons: list[InlineKeyboardButton] = []
    if page > 1:
        previous_page = page - 1
        buttons.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=ChampionshipPageCallback(page=previous_page).pack()
        ))
    if page < total:
        next_page = page + 1
        buttons.append(InlineKeyboardButton(
            text="➡️",
            callback_data=ChampionshipPageCallback(page=next_page).pack()
        ))
    builder.row(*buttons)
    builder.adjust(1)
    return builder.as_markup()


def championship_actions_kb(championship_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для взаимодействия с чемпионатом."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📅 Расписание этапов",
        callback_data=ChampionshipActionCallback(
            id=championship_id,
            action=ChampionshipAction.STAGES_SCHEDULE).pack()
    )
    builder.button(
        text="🔜 Ближайший этап",
        callback_data=ChampionshipActionCallback(
            id=championship_id,
            action=ChampionshipAction.NEAREST_STAGE).pack()
    )
    builder.button(
        text="📄 Ознакомится с регламентом",
        callback_data=ChampionshipActionCallback(
            id=championship_id,
            action=ChampionshipAction.READ_REGULATIONS).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


def judge_stage_actions_kb(stage_id: int, is_registered: bool) -> InlineKeyboardMarkup:
    """Клавиатура для взаимодействия судьи с этапом чемпионата."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📝 Зарегистрироваться",
        callback_data=JudgeStageActionCallback(
            id=stage_id,
            action=JudgeStageAction.REGISTRATION
        ).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


def pilot_stage_actions_kb(stage_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для взаимодействия пилота с этапом чемпионата."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📝 Зарегистрироваться",
        callback_data=PilotStageActionCallback(
            id=stage_id,
            action=PilotStageAction.REGISTRATION
        )
    )
    builder.adjust(1)
    return builder.as_markup()
