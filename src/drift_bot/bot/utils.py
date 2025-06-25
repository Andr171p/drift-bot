from datetime import datetime

from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State

from aiogram_datepicker import DatepickerSettings

from ..core.domain import File

WIDTH = 10  # Ширина прогресс бара


def get_datepicker_settings() -> DatepickerSettings:
    return DatepickerSettings(
        initial_view="day",
        initial_date=datetime.now().date(),
        views={
            "day": {
                "show_weekdays": True,
                "weekdays_labels": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
                "header": ["prev-year", "days-title", "next-year"],
                "footer": ["prev-month", "select", "next-month"],
            },
            "month": {
                "months_labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                "header": [
                    "prev-year",
                    ["year", "select"],
                    "next-year"
                ],
                "footer": ["select"],
            },
            "year": {
                "header": [],
                "footer": ["prev-years", "next-years"],
            }
        },
        labels={
            "prev-year": "<<",
            "next-year": ">>",
            "prev-years": "<<",
            "next-years": ">>",
            "days-title": "{month} {year}",
            "selected-day": "{day} *",
            "selected-month": "{month} *",
            "present-day": "• {day} •",
            "prev-month": "<",
            "select": "Select",
            "next-month": ">",
            "ignore": ""
        },
        custom_actions=[]
    )


async def get_file(file_id: str, call: CallbackQuery) -> File:
    file = await call.bot.get_file(file_id=file_id)
    data = await call.bot.download(file)
    file_name = file.file_path
    return File(data=data, file_name=file_name)


def draw_progress_bar(filled: int, total: int, width: int = WIDTH) -> str:
    filled_blocks = round((filled / total) * width)
    empty_blocks = width - filled_blocks
    return "▰" * filled_blocks + "▱" * empty_blocks


def get_form_fields(form: StatesGroup) -> list[str]:
    return [attr for attr in dir(form) if isinstance(getattr(form, attr), State)]
