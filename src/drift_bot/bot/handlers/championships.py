from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from dishka.integrations.aiogram import FromDishka as Depends

from ..utils import get_file
from ..states import ChampionshipForm
from ..decorators import role_required
from ..enums import Confirmation, AdminChampionshipAction
from ..keyboards import confirm_kb, admin_championship_actions_kb
from ..callbacks import ConfirmChampionshipCreationCallback, AdminChampionshipCallback

from ...templates import CHAMPIONSHIP_TEMPLATE
from ...constants import CHAMPIONSHIPS_BUCKET

from ...core.enums import Role
from ...core.domain import Championship, File
from ...core.services import CRUDService
from ...core.base import ChampionshipRepository
from ...core.exceptions import CreationError, UploadingFileError, DeletionError, RemovingFileError


championships_router = Router(name=__name__)

ADMIN_REQUIRED_MESSAGE = "⛔ Создавать чемпионаты может только администратор!"


@championships_router.message(Command("/create_championship"))
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def send_championship_form(message: Message, state: FSMContext) -> None:
    await state.set_state(ChampionshipForm.title)
    await message.answer("Укажите название соревнования: ")


@championships_router.message(ChampionshipForm.title)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def enter_championship_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(ChampionshipForm.description)
    await message.answer("Добавьте описание: ")


@championships_router.message(ChampionshipForm.description)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def enter_championship_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(ChampionshipForm.photo_id)
    await message.answer("Прикрепите фото (или нажмите /skip чтобы пропустить): ")


@championships_router.message(ChampionshipForm.photo_id, F.photo)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def attach_championship_photo(message: Message, state: FSMContext) -> None:
    if message.text != "/skip":
        await state.update_data(photo_id=message.photo[-1].file_id)
    await state.set_state(ChampionshipForm.document_id)
    await message.answer("Прикрепите регламент соревнований (или нажмите /skip чтобы пропустить): ")


@championships_router.message(ChampionshipForm.document_id, F.document)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def attach_championship_regulation(message: Message, state: FSMContext) -> None:
    if message.text != "/skip":
        await state.update_data(docuement_id=message.document.file_id)
    await state.set_state(ChampionshipForm.stages_count)
    await message.answer("Укажите количество этапов (напишите только число): ")


@championships_router.message(ChampionshipForm.stages_count)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def indicate_stages_count(message: Message, state: FSMContext) -> None:
    await state.update_data(stages_count=int(message.text))
    data = await state.get_data()
    await message.answer_photo(
        photo=data["photo_id"],
        caption=CHAMPIONSHIP_TEMPLATE.format(
            title=data["title"],
            description=data["description"],
            stages_count=data["stages_count"]
        ),
        reply_markup=confirm_kb(ConfirmChampionshipCreationCallback)
    )


@championships_router.callback_query(
    ConfirmChampionshipCreationCallback.filter(F.confirmation == Confirmation.NO)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def cancel_championship_creation(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("❌ Создание отменено.")


@championships_router.callback_query(
    ConfirmChampionshipCreationCallback.filter(F.confirmation == Confirmation.YES)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def create_championship(
        call: CallbackQuery,
        state: FSMContext,
        championship_service: Depends[CRUDService[Championship]]
) -> None:
    data = await state.get_data()
    photo_id, document_id = data.get("photo_id"), data.get("document_id")
    files: list[File] = []
    for file_id in (photo_id, document_id):
        file = await get_file(file_id, call)
        files.append(file)
    championship = Championship(
        title=data["title"],
        description=data["description"],
        stages_count=data["stages_count"]
    )
    try:
        created_championship = await championship_service.create(
            championship, files, bucket=CHAMPIONSHIPS_BUCKET
        )
        await call.message.answer(
            text="✅ Чемпионат успешно создан...",
            reply_markup=admin_championship_actions_kb(championship_id=created_championship.id)
        )
    except (CreationError, UploadingFileError):
        await call.message.answer("⚠️ Ошибка при создании чемпионата!")


@championships_router.callback_query(
    AdminChampionshipCallback.filter(F.action == AdminChampionshipAction.DELETE)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def delete_championship(
        call: CallbackQuery,
        callback_data: AdminChampionshipCallback,
        championship_service: Depends[CRUDService[Championship]]
) -> None:
    try:
        is_deleted = await championship_service.delete(callback_data.championship_id)
        if is_deleted:
            await call.message.answer("✅ Чемпионат успешно удалён...")
        else:
            await call.message.answer("❌ Чемпионат не был удалён...")
    except (DeletionError, RemovingFileError):
        await call.message.answer("⚠️ Ошибка при удалении чемпионата!")


@championships_router.callback_query(
    AdminChampionshipCallback.filter(F.action == AdminChampionshipAction.TOGGLE_ACTIVATION)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def toggle_championship_activation(
        call: CallbackQuery,
        callback_data: AdminChampionshipCallback,
        championship_repository: Depends[ChampionshipRepository]
) -> None:
    championship_id = callback_data.championship_id
    championship = await championship_repository.read(championship_id)
    is_active = True if not championship.is_active else False
    await championship.update(championship_id, is_active=is_active)
