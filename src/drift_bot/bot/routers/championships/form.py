import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from dishka.integrations.aiogram import FromDishka as Depends

from ...utils import get_file
from ...enums import Confirmation
from ...filters import FileFilter
from ...types import FilteredFile
from ...states import ChampionshipForm
from ...types import ChampionshipFormData
from ...decorators import role_required, show_progress_bar
from ...callbacks import ConfirmChampionshipCreationCallback
from ...keyboards import confirm_kb, admin_championship_actions_kb

from src.drift_bot.core.domain import Championship
from src.drift_bot.core.services import CRUDService
from src.drift_bot.core.enums import Role, FileType
from src.drift_bot.core.exceptions import CreationError, UploadingFileError

from src.drift_bot.templates import CHAMPIONSHIP_TEMPLATE
from src.drift_bot.constants import CHAMPIONSHIPS_BUCKET

logger = logging.getLogger(__name__)

championship_form_router = Router(name=__name__)

ADMIN_REQUIRED_MESSAGE = "⛔ Создавать чемпионаты может только администратор!"


@championship_form_router.message(Command("create_championship"))
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(ChampionshipForm)
async def send_championship_form(message: Message, state: FSMContext) -> None:
    await state.set_state(ChampionshipForm.title)
    await message.answer("Укажите название соревнования: ")


@championship_form_router.message(ChampionshipForm.title)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(ChampionshipForm)
async def enter_championship_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(ChampionshipForm.description)
    await message.answer("Добавьте описание: ")


@championship_form_router.message(ChampionshipForm.description)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(ChampionshipForm)
async def enter_championship_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(ChampionshipForm.photo_id)
    await message.answer("Прикрепите фото (или нажмите /skip чтобы пропустить): ")


@championship_form_router.message(ChampionshipForm.photo_id, FileFilter(FileType.PHOTO))
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(ChampionshipForm)
async def attach_championship_photo(
        message: Message,
        state: FSMContext,
        filtered_file: FilteredFile
) -> None:
    if not filtered_file["skip"]:
        await state.update_data(photo_id=filtered_file["file_id"])
    await state.set_state(ChampionshipForm.document_id)
    await message.answer("Прикрепите регламент соревнований: ")


@championship_form_router.message(ChampionshipForm.document_id, F.docuemnt)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(ChampionshipForm)
async def attach_championship_regulation(message: Message, state: FSMContext) -> None:
    await state.update_data(docuement_id=message.document.file_id)
    await state.set_state(ChampionshipForm.stages_count)
    await message.answer("Укажите количество этапов (напишите только число): ")


@championship_form_router.message(ChampionshipForm.stages_count)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(ChampionshipForm)
async def indicate_stages_count(message: Message, state: FSMContext) -> None:
    await state.update_data(stages_count=int(message.text))
    data: ChampionshipFormData = await state.get_data()
    await message.answer_photo(
        photo=data["photo_id"],
        caption=CHAMPIONSHIP_TEMPLATE.format(
            title=data["title"],
            description=data["description"],
            stages_count=data["stages_count"]
        ),
        reply_markup=confirm_kb(ConfirmChampionshipCreationCallback)
    )


@championship_form_router.callback_query(
    ConfirmChampionshipCreationCallback.filter(F.confirmation == Confirmation.NO)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def cancel_championship_creation(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("❌ Создание отменено.")


@championship_form_router.callback_query(
    ConfirmChampionshipCreationCallback.filter(F.confirmation == Confirmation.YES)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def confirm_championship_creation(
        call: CallbackQuery,
        state: FSMContext,
        championship_crud_service: Depends[CRUDService[Championship]]
) -> None:
    try:
        data = await state.get_data()
        await state.clear()
        files = [
            await get_file(file_id, call)
            for file_id in (data.get("photo_id"), data.get("document_id"))
            if file_id is not None
        ]
        championship = Championship(
            user_id=call.message.from_user.id,
            title=data["title"],
            description=data["description"],
            stages_count=data["stages_count"]
        )
        created_championship = await championship_crud_service.create(
            championship, files, bucket=CHAMPIONSHIPS_BUCKET
        )
        await call.message.answer(
            text="✅ Чемпионат успешно создан...",
            reply_markup=admin_championship_actions_kb(
                id=created_championship.id,
                is_active=created_championship.is_active
            )
        )
    except (CreationError, UploadingFileError) as e:
        logger.error(f"Error while championship creation: {e}")
        await call.message.answer("⚠️ Ошибка при создании чемпионата!")
    except KeyError:
        await call.message.answer("⚠️ Ваша сессия истекла, создайте чемпионат заново!")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        await call.message.answer("⚠️ Произошла ошибка, приносим свои извинения...")
