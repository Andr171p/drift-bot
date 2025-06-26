from aiogram.filters.callback_data import CallbackData

from .enums import (
    Confirmation,
    AdminChampionshipAction,
    AdminStageAction
)

from ..core.enums import Role, Criterion


class StartCallback(CallbackData, prefix="start"):
    role: Role


class AdminCallback(CallbackData, prefix="admin"):
    pass


class ConfirmCallback(CallbackData, prefix="confirm"):
    confirmation: Confirmation


class ConfirmChampionshipCreationCallback(ConfirmCallback, prefix="championship_creation"):
    pass


class ConfirmStageCreationCallback(CallbackData, prefix="stage_creation"):
    pass


class ConfirmJudgeRegistrationCallback(ConfirmCallback, prefix="judge_registration"):
    pass


class AdminChampionshipCallback(AdminCallback, prefix="championship"):
    championship_id: int
    action: AdminChampionshipAction


class AdminStageCallback(AdminCallback, prefix="stage"):
    stage_id: int
    action: AdminStageAction


class JudgeRegistrationCallback(CallbackData, prefix="judge_registration"):
    stage_id: int


class CriterionChoiceCallback(CallbackData, prefix="criterion_choice"):
    criterion: Criterion
