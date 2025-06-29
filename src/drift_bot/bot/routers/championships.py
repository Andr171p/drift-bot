from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from dishka.integrations.aiogram import FromDishka as Depends

from ..enums import ChampionshipAction, CalendarAction
from ..keyboards import (
    paginate_championships_kb,
    championship_actions_kb,
    CalendarKeyboard,
)
from ..callbacks import (
    ChampionshipActionCallback,
    ChampionshipPageCallback,
    CalendarActionCallback,
    ChampionshipCallback
)

from src.drift_bot.core.enums import FileType
from src.drift_bot.core.domain import Championship, Stage
from src.drift_bot.core.services import CRUDService
from src.drift_bot.core.base import ChampionshipRepository, StageRepository

from src.drift_bot.templates import CHAMPIONSHIP_TEMPLATE, STAGE_TEMPLATE
from src.drift_bot.utils import find_target_file

PAGE, LIMIT = 1, 3
DEFAULT_DAY = 1

championships_router = Router(name=__name__)


@championships_router.message(Command("championships"))
async def send_start_championships_menu(
        message: Message,
        championship_repository: Depends[ChampionshipRepository]
) -> None:
    championships = await championship_repository.paginate(page=PAGE, limit=LIMIT)
    total = await championship_repository.count()
    await message.answer(
        text="Доступные чемпионаты 🏆",
        reply_markup=paginate_championships_kb(
            page=PAGE,
            total=total,
            championships=championships
        )
    )


@championships_router.callback_query(ChampionshipPageCallback.filter())
async def send_next_championship_menu(
        call: CallbackQuery,
        callback_data: ChampionshipPageCallback,
        championship_repository: Depends[ChampionshipRepository]
) -> None:
    page = callback_data.page
    championships = await championship_repository.paginate(page=page, limit=LIMIT)
    total = await championship_repository.count()
    await call.message.edit_reply_markup(
        reply_markup=paginate_championships_kb(
            page=page,
            total=total,
            championships=championships
        )
    )


@championships_router.callback_query(ChampionshipCallback.filter())
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
    photo = find_target_file(files, target_type=FileType.PHOTO)
    if photo:
        await call.message.answer_photo(
            photo=BufferedInputFile(file=photo.data, filename=photo.file_name),
            caption=text,
            reply_markup=keyboard
        )
    else:
        await call.message.answer(text=text, reply_markup=keyboard)


@championships_router.callback_query(
    ChampionshipActionCallback.filter(F.action == ChampionshipAction.READ_REGULATIONS)
)
async def send_championship_regulations(
        call: CallbackQuery,
        callback_data: ChampionshipActionCallback,
        championship_crud_service: Depends[CRUDService[Championship]]
) -> None:
    _, files = await championship_crud_service.read(callback_data.id)
    document = find_target_file(files, target_type=FileType.DOCUMENT)
    if not document:
        await call.message.answer("У этого чемпионата пока нет регламента...")
    else:
        await call.message.answer_document(
            document=BufferedInputFile(file=document.data, filename=document.file_name)
        )


@championships_router.callback_query(
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


@championships_router.callback_query(
    CalendarActionCallback.filter(F.action == CalendarAction.NEXT)
)
async def send_next_stage_schedule_of_championship(
        call: CallbackQuery,
        callback_data: CalendarActionCallback,
        championship_repository: Depends[ChampionshipRepository]
) -> None:
    date = datetime(year=callback_data.year, month=callback_data.month, day=DEFAULT_DAY)
    calendar_kb = CalendarKeyboard(current_date=date)


@championships_router.callback_query(
    ChampionshipActionCallback.filter(F.action == ChampionshipAction.NEAREST_STAGE)
)
async def send_nearest_stage_of_championship(
        call: CallbackQuery,
        callback_data: ChampionshipActionCallback,
        stage_repository: Depends[StageRepository],
        stage_crud_service: Depends[CRUDService[Stage]]
) -> None:
    stage = await stage_repository.get_nearest(callback_data.id, date=datetime.now())
    if not stage:
        await call.message.answer("Пока нет ни одного этапа...")
        return
    text = STAGE_TEMPLATE.format(
        title=stage.title,
        description=stage.description,
        location=stage.location,
        map_link=stage.map_link,
        date=stage.date
    )
    _, files = await stage_crud_service.read(stage.id)
    photo = find_target_file(files, target_type=FileType.PHOTO)
    keyboard = ...
    if photo:
        await call.message.answer_photo(
            photo=BufferedInputFile(file=photo.data, filename=photo.file_name),
            caption=text,
            reply_markup=keyboard
        )
    else:
        await call.message.answer(text=text, reply_markup=keyboard)
