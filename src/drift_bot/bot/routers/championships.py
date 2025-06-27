import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from dishka.integrations.aiogram import FromDishka as Depends

from ..utils import get_file
from ..states import ChampionshipForm
from ..types import ChampionshipFormData
from ..decorators import role_required, show_progress_bar
from ..enums import Confirmation, AdminChampionshipAction
from ..keyboards import confirm_kb, admin_championship_actions_kb, paginate_championships_kb
from ..callbacks import (
    ConfirmChampionshipCreationCallback,
    AdminChampionshipCallback,
    ChampionshipCallback,
    ChampionshipPageCallback
)

from ...templates import CHAMPIONSHIP_TEMPLATE
from ...constants import CHAMPIONSHIPS_BUCKET

from ...core.enums import Role
from ...core.domain import Championship, File, User
from ...core.services import CRUDService
from ...core.base import CRUDRepository, ChampionshipRepository
from ...core.exceptions import CreationError, UploadingFileError, DeletionError, RemovingFileError

logger = logging.getLogger(__name__)

championships_router = Router(name=__name__)

ADMIN_REQUIRED_MESSAGE = "⛔ Создавать чемпионаты может только администратор!"


@championships_router.message(Command("create_championship"))
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(ChampionshipForm)
async def send_championship_form(message: Message, state: FSMContext) -> None:
    await state.set_state(ChampionshipForm.title)
    await message.answer("Укажите название соревнования: ")


@championships_router.message(ChampionshipForm.title)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(ChampionshipForm)
async def enter_championship_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(ChampionshipForm.description)
    await message.answer("Добавьте описание: ")


@championships_router.message(ChampionshipForm.description)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(ChampionshipForm)
async def enter_championship_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(ChampionshipForm.photo_id)
    await message.answer("Прикрепите фото (или нажмите /skip чтобы пропустить): ")


@championships_router.message(ChampionshipForm.photo_id, F.photo)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(ChampionshipForm)
async def attach_championship_photo(message: Message, state: FSMContext) -> None:
    if message.text != "/skip":
        await state.update_data(photo_id=message.photo[-1].file_id)
    await state.set_state(ChampionshipForm.document_id)
    await message.answer("Прикрепите регламент соревнований (или нажмите /skip чтобы пропустить): ")


@championships_router.message(ChampionshipForm.document_id, F.document)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
@show_progress_bar(ChampionshipForm)
async def attach_championship_regulation(message: Message, state: FSMContext) -> None:
    if message.text != "/skip":
        await state.update_data(docuement_id=message.document.file_id)
    await state.set_state(ChampionshipForm.stages_count)
    await message.answer("Укажите количество этапов (напишите только число): ")


@championships_router.message(ChampionshipForm.stages_count)
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
        championship_crud_service: Depends[CRUDService[Championship]]
) -> None:
    try:
        data = await state.get_data()
        await state.clear()
        photo_id, document_id = data.get("photo_id"), data.get("document_id")
        files: list[File] = []
        for file_id in (photo_id, document_id):
            if file_id is not None:
                file = await get_file(file_id, call)
                files.append(file)
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
    text = "🟢 Чемпионат открыт" if is_active else "🔴 Чемпионат закрыт"
    await call.message.answer(text)


@championships_router.message(Command("championships"))
async def send_start_championships_menu(
        message: Message,
        championship_repository: Depends[ChampionshipRepository]
) -> None:
    PAGE, LIMIT = 1, 3
    championships = await championship_repository.paginate(page=PAGE, limit=LIMIT)
    total = await championship_repository.count()
    await message.answer(
        text="Активные чемпионаты ⬇️",
        reply_markup=paginate_championships_kb(
            page=PAGE,
            total=total,
            championships=championships
        )
    )


@championships_router.callback_query(ChampionshipPageCallback)
async def send_next_championship_menu(
        call: CallbackQuery,
        callback_data: ChampionshipPageCallback,
        championship_repository: Depends[ChampionshipRepository]
) -> None:
    LIMIT = 3
    page = callback_data.page
    championships = await championship_repository.paginate(page=page, limit=LIMIT)
    total = await championship_repository.count()
    await call.message.answer(
        text="Активные чемпионаты ⬇️",
        reply_markup=paginate_championships_kb(
            page=page,
            total=total,
            championships=championships
        )
    )


@championships_router.callback_query(ChampionshipCallback)
async def send_championship(
        call: CallbackQuery,
        callback_data: ChampionshipCallback,
        user_repository: Depends[CRUDRepository[User]],
        championship_crud_service: Depends[CRUDService[Championship]]
) -> None:
    user = await user_repository.read(call.message.from_user.id)
    championship, files = await championship_crud_service.read(callback_data.id)
    text = CHAMPIONSHIP_TEMPLATE.format(
        title=championship.title,
        description=championship.description,
        stages_count=championship.stages_count
    )
    keyboard = ...
    if files is not None:
        ...
