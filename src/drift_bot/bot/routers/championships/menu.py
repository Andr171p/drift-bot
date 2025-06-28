from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from dishka.integrations.aiogram import FromDishka as Depends

from ...enums import ChampionshipAction, CalendarAction
from ...keyboards import paginate_championships_kb, championship_actions_kb, CalendarKeyboard
from ...callbacks import (
    ChampionshipPageCallback,
    ChampionshipCallback,
    ChampionshipActionCallback,
    CalendarActionCallback
)

from src.drift_bot.core.enums import FileType, Role
from src.drift_bot.core.domain import Championship
from src.drift_bot.core.services import CRUDService
from src.drift_bot.core.base import ChampionshipRepository

from src.drift_bot.templates import CHAMPIONSHIP_TEMPLATE

PAGE, LIMIT = 1, 3
DEFAULT_DAY = 1

championship_menu_router = Router(name=__name__)


@championship_menu_router.message(Command("championships"))
async def send_start_championships_menu(
        message: Message,
        championship_repository: Depends[ChampionshipRepository]
) -> None:
    championships = await championship_repository.paginate(page=PAGE, limit=LIMIT)
    total = await championship_repository.count()
    await message.answer(
        text="Доступные чемпионаты ⬇️",
        reply_markup=paginate_championships_kb(
            page=PAGE,
            total=total,
            championships=championships
        )
    )


@championship_menu_router.callback_query(ChampionshipPageCallback)
async def send_next_championship_menu(
        call: CallbackQuery,
        callback_data: ChampionshipPageCallback,
        championship_repository: Depends[ChampionshipRepository]
) -> None:
    page = callback_data.page
    championships = await championship_repository.paginate(page=page, limit=LIMIT)
    total = await championship_repository.count()
    await call.message.answer(
        text="Доступные чемпионаты ⬇️",
        reply_markup=paginate_championships_kb(
            page=page,
            total=total,
            championships=championships
        )
    )


@championship_menu_router.callback_query(ChampionshipCallback)
async def choose_championship(
        call: CallbackQuery,
        callback_data: ChampionshipCallback,
        championship_crud_service: Depends[CRUDService[Championship]]
) -> None:
    championship, files = await championship_crud_service.read(callback_data.id)
    text = CHAMPIONSHIP_TEMPLATE.format(
        title=championship.title,
        description=championship.description,
        stages_count=championship.stages_count
    )
    keyboard = championship_actions_kb(callback_data.id)
    photo = next((file for file in files if file.type == FileType.PHOTO), None)
    if photo:
        await call.message.answer_photo(
            photo=BufferedInputFile(file=photo.data, filename=photo.file_name),
            caption=text,
            reply_markup=keyboard
        )
    else:
        await call.message.answer(text=text, reply_markup=keyboard)


@championship_menu_router.callback_query(
    ChampionshipActionCallback.filter(F.action == ChampionshipAction.READ_REGULATIONS)
)
async def send_championship_regulations(
        call: CallbackQuery,
        callback_data: ChampionshipActionCallback,
        championship_crud_service: Depends[CRUDService[Championship]]
) -> None:
    _, files = await championship_crud_service.read(callback_data.id)
    document = next((file for file in files if file.type == FileType.DOCUMENT), None)
    if not document:
        await call.message.answer("У этого чемпионата пока нет регламента...")
    else:
        await call.message.answer_document(
            document=BufferedInputFile(file=document.data, filename=document.file_name)
        )


@championship_menu_router.callback_query(
    ChampionshipActionCallback.filter(F.action == ChampionshipAction.STAGES_SCHEDULE)
)
async def send_stages_schedule_of_championship(
        call: CallbackQuery,
        callback_data: ChampionshipActionCallback,
        championship_repository: Depends[ChampionshipRepository]
) -> None:
    stages = await championship_repository.get_stages(callback_data.id)
    dates = [stage.date for stage in stages]
    calendar_kb = CalendarKeyboard(marked_dates=dates, mark_label="🏁")
    await call.message.answer(text="📅 Расписание этапов", reply_markup=calendar_kb())


@championship_menu_router.callback_query(CalendarActionCallback.filter(F.action == CalendarAction.NEXT))
async def send_next_stage_schedule_of_championship(
        call: CallbackQuery,
        callback_date: CalendarActionCallback,
        championship_repository: Depends[ChampionshipRepository]
) -> None:
    date = datetime(year=callback_date.year, month=callback_date.month, day=DEFAULT_DAY)
    calendar_kb = CalendarKeyboard(current_date=date)
