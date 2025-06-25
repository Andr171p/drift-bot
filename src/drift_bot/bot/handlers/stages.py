from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from aiogram_datepicker import Datepicker

from dishka.integrations.aiogram import FromDishka as Depends

from ..states import StageForm
from ..utils import get_file, get_datepicker_settings
from ..decorators import role_required, show_progress_bar
from ..enums import AdminChampionshipAction, Confirmation
from ..keyboards import numeric_kb, confirm_kb, admin_stage_actions_kb
from ..callbacks import AdminChampionshipCallback, ConfirmStageCreationCallback

from ...core.enums import Role
from ...core.base import CRUDRepository
from ...core.services import CRUDService
from ...core.domain import Championship, Stage
from ...core.exceptions import CreationError, UploadingFileError

from ...templates import STAGE_TEMPLATE
from ...constants import STAGES_BUCKET


stages_router = Router(name=__name__)

datepicker = Datepicker(get_datepicker_settings())

ADMIN_REQUIRED_MESSAGE = "⛔ Добавлять этапы может только администратор!"


@stages_router.callback_query(
    AdminChampionshipCallback.filter(F.action == AdminChampionshipAction.ADD_STAGE)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def send_stage_form(
        call: CallbackQuery,
        callback_data: AdminChampionshipCallback,
        state: FSMContext,
        championship_repository: Depends[CRUDRepository[Championship]]
) -> None:
    await state.set_state(StageForm.championship_id)
    championship_id = callback_data.championship_id
    await state.update_data(championship_id=championship_id)
    championship = await championship_repository.read(championship_id)
    await state.set_state(StageForm.number)
    await call.message.answer(
        text="Укажите номер этапа: ",
        reply_markup=numeric_kb(numbers=championship.stages_count)
    )


@stages_router.message(StageForm.number, F.text.isdigit())
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(StageForm)
async def indicate_stage_number(message: Message, state: FSMContext) -> None:
    await state.update_data(number=int(message.text))
    await state.set_state(StageForm.title)
    await message.answer(
        text="Введите название этапа: ",
        reply_markup=ReplyKeyboardRemove()
    )


@stages_router.message(StageForm.title)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(StageForm)
async def enter_stage_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(StageForm.description)
    await message.answer("Добавьте описание этапа: ")


@stages_router.message(StageForm.description)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(StageForm)
async def enter_stage_description(message: Message, state: FSMContext) -> None:
    await state.update_data(desciprion=message.text)
    await state.set_state(StageForm.photo_id)
    await message.answer("Прикрепите фото (или нажмите /skip чтобы пропустить): ")


@stages_router.message(StageForm.photo_id, F.photo)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(StageForm)
async def attach_stage_photo(message: Message, state: FSMContext) -> None:
    if message.text != "/skip":
        await state.update_data(photo_id=message.photo[-1].file_id)
    await state.set_state(StageForm.location)
    await message.answer("Укажите место проведения: ")


@stages_router.message(StageForm.location)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(StageForm)
async def enter_stage_location(message: Message, state: FSMContext) -> None:
    await state.update_data(location=message.text)
    await state.set_state(StageForm.map_link)
    await message.answer(
        "Добавьте ссылку на карты (Google maps, 2GIS, ...), чтобы зрителям было проще добраться: "
    )


@stages_router.message(StageForm.map_link)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(StageForm)
async def enter_stage_map_link(message: Message, state: FSMContext) -> None:
    await state.update_data(map_link=message.text)
    await state.set_state(StageForm.date)
    await message.answer(
        text="Укажите дату проведения этапа: ",
        reply_markup=datepicker.start_calendar()
    )


@stages_router.callback_query(StageForm.date, Datepicker.datepicker_callback.filter())
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(StageForm)
async def enter_stage_date(call: CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    date = await datepicker.process(call, callback_data)
    await state.update_data(date=date)
    data = await state.get_data()
    await call.message.answer(
        text=STAGE_TEMPLATE.format(
            title=data["title"],
            description=data["description"],
            location=data["location"],
            map_link=data["map_link"],
            date=data["date"]
        )
    )
    await call.message.answer(
        text="Подтвердите создание этапа",
        reply_markup=confirm_kb(ConfirmStageCreationCallback)
    )


@stages_router.callback_query(ConfirmStageCreationCallback.filter(F.confirmation == Confirmation.NO))
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def cancel_stage_creation(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("❌ Создание этапа отменено...")


@stages_router.callback_query(ConfirmStageCreationCallback.filter(F.confirmation == Confirmation.YES))
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def create_stage(
        call: CallbackQuery,
        state: FSMContext,
        stage_service: Depends[CRUDService[Stage]]
) -> None:
    data = await state.get_data()
    file = await get_file(file_id=data["photo_id"], call=call)
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
        created_stage = await stage_service.create(stage, files=[file], bucket=STAGES_BUCKET)
        await call.message.answer(
            text="✅ Этап успешно создан...",
            reply_markup=admin_stage_actions_kb(
                stage_id=created_stage.id,
                is_active=created_stage.is_active
            )
        )
    except (CreationError, UploadingFileError):
        await call.message.answer("⚠️ Ошибка при добавлении этапа!")
