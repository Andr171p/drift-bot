from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from dishka.integrations.aiogram import FromDishka as Depends

from ..utils import get_file
from ..enums import Confirmation
from ..states import ChampionshipForm
from ..keyboards import confirm_kb
from ..callbacks import ConfirmChampionshipCreationCallback

from ...templates import COMPETITION_TEMPLATE
from ...decorators import role_required
from ...core.enums import Role
from ...core.domain import Championship, File
from ...core.use_cases import ChampionshipCreationUseCase


championships_router = Router(name=__name__)


@championships_router.message(Command("/create_championship"))
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def send_championship_form(message: Message, state: FSMContext) -> None:
    await state.set_state(ChampionshipForm.title)
    await message.answer("Укажите название соревнования: ")


@championships_router.message(ChampionshipForm.title)
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def enter_championship_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(ChampionshipForm.description)
    await message.answer("Добавьте описание: ")


@championships_router.message(ChampionshipForm.description)
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def enter_championship_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(ChampionshipForm.photo_id)
    await message.answer("Прикрепите фото (или нажмите /skip чтобы пропустить): ")


@championships_router.message(ChampionshipForm.photo_id, F.photo)
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def attach_championship_photo(message: Message, state: FSMContext) -> None:
    if message.text != "/skip":
        await state.update_data(photo_id=message.photo[-1].file_id)
    await state.set_state(ChampionshipForm.document_id)
    await message.answer("Прикрепите регламент соревнований (или нажмите /skip чтобы пропустить): ")


@championships_router.message(ChampionshipForm.document_id, F.document)
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def attach_championship_regulation(message: Message, state: FSMContext) -> None:
    if message.text != "/skip":
        await state.update_data(docuement_id=message.document.file_id)
    await state.set_state(ChampionshipForm.stages_count)
    await message.answer("Укажите количество этапов (напишите только число): ")


@championships_router.message(ChampionshipForm.stages_count)
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def indicate_stages_count(message: Message, state: FSMContext) -> None:
    await state.update_data(stages_count=int(message.text))
    data = await state.get_data()
    await message.answer_photo(
        photo=data["photo_id"],
        caption=COMPETITION_TEMPLATE.format(
            title=data["title"],
            description=data["description"],
            stages_count=data["stages_count"]
        ),
        reply_markup=confirm_kb(ConfirmChampionshipCreationCallback)
    )


@championships_router.callback_query(
    ConfirmChampionshipCreationCallback.filter(F.confirmation == Confirmation.NO)
)
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def cancel_competition_creation(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("❌ Создание отменено.")


@championships_router.callback_query(
    ConfirmChampionshipCreationCallback.filter(F.confirmation == Confirmation.YES)
)
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def create_competition(
        call: CallbackQuery,
        state: FSMContext,
        championship_creation_use_case: Depends[ChampionshipCreationUseCase]
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
    created_championship = await championship_creation_use_case.execute(championship, files)
