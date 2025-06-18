from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .enums import Confirmation, AdminEventAction
from .callbacks import ConfirmCallback, AdminEventCallback


def confirm_event_creation_kb() -> InlineKeyboardMarkup:
    """
        Клавиатура для подтверждения создания мероприятия.
         - `Да` для создания
         - `нет` для отмены создания
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="Да ✅", callback_data=ConfirmCallback(confirmation=Confirmation.YES).pack())
    builder.button(text="Нет ❌", callback_data=ConfirmCallback(confirmation=Confirmation.NO).pack())
    return builder.as_markup()


def admin_event_actions_kb(event_id: int, active: bool) -> InlineKeyboardMarkup:
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
