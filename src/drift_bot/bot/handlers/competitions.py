from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from dishka.integrations.aiogram import FromDishka as Depends

from ..enums import Confirmation
from ..states import CompetitionForm
from ..keyboards import confirm_kb
from ..callbacks import ConfirmCompetitionCallback

from ...templates import COMPETITION_TEMPLATE
from ...decorators import role_required
from ...core.enums import Role


competition_router = Router(name=__name__)


@competition_router.message(Command("/create_competition"))
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def send_competition_form(message: Message, state: FSMContext) -> None:
    await state.set_state(CompetitionForm.title)
    await message.answer("Укажите название соревнования: ")


@competition_router.message(CompetitionForm.title)
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def enter_competition_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(CompetitionForm.description)
    await message.answer("Добавьте описание: ")


@competition_router.message(CompetitionForm.description)
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def enter_competition_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(CompetitionForm.photo_id)
    await message.answer("Прикрепите фото (или нажмите /skip чтобы пропустить): ")


@competition_router.message(CompetitionForm.photo_id, F.photo)
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def attach_competition_photo(message: Message, state: FSMContext) -> None:
    if message.text != "/skip":
        await state.update_data(photo_id=message.photo[-1].file_id)
    await state.set_state(CompetitionForm.document_id)
    await message.answer("Прикрепите регламент соревнований (или нажмите /skip чтобы пропустить): ")


@competition_router.message(CompetitionForm.document_id, F.document)
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def attach_competition_regulation(message: Message, state: FSMContext) -> None:
    if message.text != "/skip":
        await state.update_data(docuement_id=message.document.file_id)
    await state.set_state(CompetitionForm.stages_count)
    await message.answer("Укажите количество этапов (напишите только число): ")


@competition_router.message(CompetitionForm.stages_count)
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
        reply_markup=confirm_kb(ConfirmCompetitionCallback)
    )


@competition_router.callback_query(
    ConfirmCompetitionCallback.filter(F.confirmation == Confirmation.NO)
)
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def cancel_competition_creation(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("❌ Создание отменено.")


@competition_router.callback_query(
    ConfirmCompetitionCallback.filter(F.confirmation == Confirmation.YES)
)
@role_required(Role.ADMIN, error_message="🛑 У вас нет доступа к этому функционалу!")
async def create_competition(
        call: CallbackQuery,
        state: FSMContext,
) -> None:
    ...
