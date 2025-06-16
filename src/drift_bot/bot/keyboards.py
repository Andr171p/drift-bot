from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .callbacks import ConfirmCallback, Confirmation


def confirm_event_creation_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(
            text="Да ✅",
            callback_data=ConfirmCallback(confirmation=Confirmation.YES).pack()
        )],
        [InlineKeyboardButton(
            text="Нет ❌",
            callback_data=ConfirmCallback(confirmation=Confirmation.NO).pack()
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
