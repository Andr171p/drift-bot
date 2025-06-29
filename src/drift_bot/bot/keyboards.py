from typing import Optional, Union

from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from pydantic import PositiveInt

from .enums import (
    Confirmation,
    AdminChampionshipAction,
    AdminStageAction,
    ChampionshipAction,
    CalendarAction
)
from .callbacks import (
    StartCallback,
    CriterionChoiceCallback,
    AdminChampionshipActionCallback,
    AdminStageActionCallback,
    JudgeRegistrationCallback,
    ChampionshipCallback,
    ChampionshipPageCallback,
    ChampionshipActionCallback,
    CalendarActionCallback,
    ConfirmChampionshipCreationCallback,
    ConfirmJudgeRegistrationCallback,
    ConfirmStageDeletionCallback,
    ConfirmStageCreationCallback
)

from ..core.enums import Role
from ..core.domain import Championship
from ..constants import CRITERION2TEXT, MONTH_NAMES, WEEKDAY_NAMES

WEEK_LENGTH = 7  # Длина недели
MONTHS = 12      # Количество месяцев в году

ConfirmCallback = Union[
    ConfirmChampionshipCreationCallback,
    ConfirmJudgeRegistrationCallback,
    ConfirmStageCreationCallback,
    ConfirmStageDeletionCallback,
]


def start_keyboard() -> InlineKeyboardMarkup:
    """Стартовая клавиатура для выбора роли."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🏎️ Участник", callback_data=StartCallback(role=Role.PILOT).pack())
    builder.button(text="⚖️ Судья", callback_data=StartCallback(role=Role.JUDGE).pack())
    builder.button(text="📋👨‍💼 Администратор", callback_data=StartCallback(role=Role.ADMIN).pack())
    builder.adjust(1)
    return builder.as_markup()


def confirm_kb(callback: type[ConfirmCallback]) -> InlineKeyboardMarkup:
    """
        Клавиатура для подтверждения создания ресурса.
         - `Да` для создания
         - `нет` для отмены создания
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Да ✅",
        callback_data=callback(confirmation=Confirmation.YES).pack()
    )
    builder.button(
        text="Нет ❌",
        callback_data=callback(confirmation=Confirmation.NO).pack()
    )
    return builder.as_markup()


def admin_championship_actions_kb(id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Клавиатура администратора для взаимодействия с чемпионатом."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🗑️ Удалить",
        callback_data=AdminChampionshipActionCallback(
            id=id,
            action=AdminChampionshipAction.DELETE
        ).pack()
    )
    builder.button(
        text="➕ Добавить этап",
        callback_data=AdminChampionshipActionCallback(
            id=id,
            action=AdminChampionshipAction.ADD_STAGE
        ).pack()
    )
    builder.button(
        text="🟢 Сделать активным" if not is_active else "🔴 Закрыть",
        callback_data=AdminChampionshipActionCallback(
            id=id,
            action=AdminChampionshipAction.TOGGLE_ACTIVATION
        ).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


def admin_stage_actions_kb(id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Клавиатура для взаимодействия с этапом чемпионата."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🗑️ Удалить",
        callback_data=AdminStageActionCallback(
            id=id,
            action=AdminStageAction.DELETE
        ).pack()
    )
    builder.button(
        text="🔓 Открыть регистрацию" if not is_active else "🔐 Закрыть регистрацию",
        callback_data=AdminStageActionCallback(
            id=id,
            action=AdminStageAction.TOGGLE_REGISTRATION
        ).pack()
    )
    builder.button(
        text="📨 Пригласить судью",
        callback_data=AdminStageActionCallback(
            id=id,
            action=AdminStageAction.INVITE_JUDGE
        ).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


def choose_criterion_kb() -> InlineKeyboardMarkup:
    """Клавиатура для выбора судейского критерия."""
    builder = InlineKeyboardBuilder()
    for criterion in CRITERION2TEXT.keys():
        builder.button(
            text=CRITERION2TEXT[criterion],
            callback_data=CriterionChoiceCallback(criterion=criterion).pack()
        )
    return builder.as_markup()


def numeric_kb(numbers: int) -> ReplyKeyboardMarkup:
    """Клавиатура для ввода цифр."""
    builder = ReplyKeyboardBuilder()
    for number in range(1, numbers + 1):
        builder.button(text=str(number))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def judge_registration_kb(stage_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для начала процедуры регистрации судьи на этап."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📝 Начать регистрацию",
        callback_data=JudgeRegistrationCallback(stage_id=stage_id).pack()
    )
    return builder.as_markup()


def paginate_championships_kb(
        page: PositiveInt,
        total: PositiveInt,
        championships: list[Championship]
) -> InlineKeyboardMarkup:
    """Клавиатура для пагинации активных чемпионатов."""
    builder = InlineKeyboardBuilder()
    for championship in championships:
        builder.button(
            text=f"{championship.title}",
            callback_data=ChampionshipCallback(id=championship.id).pack()
        )
    if page > 1:
        previous_page = page - 1
        builder.button(text="⬅️", callback_data=ChampionshipPageCallback(page=previous_page).pack())
    if page < total:
        next_page = page + 1
        builder.button(text="➡️", callback_data=ChampionshipPageCallback(page=next_page).pack())
    builder.adjust(1)
    return builder.as_markup()


def championship_actions_kb(id: int) -> InlineKeyboardMarkup:
    """Клавиатура для взаимодействия с чемпионатом."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📅 Расписание этапов",
        callback_data=ChampionshipActionCallback(id=id, action=ChampionshipAction.STAGES_SCHEDULE).pack()
    )
    builder.button(
        text="🔜 Ближайший этап",
        callback_data=ChampionshipActionCallback(id=id, action=ChampionshipAction.NEAREST_STAGE).pack()
    )
    builder.button(
        text="📄 Ознакомится с регламентом",
        callback_data=ChampionshipActionCallback(id=id, action=ChampionshipAction.READ_REGULATIONS).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


class CalendarKeyboard:
    def __init__(
            self,
            current_date: Optional[datetime] = None,
            marked_dates: Optional[list[datetime]] = None,
            mark_label: Optional[str] = None,
    ) -> None:
        """
            Инициализация календаря.

            :param current_date: Дата для отображения (по умолчанию текущая)
            :param marked_dates: Список отмеченных дат
            :param mark_label: Метка для выделения отмеченных дат
        """
        self.current_date = current_date or datetime.now()
        self.marked_dates = marked_dates or []
        self.mark_label = mark_label or "✅"

    @property
    def _month_names(self) -> list[str]:
        return MONTH_NAMES

    @property
    def _weekday_names(self) -> list[str]:
        return WEEKDAY_NAMES

    @staticmethod
    def _get_month_days(year: int, month: int) -> list[list[...]]:
        """Создаёт календарную сетку для указанного месяца и года."""
        first_day = datetime(year=year, month=month, day=1)
        last_day = (
            datetime(year=year, month=month + 1, day=1) - timedelta(days=1)
            if month < MONTHS
            else datetime(year=year + 1, month=1, day=1) - timedelta(days=1)
        )
        first_weekday = first_day.weekday()
        # last_weekday = last_day.weekday()

        weeks: list[Optional[int]] = []
        current_week = [None] * first_weekday

        for day in range(1, last_day.day + 1):
            current_week.append(day)
            if len(current_week) == WEEK_LENGTH:
                weeks.append(current_week)
                current_week = []

        if current_week:
            current_week += [None] * (WEEK_LENGTH - len(current_week))
            weeks.append(current_week)
        return weeks

    def _id_date_marked(self, date: datetime) -> bool:
        """Проверяет отмечена ли дата."""
        return any(date.date() == marked_date for marked_date in self.marked_dates)

    def _get_day_button(self, day: Optional[int], month: int, year: int) -> InlineKeyboardButton:
        """
            Создает кнопку дня с соответствующей отметкой.

            :param day: Число дня или None
            :param month: Текущий месяц
            :param year: Текущий год
            :return: Объект InlineKeyboardButton
        """
        if day is None:
            return InlineKeyboardButton(
                text="",
                callback_data=CalendarActionCallback(action=CalendarAction.IGNORE).pack()
            )
        date = datetime(year=year, month=month, day=day)
        is_marked = self._id_date_marked(date)
        label = self.mark_label if is_marked else ""
        return InlineKeyboardButton(
            text=f"{label}{day}{label}",
            callback_data=CalendarActionCallback(
                action=CalendarAction.DAY,
                year=year,
                month=month,
                day=day
            ).pack()
        )

    def __call__(self) -> InlineKeyboardMarkup:
        """Создаёт клавиатуру календаря."""
        builder = InlineKeyboardBuilder()
        year, month = self.current_date.year, self.current_date.month
        # Заголовок с месяцем и годом
        month_name = self._month_names[month - 1]
        builder.row(InlineKeyboardButton(
            text=f"{month_name} {year}",
            callback_data=CalendarActionCallback(action=CalendarAction.IGNORE).pack()
        ))
        # Дни недели
        builder.row(*[
            InlineKeyboardButton(
                text=day,
                callback_data=CalendarActionCallback(action=CalendarAction.IGNORE).pack()
            ) for day in self._weekday_names
        ])
        # Дни месяца
        weeks = self._get_month_days(year, month)
        for week in weeks:
            builder.row(*[self._get_day_button(day, month, year) for day in week])

        # Навигация
        previous_month = month - 1 if month > 1 else MONTHS
        previous_year = year if month > 1 else year - 1
        next_month = month + 1 if month < MONTHS else 1
        next_year = year if month < MONTHS else year + 1

        builder.row(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=CalendarActionCallback(
                    action=CalendarAction.PREVIOUS, year=previous_year, month=previous_month
                ).pack()
            ),
            InlineKeyboardButton(
                text="Сегодня",
                callback_data=CalendarActionCallback(
                    action=CalendarAction.TODAY, year=datetime.now().year, month=datetime.now().month
                ).pack()
            ),
            InlineKeyboardButton(
                text="➡️",
                callback_data=CalendarActionCallback(
                    action=CalendarAction.NEXT, year=next_year, month=next_month
                ).pack()
            )
        )
        return builder.as_markup()
