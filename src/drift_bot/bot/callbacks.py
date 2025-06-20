from aiogram.filters.callback_data import CallbackData

from .enums import Confirmation, AdminEventAction

from ..core.enums import Role, Criterion


class StartCallback(CallbackData, prefix="start"):
    role: Role


class ConfirmCallback(CallbackData, prefix="confirm"):
    confirmation: Confirmation


class ConfirmCompetitionCallback(ConfirmCallback, prefix="competition"):
    pass


class ConfirmJudgeCallback(ConfirmCallback, prefix="judge"):
    pass


class AdminEventCallback(CallbackData, prefix="event"):
    event_id: int
    action: AdminEventAction


class JudgeRegistrationCallback(CallbackData, prefix="register_judge"):
    event_id: int


class CriterionChoiceCallback(CallbackData, prefix="criterion_choice"):
    criterion: Criterion
