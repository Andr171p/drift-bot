from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .enums import Confirmation, AdminEventAction
from .callbacks import (
    StartCallback,
    ConfirmCallback,
    AdminEventCallback,
    JudgeRegistrationCallback,
    CriterionChoiceCallback,
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
    builder.button(text="Участник 🏎️", callback_data=StartCallback(role=Role.PILOT).pack())
    builder.button(text="Судья ⚖️", callback_data=StartCallback(role=Role.JUDGE).pack())
    builder.button(text="Администратор 📋👨‍💼", callback_data=StartCallback(role=Role.ADMIN).pack())
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


def admin_event_actions_kb(event_id: int, active: bool) -> InlineKeyboardMarkup:
    """Клавиатура администратора для работы, взаимодействия с событием."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Редактировать ✏️",
        callback_data=AdminEventCallback(event_id=event_id, action=AdminEventAction.EDIT).pack()
    )
    builder.button(
        text="Удалить 🗑️",
        callback_data=AdminEventCallback(event_id=event_id, action=AdminEventAction.DELETE).pack()
    )
    builder.button(
        text="Открыть регистрацию 🚀" if active else "Закрыть регистрацию 🔒",
        callback_data=AdminEventCallback(
            event_id=event_id,
            action=AdminEventAction.TOGGLE_REGISTRATION
        ).pack()
    )
    builder.button(
        text="Пригласить судью 🔗",
        callback_data=AdminEventCallback(
            event_id=event_id,
            action=AdminEventAction.INVITE_REFEREE
        ).pack()
    )
    builder.button(
        text="Судьи ⚖️",
        callback_data=AdminEventCallback(
            event_id=event_id,
            action=AdminEventAction.REFEREES_LIST
        ).pack()
    )
    builder.button(
        text="Пилоты 🏎️",
        callback_data=AdminEventCallback(
            event_id=event_id,
            action=AdminEventAction.PILOTS_LIST
        ).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


def register_judge_kb(event_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для регистрации судьи на этап."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Зарегистрироваться 🔣",
        callback_data=JudgeRegistrationCallback(event_id=event_id).pack()
    )
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
