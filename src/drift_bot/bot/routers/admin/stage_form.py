from typing import Optional

import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from dishka.integrations.aiogram import FromDishka as Depends

from ...utils import get_file
from ...states import StageForm
from ...filters import FileFilter
from ...enums import AdminChampionshipAction, Confirmation
from ...decorators import role_required, show_progress_bar
from ...keyboards import numeric_kb, confirm_kb, admin_stage_actions_kb
from ...callbacks import AdminChampionshipActionCallback, ConfirmStageCreationCallback

from src.drift_bot.core.domain import Stage, File
from src.drift_bot.core.enums import Role, FileType
from src.drift_bot.core.services import CRUDService
from src.drift_bot.core.base import ChampionshipRepository
from src.drift_bot.core.exceptions import CreationError, UploadingFileError

from src.drift_bot.templates import STAGE_TEMPLATE
from src.drift_bot.constants import STAGES_BUCKET

logger = logging.getLogger(name=__name__)

stage_form_router = Router(name=__name__)

ADMIN_REQUIRED_MESSAGE = "⛔ Добавлять этапы может только администратор!"


@stage_form_router.callback_query(
    AdminChampionshipActionCallback.filter(F.action == AdminChampionshipAction.ADD_STAGE)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def send_stage_form(
        call: CallbackQuery,
        callback_data: AdminChampionshipActionCallback,
        state: FSMContext,
        championship_repository: Depends[ChampionshipRepository]
) -> None:
    await state.set_state(StageForm.championship_id)
    await state.update_data(championship_id=callback_data.id)
    championship = await championship_repository.read(callback_data.id)
    await state.set_state(StageForm.number)
    await call.message.answer(
        text="Укажите номер этапа: ",
        reply_markup=numeric_kb(numbers=championship.stages_count)
    )


@stage_form_router.message(StageForm.number, F.text.isdigit())
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(StageForm)
async def indicate_stage_number(message: Message, state: FSMContext) -> None:
    await state.update_data(number=int(message.text))
    await state.set_state(StageForm.title)
    await message.answer(
        text="Введите название этапа: ",
        reply_markup=ReplyKeyboardRemove()
    )


@stage_form_router.message(StageForm.title)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(StageForm)
async def enter_stage_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(StageForm.description)
    await message.answer("Добавьте описание этапа: ")


@stage_form_router.message(StageForm.description)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(StageForm)
async def enter_stage_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(StageForm.photo_id)
    await message.answer("Прикрепите фото (или нажмите /skip чтобы пропустить): ")


@stage_form_router.message(StageForm.photo_id, FileFilter(FileType.PHOTO))
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(StageForm)
async def attach_stage_photo(
        message: Message,
        state: FSMContext,
        file_id: Optional[str] = None,
        skip: bool = False
) -> None:
    if not skip:
        await state.update_data(photo_id=file_id)
    await state.set_state(StageForm.location)
    await message.answer("Укажите место проведения: ")


@stage_form_router.message(StageForm.location)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(StageForm)
async def enter_stage_location(message: Message, state: FSMContext) -> None:
    await state.update_data(location=message.text)
    await state.set_state(StageForm.map_link)
    await message.answer(
        "Добавьте ссылку на карты (Google maps, 2GIS, ...), чтобы зрителям было проще добраться: "
    )


@stage_form_router.message(StageForm.map_link)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(StageForm)
async def enter_stage_map_link(message: Message, state: FSMContext) -> None:
    await state.update_data(map_link=message.text)
    await state.set_state(StageForm.date)
    await message.answer("Укажите дату проведения этапа: ")


@stage_form_router.message(StageForm.date)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(StageForm)
async def enter_stage_date(message: Message, state: FSMContext) -> None:
    date = datetime.now()
    await state.update_data(date=date)
    data = await state.get_data()
    text = STAGE_TEMPLATE.format(
        title=data["title"],
        description=data["description"],
        location=data["location"],
        map_link=data["map_link"],
        date=data["date"]
    )
    photo = data.get("photo_id")
    if photo:
        await message.answer_photo(photo=photo, caption=text)
    else:
        await message.answer(text=text)
    await message.answer(
        text="Подтвердите создание этапа",
        reply_markup=confirm_kb(ConfirmStageCreationCallback)
    )


@stage_form_router.callback_query(
    ConfirmStageCreationCallback.filter(F.confirmation == Confirmation.NO)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def cancel_stage_creation(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("❌ Создание этапа отменено...")


@stage_form_router.callback_query(ConfirmStageCreationCallback.filter(F.confirmation == Confirmation.YES))
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def confirm_stage_creation(
        call: CallbackQuery,
        state: FSMContext,
        stage_crud_service: Depends[CRUDService[Stage]]
) -> None:
    data = await state.get_data()
    await state.clear()
    file: File | None = None
    photo_id = data.get("photo_id")
    if photo_id:
        file = await get_file(file_id=photo_id, call=call)
    stage = Stage(
        championship_id=data["championship_id"],
        number=data["number"],
        title=data["title"],
        description=data["description"],
        location=data["location"],
        map_link=data["map_link"],
        date=data["date"]
    )
    try:
        created_stage = await stage_crud_service.create(stage, files=[file], bucket=STAGES_BUCKET)
        await call.message.answer(
            text="✅ Этап успешно создан...",
            reply_markup=admin_stage_actions_kb(
                id=created_stage.id,
                is_active=created_stage.is_active
            )
        )
    except (CreationError, UploadingFileError) as e:
        logger.error(f"Error occurred: {e}")
        await call.message.answer("⚠️ Ошибка при добавлении этапа!")
