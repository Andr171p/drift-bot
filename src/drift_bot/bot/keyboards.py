from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .enums import Confirmation, AdminEventAction
from .callbacks import (
    ConfirmEventCreationCallback,
    ConfirmJudgeRegistrationCallback,
    AdminEventCallback,
    JudgeRegistrationCallback,
    CriterionChoiceCallback,
)

from ..core.enums import Criterion


CRITERION_TEXTS: dict[Criterion, str] = {
    Criterion.ANGLE: "Угол",
    Criterion.LINE: "Траектория",
    Criterion.STYLE: "Стиль"
}


def confirm_event_creation_kb() -> InlineKeyboardMarkup:
    """
        Клавиатура для подтверждения создания мероприятия.
         - `Да` для создания
         - `нет` для отмены создания
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Да ✅",
        callback_data=ConfirmEventCreationCallback(confirmation=Confirmation.YES).pack()
    )
    builder.button(
        text="Нет ❌",
        callback_data=ConfirmEventCreationCallback(confirmation=Confirmation.NO).pack()
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


def confirm_judge_registration_kb() -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения регистрации судьи."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Да ✅",
        callback_data=ConfirmJudgeRegistrationCallback(confirmation=Confirmation.YES).pack()
    )
    builder.button(
        text="Нет ❌",
        callback_data=ConfirmJudgeRegistrationCallback(confirmation=Confirmation.NO).pack()
    )
    return builder.as_markup()
