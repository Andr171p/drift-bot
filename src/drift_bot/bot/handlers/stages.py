from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from dishka.integrations.aiogram import FromDishka as Depends

from ..states import StageForm
from ..keyboards import numeric_kb
from ..enums import AdminChampionshipAction
from ..callbacks import AdminChampionshipCallback
from ..utils import get_file, show_progress_bar

from ...decorators import role_required

from ...core.enums import Role
from ...core.domain import Championship
from ...core.base import CRUDRepository


stages_router = Router(name=__name__)


@stages_router.callback_query(
    AdminChampionshipCallback.filter(F.action == AdminChampionshipAction.ADD_STAGE)
)
@role_required(Role.ADMIN, error_message="🛑 Добавлять этапы может только администратор!")
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
@role_required(Role.ADMIN, error_message="🛑 Добавлять этапы может только администратор!")
@show_progress_bar(StageForm)
async def indicate_stage_number(message: Message, state: FSMContext) -> None:
    await state.update_data(number=int(message.text))
    await state.set_state(StageForm.title)
    await message.answer(
        text="Введите название этапа: ",
        reply_markup=ReplyKeyboardRemove()
    )
