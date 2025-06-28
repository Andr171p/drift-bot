from typing import Optional

from aiogram.filters.callback_data import CallbackData

from .enums import (
    Confirmation,
    AdminChampionshipAction,
    AdminStageAction,
    ChampionshipAction,
    CalendarAction
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


class ConfirmStageCreationCallback(ConfirmCallback, prefix="stage_creation"):
    pass


class ConfirmStageDeletionCallback(ConfirmCallback, prefix="stage_deletion"):
    pass


class ConfirmJudgeRegistrationCallback(ConfirmCallback, prefix="judge_registration"):
    pass


class AdminChampionshipActionCallback(AdminCallback, prefix="championship"):
    id: int
    action: AdminChampionshipAction


class AdminStageActionCallback(AdminCallback, prefix="stage"):
    id: int
    action: AdminStageAction


class JudgeRegistrationCallback(CallbackData, prefix="judge_registration"):
    stage_id: int


class CriterionChoiceCallback(CallbackData, prefix="criterion_choice"):
    criterion: Criterion


class PageCallback(CallbackData, prefix="page"):
    page: int


class ChampionshipPageCallback(PageCallback, prefix="championship"):
    pass


class MyChampionshipPageCallback(ChampionshipPageCallback, prefix="admin"):
    pass


class ChampionshipCallback(CallbackData, prefix="championship"):
    id: int


class ChampionshipActionCallback(ChampionshipCallback, prefix="action"):
    action: ChampionshipAction


class CalendarActionCallback(CallbackData, prefix="calendar"):
    action: CalendarAction
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    payload: Optional[list] = None
