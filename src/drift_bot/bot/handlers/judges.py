from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from dishka.integrations.aiogram import FromDishka as Depends

from ..utils import get_file
from ..states import JudgeForm
from ..enums import Confirmation
from ..keyboards import choose_criterion_kb, confirm_kb
from ..decorators import role_required, show_progress_bar
from ..callbacks import (
    JudgeRegistrationCallback,
    CriterionChoiceCallback,
    ConfirmJudgeRegistrationCallback
)

from ...core.enums import Role
from ...core.domain import Judge
from ...core.services import CRUDService
from ...core.exceptions import CreationError, UploadingFileError

from ...templates import JUDGE_TEMPLATE
from ...constants import CRITERION2TEXT, JUDGES_BUCKET

judges_router = Router(name=__name__)

JUDGE_REQUIRED_MESSAGE = "⛔ Этот функционал доступен только для судей!"


@judges_router.callback_query(JudgeRegistrationCallback)
@role_required(Role.JUDGE, error_message=JUDGE_REQUIRED_MESSAGE)
@show_progress_bar(JudgeForm)
async def send_judge_registration_form(
        call: CallbackQuery,
        callback_data: JudgeRegistrationCallback,
        state: FSMContext
) -> None:
    await state.set_state(JudgeForm.stage_id)
    await state.update_data(stage_id=callback_data.stage_id)
    await state.set_state(JudgeForm.full_name)
    await call.message.answer("Введите своё ФИО: ")


@judges_router.message(JudgeForm.full_name)
@role_required(Role.JUDGE, error_message=JUDGE_REQUIRED_MESSAGE)
@show_progress_bar(JudgeForm)
async def enter_judge_full_name(message: Message, state: FSMContext) -> None:
    await state.update_data(full_name=message.text)
    await state.set_state(JudgeForm.photo_id)
    await message.answer("Прикрепите фото (или нажмите /skip чтобы пропустить): ")


@judges_router.message(JudgeForm.photo_id, F.photo)
@role_required(Role.JUDGE, error_message=JUDGE_REQUIRED_MESSAGE)
@show_progress_bar(JudgeForm)
async def attach_judge_photo(message: Message, state: FSMContext) -> None:
    await state.update_data(photo_id=message.photo[-1].file_id)
    await state.set_state(JudgeForm.criterion)
    await message.answer(text="Выберите оцениваемый критерий ⬇️", reply_markup=choose_criterion_kb())


@judges_router.callback_query(CriterionChoiceCallback)
@role_required(Role.JUDGE, error_message=JUDGE_REQUIRED_MESSAGE)
@show_progress_bar(JudgeForm)
async def choose_judge_criterion(
        call: CallbackQuery,
        callback_data: CriterionChoiceCallback,
        state: FSMContext
) -> None:
    await state.update_data(criterion=callback_data.criterion)
    data = await state.get_data()
    await call.message.answer(
        text=JUDGE_TEMPLATE.format(
            full_name=data["full_name"],
            criterion=CRITERION2TEXT[data["criterion"]]
        )
    )
    await call.message.answer(
        text="Подтвердите регистрацию",
        reply_markup=confirm_kb(ConfirmJudgeRegistrationCallback)
    )


@judges_router.callback_query(
    ConfirmJudgeRegistrationCallback.filter(F.confirmation == Confirmation.NO)
)
@role_required(Role.JUDGE, error_message=JUDGE_REQUIRED_MESSAGE)
async def cancel_judge_registration(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("❌ Регистрация отменена.")


@judges_router.callback_query(
    ConfirmJudgeRegistrationCallback.filter(F.confirmation == Confirmation.YES)
)
@role_required(Role.JUDGE, error_message=JUDGE_REQUIRED_MESSAGE)
async def confirm_judge_registration(
        call: CallbackQuery,
        state: FSMContext,
        judge_service: Depends[CRUDService[Judge]]
) -> None:
    data = await state.get_data()
    await state.clear()
    file = await get_file(file_id=data["photo_id"], call=call)
    judge = Judge(
        user_id=call.message.from_user.id,
        stage_id=data["stage_id"],
        full_name=data["full_name"],
        criterion=data["criterion"]
    )
    try:
        _ = await judge_service.create(judge, files=[file], bucket=JUDGES_BUCKET)
        await call.message.answer("✅ Вы успешно зарегистрированы!")
    except (CreationError, UploadingFileError):
        await call.message.answer("⚠️ Ошибка при регистрации!")
