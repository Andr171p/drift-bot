from aiogram.filters.callback_data import CallbackData

from .constants import Confirmation


class ConfirmCallback(CallbackData, prefix="confirm"):
    confirmation: Confirmation
