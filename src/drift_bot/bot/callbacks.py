
from aiogram.filters.callback_data import CallbackData

from .enums import Confirmation, AdminEventAction


class ConfirmCallback(CallbackData, prefix="confirm"):
    confirmation: Confirmation


class AdminEventCallback(CallbackData, prefix="event"):
    event_id: int
    action: AdminEventAction
