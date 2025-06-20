from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from dishka.integrations.aiogram import FromDishka as Depends

from ..states import JudgeForm
from ..enums import Confirmation
from ..keyboards import choose_criterion_kb, confirm_judge_registration_kb
from ..callbacks import (
    JudgeRegistrationCallback,
    CriterionChoiceCallback,
    ConfirmJudgeRegistrationCallback
)

from ...core.domain import Judge, Photo
from ...core.dto import JudgeWithPhoto
from ...core.services import CRUDService
from ...core.base import CRUDRepository, FileStorage
from ...core.exceptions import (
    CreationError,
    UploadingFileError,
    ReadingError,
    DownloadingFileError
)

from ...templates import (
    SUBMIT_JUDGE_REGISTRATION_TEMPLATE,
    JUDGE_COMMANDS_MESSAGE,
    REGISTERED_JUDGE_TEMPLATE
)
from ...constants import JUDGES_BUCKET


judges_router = Router(name=__name__)


@judges_router.callback_query(JudgeRegistrationCallback)
async def send_judge_form(
        call: CallbackQuery,
        callback_data: JudgeRegistrationCallback,
        state: FSMContext
) -> None:
    await state.set_state(JudgeForm.event_id)
    await state.update_data(event_id=callback_data.event_id)
    await state.set_state(JudgeForm.full_name)
    await call.message.answer("Введите своё ФИО: ")


@judges_router.message(JudgeForm.full_name)
async def enter_judge_full_name(message: Message, state: FSMContext) -> None:
    await state.update_data(message.text)
    await state.set_state(JudgeForm.file_id)
    await message.answer("Прикрепите своё фото (или нажмите /skip): ")


@judges_router.message(JudgeForm.file_id, F.photo)
async def attach_judge_photo(message: Message, state: FSMContext) -> None:
    if message.text.lower() != "/skip":
        photo = message.photo[-1]
        await state.update_data(file_id=photo.file_id)
    await state.set_state(JudgeForm.criterion)
    await message.answer(text="Выберите критерий ⬇️:", reply_markup=choose_criterion_kb())


@judges_router.callback_query(CriterionChoiceCallback)
async def choose_judge_criterion(
        call: CallbackQuery,
        callback_data: CriterionChoiceCallback,
        state: FSMContext
) -> None:
    await state.update_data(criterion=callback_data.criterion)
    data = await state.get_data()
    text = SUBMIT_JUDGE_REGISTRATION_TEMPLATE.format(
        full_name=data["full_name"],
        criterion=data["criterion"]
    )
    file_id = data.get("file_id")
    if not file_id:
        await call.message.answer(
            text=text,
            reply_markup=confirm_judge_registration_kb()
        )
    await call.message.answer_photo(
        photo=file_id,
        caption=text,
        reply_markup=confirm_judge_registration_kb()
    )


@judges_router.callback_query(
    ConfirmJudgeRegistrationCallback.filter(F.confirmation == Confirmation.NO)
)
async def cancel_judge_registration(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("❌ Регистрация отменена.")


@judges_router.callback_query(
    ConfirmJudgeRegistrationCallback.filter(F.confirmation == Confirmation.YES)
)
async def register_judge(
        call: CallbackQuery,
        state: FSMContext,
        judge_repository: Depends[CRUDRepository[Judge]],
        file_storage: Depends[FileStorage]
) -> None:
    judge_service = CRUDService[Judge, JudgeWithPhoto](
        crud_repository=judge_repository,
        file_storage=file_storage,
        bucket=JUDGES_BUCKET
    )
    data = await state.get_data()
    judge = Judge(
        event_id=data["event_id"],
        full_name=data["full_name"],
        criterion=data["criterion"]
    )
    file = await call.bot.get_file(file_id=data["file_id"])
    file_data = await call.bot.download(file=file)
    file_format = file.file_path.split(".")[-1].lower()
    photo = Photo(data=file_data.read(), format=file_format)
    try:
        judge_with_photo = await judge_service.create(judge, photo)
        await call.message.answer("✅ Вы успешно зарегистрировались!")
        await call.message.answer(JUDGE_COMMANDS_MESSAGE)
        photo = judge_with_photo.photo
        await call.message.answer_photo(
            photo=BufferedInputFile(file=judge_with_photo.photo.data, filename=photo.file_name),
            caption=REGISTERED_JUDGE_TEMPLATE.format(
                full_name=judge_with_photo.full_name,
                criterion=judge_with_photo.criterion,
                created_at=judge_with_photo.created_at
            ),
        )
    except (CreationError, UploadingFileError):
        await call.message.answer("⚠️ Произошла ошибка при регистрации, попробуйте позже...")


...
