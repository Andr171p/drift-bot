import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from dishka.integrations.aiogram import FromDishka as Depends

from ...decorators import role_required
from ...enums import AdminStageAction
from ...callbacks import AdminStageActionCallback

from src.drift_bot.core.enums import Role
from src.drift_bot.core.domain import Stage
from src.drift_bot.core.base import StageRepository
from src.drift_bot.core.services import ReferralService, CRUDService
from src.drift_bot.core.exceptions import CreationError, DeletionError, RemovingFileError

logger = logging.getLogger(name=__name__)

stage_admin_actions_router = Router(name=__name__)

ADMIN_REQUIRED_MESSAGE = "⛔ Управлять этапами может только администратор!"


@stage_admin_actions_router.callback_query(
    AdminStageActionCallback.filter(F.action == AdminStageAction.INVITE_JUDGE)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def invite_judge_to_stage(
        call: CallbackQuery,
        callback_data: AdminStageActionCallback,
        referral_service: Depends[ReferralService]
) -> None:
    try:
        referral = await referral_service.invite(
            stage_id=callback_data.stage_id,
            admin_id=call.message.from_user.id,
            role=Role.JUDGE
        )
        await call.message.answer(f"🔗 Ваша реферальная ссылка: {referral.link}")
    except CreationError as e:
        logger.error(f"Error occurred: {e}")
        await call.message.answer("⚠️ Ошибка при создании ссылки!")


@stage_admin_actions_router.callback_query(
    AdminStageActionCallback.filter(F.action == AdminStageAction.DELETE)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def remove_stage(
        call: CallbackQuery,
        callback_data: AdminStageActionCallback,
        stage_crud_service: Depends[CRUDService[Stage]]
) -> None:
    try:
        is_deleted = await stage_crud_service.delete(callback_data.id)
        if is_deleted:
            await call.message.answer("✅ Этап успешно удалён...")
        else:
            await call.message.answer("❌ Этап не был удалён...")
    except (DeletionError, RemovingFileError) as e:
        logger.error(f"Error occurred: {e}")
        await call.message.answer("⚠️ Ошибка при удалении этапа!")


@stage_admin_actions_router.callback_query(
    AdminStageActionCallback.filter(F.action == AdminStageAction.TOGGLE_REGISTRATION)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def toggle_stage_registration(
        call: CallbackQuery,
        callback_data: AdminStageActionCallback,
        stage_repository: Depends[StageRepository]
) -> None:
    created_stage = await stage_repository.read(callback_data.id)
    is_active = True if not created_stage.is_active else False
    await stage_repository.update(callback_data.id, is_active=is_active)
    text = "🔓 Регистрация открыта" if is_active else "🔐 Регистрация закрыта"
    await call.message.answer(text)
