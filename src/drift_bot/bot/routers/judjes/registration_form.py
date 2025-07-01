from typing import Optional

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from dishka.integrations.aiogram import FromDishka as Depends

from ...utils import get_file
from ...states import JudgeForm
from ...filters import FileFilter
from ...enums import Confirmation, JudgeStageAction
from ...keyboards import choose_criterion_kb, confirm_kb
from ...decorators import role_required, show_progress_bar, check_participant_registration
from ...callbacks import (
    JudgeStageActionCallback,
    CriterionChoiceCallback,
    ConfirmJudgeRegistrationCallback
)

from src.drift_bot.core.enums import Role, FileType
from src.drift_bot.core.domain import Judge
from src.drift_bot.core.services import CRUDService
from src.drift_bot.core.exceptions import CreationError, UploadingFileError

from src.drift_bot.templates import JUDGE_TEMPLATE
from src.drift_bot.constants import CRITERION2TEXT, JUDGES_BUCKET

logger = logging.getLogger(__name__)

registration_form_router = Router(name=__name__)

JUDGE_REQUIRED_MESSAGE = "⛔ Этот функционал доступен только для судей!"


@registration_form_router.callback_query(
    JudgeStageActionCallback.filter(F.action == JudgeStageAction.REGISTRATION)
)
@role_required(Role.JUDGE, error_message=JUDGE_REQUIRED_MESSAGE)
@check_participant_registration(Role.JUDGE)
@show_progress_bar(JudgeForm)
async def send_judge_registration_form(
        call: CallbackQuery,
        callback_data: JudgeStageActionCallback,
        state: FSMContext,
) -> None:
    await state.set_state(JudgeForm.stage_id)
    await state.update_data(stage_id=callback_data.id)
    await state.set_state(JudgeForm.full_name)
    await call.message.answer("Введите своё ФИО: ")


@registration_form_router.message(JudgeForm.full_name)
@role_required(Role.JUDGE, error_message=JUDGE_REQUIRED_MESSAGE)
@show_progress_bar(JudgeForm)
async def enter_judge_full_name(message: Message, state: FSMContext) -> None:
    await state.update_data(full_name=message.text)
    await state.set_state(JudgeForm.photo_id)
    await message.answer("Прикрепите фото (или нажмите /skip чтобы пропустить): ")


@registration_form_router.message(JudgeForm.photo_id, FileFilter(FileType.PHOTO))
@role_required(Role.JUDGE, error_message=JUDGE_REQUIRED_MESSAGE)
@show_progress_bar(JudgeForm)
async def attach_judge_photo(
        message: Message,
        state: FSMContext,
        file_id: Optional[str] = None,
        skip: bool = False
) -> None:
    if not skip:
        await state.update_data(photo_id=file_id)
    await state.set_state(JudgeForm.criterion)
    await message.answer(
        text="Выберите оцениваемый критерий ⬇️",
        reply_markup=choose_criterion_kb()
    )


@registration_form_router.callback_query(CriterionChoiceCallback.filter())
@role_required(Role.JUDGE, error_message=JUDGE_REQUIRED_MESSAGE)
@show_progress_bar(JudgeForm)
async def choose_judge_criterion(
        call: CallbackQuery,
        callback_data: CriterionChoiceCallback,
        state: FSMContext
) -> None:
    await state.update_data(criterion=callback_data.criterion)
    data = await state.get_data()
    photo = data.get("photo_id")
    text = JUDGE_TEMPLATE.format(
        full_name=data["full_name"],
        criterion=CRITERION2TEXT[data["criterion"]]
    )
    if photo:
        await call.message.answer_photo(photo=photo, caption=text)
    else:
        await call.message.answer(text=text)
    await call.message.answer(
        text="Подтвердите регистрацию",
        reply_markup=confirm_kb(ConfirmJudgeRegistrationCallback)
    )


@registration_form_router.callback_query(
    ConfirmJudgeRegistrationCallback.filter(F.confirmation == Confirmation.NO)
)
@role_required(Role.JUDGE, error_message=JUDGE_REQUIRED_MESSAGE)
async def cancel_judge_registration(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("❌ Регистрация отменена.")


@registration_form_router.callback_query(
    ConfirmJudgeRegistrationCallback.filter(F.confirmation == Confirmation.YES)
)
@role_required(Role.JUDGE, error_message=JUDGE_REQUIRED_MESSAGE)
async def confirm_judge_registration(
        call: CallbackQuery,
        state: FSMContext,
        judge_service: Depends[CRUDService[Judge]]
) -> None:
    try:
        data = await state.get_data()
        await state.clear()
        file = await get_file(file_id=data["photo_id"], call=call)
        judge = Judge(
            user_id=call.message.from_user.id,
            stage_id=data["stage_id"],
            full_name=data["full_name"],
            criterion=data["criterion"]
        )
        _ = await judge_service.create(judge, files=[file], bucket=JUDGES_BUCKET)
        await call.message.answer("✅ Вы успешно зарегистрированы!")
    except (CreationError, UploadingFileError) as e:
        logging.error(f"Error while judge registration: {e}")
        await call.message.answer("⚠️ Ошибка при регистрации!")
    except KeyError:
        await call.message.answer("⚠️ Ваша сессия истекла, пройдите регистрацию заново!")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await call.message.answer("⚠️ Произошла ошибка, приносим свои извинения...")
