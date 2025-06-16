from aiogram.filters.callback_data import CallbackData

from .enums import Confirmation


class ConfirmCallback(CallbackData, prefix="confirm"):
    confirmation: Confirmation
