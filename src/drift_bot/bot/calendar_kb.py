from typing import Optional

import calendar
from datetime import datetime

from enum import StrEnum

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

WEEK_LENGTH = 7
YEAR_LENGTH = 12
WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
MONTHS = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь"
]


class CalendarAction(StrEnum):
    IGNORE = "ignore"
    SELECT = "select"
    PREVIOUS = "previous"
    NEXT = "next"


class CalendarCallback(CallbackData, prefix="calendar"):
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    is_marked: bool = False
    action: CalendarAction


class CalendarKeyboard:
    def __init__(
            self,
            year: int,
            month: int,
            marked_dates: list[datetime],
            mark_label: str = "",
            callback: type[CalendarCallback] = CalendarCallback,
            **callback_kwargs
    ) -> None:
        """
            Инициализация календаря.

            :param year: Год для отображения
            :param month: Месяц для отображения (1-12)
            :param marked_dates: Список дат для отметки
            :param mark_label: Префикс для отмеченных дат
            :param callback: Кастомный класс наследуемый от CalendarCallback
            :param **callback_kwargs: Дополнительные данные передаваемые в кастомный класс
        """
        self._year = year
        self._month = month
        self._marked_dates = marked_dates
        self._mark_label = mark_label
        self._month_days = calendar.monthcalendar(year, month)
        self._marked_days = self._mark_days()
        self._callback = callback
        self._callback_kwargs = callback_kwargs

    def _mark_days(self) -> set[int]:
        """Возвращает множество отмеченных дней для текущего месяца."""
        return {
            date.day for date in self._marked_dates
            if date.year == self._year and date.month == self._month
        }

    def _get_navigation_months(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """Вычисляет предыдущий и следующий месяцы для навигации."""
        prev_month = self._month - 1 if self._month > 1 else YEAR_LENGTH
        prev_year = self._year if self._month > 1 else self._year - 1

        next_month = self._month + 1 if self._month < YEAR_LENGTH else 1
        next_year = self._year if self._month < YEAR_LENGTH else self._year + 1

        return (prev_year, prev_month), (next_year, next_month)

    def _build_day_button(self, day: int) -> InlineKeyboardButton:
        """Создает кнопку для дня календаря."""
        if day == 0:
            return InlineKeyboardButton(
                text=" ",
                callback_data=self._callback(action=CalendarAction.IGNORE, **self._callback_kwargs).pack()
            )
        is_marked = day in self._marked_days
        text = f"{self._mark_label}{day}" if is_marked else str(day)
        return InlineKeyboardButton(
            text=text,
            callback_data=self._callback(
                year=self._year,
                month=self._month,
                day=day,
                is_marked=is_marked,
                action=CalendarAction.SELECT,
                **self._callback_kwargs
            ).pack()
        )

    @staticmethod
    def _build_weekdays_row(builder: InlineKeyboardBuilder) -> None:
        """Добавляет строку с днями недели."""
        builder.row(*[
            InlineKeyboardButton(
                text=day,
                callback_data=CalendarCallback(action=CalendarAction.IGNORE).pack()
            )
            for day in WEEKDAYS
        ])

    def _build_days_grid(self, builder: InlineKeyboardBuilder) -> None:
        """Добавляет сетку дней месяца."""
        for week in self._month_days:
            builder.row(*[self._build_day_button(day) for day in week])

    def _build_navigation_row(self, builder: InlineKeyboardBuilder) -> None:
        """Добавляет строку навигации."""
        (prev_year, prev_month), (next_year, next_month) = self._get_navigation_months()

        builder.row(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=self._callback(
                    year=prev_year,
                    month=prev_month,
                    action=CalendarAction.PREVIOUS,
                    **self._callback_kwargs
                ).pack()
            ),
            InlineKeyboardButton(
                text=f"{MONTHS[self._month - 1]} {self._year}",
                callback_data=CalendarCallback(action=CalendarAction.IGNORE).pack()
            ),
            InlineKeyboardButton(
                text="➡️",
                callback_data=self._callback(
                    year=next_year,
                    month=next_month,
                    action=CalendarAction.NEXT,
                    **self._callback_kwargs
                ).pack()
            )
        )

    def __call__(self) -> InlineKeyboardMarkup:
        """Строит и возвращает клавиатуру календаря."""
        builder = InlineKeyboardBuilder()

        self._build_weekdays_row(builder)
        self._build_days_grid(builder)
        self._build_navigation_row(builder)

        return builder.as_markup()
