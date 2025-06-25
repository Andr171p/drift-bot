from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from .enums import Confirmation, AdminChampionshipAction
from .callbacks import (
    StartCallback,
    ConfirmCallback,
    CriterionChoiceCallback,
    AdminChampionshipCallback
)

from ..core.enums import Role, Criterion


CRITERION_TEXTS: dict[Criterion, str] = {
    Criterion.ANGLE: "Угол",
    Criterion.LINE: "Траектория",
    Criterion.STYLE: "Стиль"
}


def start_keyboard() -> InlineKeyboardMarkup:
    """Стартовая клавиатура для выбора роли."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🏎️ Участник", callback_data=StartCallback(role=Role.PILOT).pack())
    builder.button(text="⚖️ Судья", callback_data=StartCallback(role=Role.JUDGE).pack())
    builder.button(text="📋👨‍💼 Администратор", callback_data=StartCallback(role=Role.ADMIN).pack())
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


def admin_championship_actions_kb(championship_id: int) -> InlineKeyboardMarkup:
    """Клавиатура администратора для взаимодействия с чемпионатом."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🗑️ Удалить",
        callback_data=AdminChampionshipCallback(
            championship_id=championship_id,
            action=AdminChampionshipAction.DELETE
        ).pack()
    )
    builder.button(
        text="➕ Добавить этап",
        callback_data=AdminChampionshipCallback(
            championship_id=championship_id,
            action=AdminChampionshipAction.ADD_STAGE
        ).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


def choose_criterion_kb() -> InlineKeyboardMarkup:
    """Клавиатура для выбора судейского критерия."""
    builder = InlineKeyboardBuilder()
    for criterion in CRITERION_TEXTS.keys():
        builder.button(
            text=CRITERION_TEXTS[criterion],
            callback_data=CriterionChoiceCallback(criterion=criterion)
        )
    return builder.as_markup()


def numeric_kb(numbers: int) -> ReplyKeyboardMarkup:
    """Клавиатура для ввода цифр."""
    builder = ReplyKeyboardBuilder()
    for number in range(1, numbers + 1):
        builder.button(text=str(number))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
