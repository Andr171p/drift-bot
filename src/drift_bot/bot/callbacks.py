from sys import prefix

from aiogram.filters.callback_data import CallbackData

from .enums import Confirmation, AdminEventAction

from ..core.enums import Role, Criterion


class StartCallback(CallbackData, prefix="start"):
    role: Role


class ConfirmCallback(CallbackData, prefix="confirm"):
    confirmation: Confirmation


class ConfirmEventCreationCallback(ConfirmCallback, prefix="event_creation"):
    pass


class ConfirmJudgeRegistrationCallback(ConfirmCallback, prefix="judge_registration"):
    pass


class AdminEventCallback(CallbackData, prefix="event"):
    event_id: int
    action: AdminEventAction


class JudgeRegistrationCallback(CallbackData, prefix="register_judge"):
    event_id: int


class CriterionChoiceCallback(CallbackData, prefix="criterion_choice"):
    criterion: Criterion
