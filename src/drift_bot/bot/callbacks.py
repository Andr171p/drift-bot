from aiogram.filters.callback_data import CallbackData

from .enums import Confirmation, AdminChampionshipAction

from ..core.enums import Role, Criterion


class StartCallback(CallbackData, prefix="start"):
    role: Role


class ConfirmCallback(CallbackData, prefix="confirm"):
    confirmation: Confirmation


class ConfirmChampionshipCreationCallback(ConfirmCallback, prefix="championship_creation"):
    pass


class ConfirmJudgeRegistrationCallback(ConfirmCallback, prefix="judge_registration"):
    pass


class AdminChampionshipCallback(CallbackData, prefix="championship"):
    championship_id: int
    action: AdminChampionshipAction


class CriterionChoiceCallback(CallbackData, prefix="criterion_choice"):
    criterion: Criterion
