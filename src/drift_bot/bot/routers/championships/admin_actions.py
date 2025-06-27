import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from dishka.integrations.aiogram import FromDishka as Depends

from ...decorators import role_required
from ...enums import AdminChampionshipAction
from ...callbacks import AdminChampionshipActionCallback

from src.drift_bot.core.enums import Role
from src.drift_bot.core.domain import Championship
from src.drift_bot.core.services import CRUDService
from src.drift_bot.core.base import ChampionshipRepository
from src.drift_bot.core.exceptions import DeletionError, RemovingFileError

logger = logging.getLogger(name=__name__)

championship_admin_actions_router = Router(name=__name__)

ADMIN_REQUIRED_MESSAGE = "⛔ Редактировать чемпионат и добавлять этапы может только администратор!"


@championship_admin_actions_router.callback_query(
    AdminChampionshipActionCallback.filter(F.action == AdminChampionshipAction.DELETE)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def delete_championship(
        call: CallbackQuery,
        callback_data: AdminChampionshipActionCallback,
        championship_crud_service: Depends[CRUDService[Championship]]
) -> None:
    try:
        is_deleted = await championship_crud_service.delete(callback_data.id)
        if is_deleted:
            logger.info(f"Championship {callback_data.id} deleted successfully.")
            await call.message.answer("✅ Чемпионат успешно удалён...")
        else:
            await call.message.answer("❌ Чемпионат не был удалён...")
    except (DeletionError, RemovingFileError) as e:
        logger.error(f"Error occurred: {e}")
        await call.message.answer("⚠️ Ошибка при удалении чемпионата!")


@championship_admin_actions_router.callback_query(
    AdminChampionshipActionCallback.filter(F.action == AdminChampionshipAction.TOGGLE_ACTIVATION)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def toggle_championship_activation(
        call: CallbackQuery,
        callback_data: AdminChampionshipActionCallback,
        championship_repository: Depends[ChampionshipRepository]
) -> None:
    championship = await championship_repository.read(callback_data.id)
    is_active = True if not championship.is_active else False
    await championship.update(callback_data.id, is_active=is_active)
    text = "🟢 Чемпионат открыт" if is_active else "🔴 Чемпионат закрыт"
    await call.message.answer(text)
