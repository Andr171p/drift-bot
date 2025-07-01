from aiogram.filters.callback_data import CallbackData

from .calendar_kb import CalendarCallback
from .enums import (
    Confirmation,
    AdminChampionshipAction,
    AdminStageAction,
    ChampionshipAction,
    JudgeStageAction,
    PilotStageAction
)

from ..core.enums import Role, Criterion


class StartCallback(CallbackData, prefix="start"):
    """Выбор роли после команды /start"""
    role: Role


class ConfirmChampionshipCreationCallback(CallbackData, prefix="confirm_championship_creation"):
    """Подтвердить создание чемпионата."""
    confirmation: Confirmation


class ConfirmStageCreationCallback(CallbackData, prefix="confirm_stage_creation"):
    """Подтвердить создание этапа."""
    confirmation: Confirmation


class ConfirmStageDeletionCallback(CallbackData, prefix="confirm_stage_deletion"):
    """Подтвердить удаление этапа."""
    confirmation: Confirmation


class ConfirmJudgeRegistrationCallback(CallbackData, prefix="confirm_judge_registration"):
    """Подтвердить регистрацию судьи на этап."""
    confirmation: ConfirmChampionshipCreationCallback


class AdminChampionshipActionCallback(CallbackData, prefix="admin_championship_action"):
    """Действия админа над созданным чемпионатом."""
    id: int
    action: AdminChampionshipAction


class AdminStageActionCallback(CallbackData, prefix="admin_stage_action"):
    """Действия админа над созданным этапом."""
    id: int
    action: AdminStageAction


class CriterionChoiceCallback(CallbackData, prefix="criterion_choice"):
    """Выбор судейского критерия."""
    criterion: Criterion


class ChampionshipCallback(CallbackData, prefix="championship"):
    id: int


class ChampionshipPageCallback(CallbackData, prefix="championship_page"):
    page: int


class ChampionshipActionCallback(CallbackData, prefix="championship_action"):
    id: int
    action: ChampionshipAction


class StageCalendarCallback(CalendarCallback):
    """Расписание этапов чемпионата."""
    championship_id: int


class JudgeStageActionCallback(CallbackData, prefix="judge_stage_action"):
    """Действия судьи для взаимодействия с этапом."""
    id: int
    action: JudgeStageAction


class PilotStageActionCallback(CallbackData, prefix="pilot_stage_action"):
    """Действия пилота для взаимодействия с этапом."""
    id: int
    action: PilotStageAction
