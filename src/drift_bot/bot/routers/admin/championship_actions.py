import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, BufferedInputFile

from dishka.integrations.aiogram import FromDishka as Depends

from ...decorators import role_required
from ...enums import AdminChampionshipAction
from ...callbacks import AdminChampionshipActionCallback
from ...keyboards import admin_championship_actions_kb

from src.drift_bot.core.enums import Role, FileType
from src.drift_bot.core.domain import Championship
from src.drift_bot.core.services import CRUDService
from src.drift_bot.core.base import ChampionshipRepository
from src.drift_bot.core.exceptions import DeletionError, RemovingFileError, UpdateError

from src.drift_bot.templates import CHAMPIONSHIP_TEMPLATE


logger = logging.getLogger(name=__name__)

championship_actions_router = Router(name=__name__)

ADMIN_REQUIRED_MESSAGE = "⛔ Редактировать чемпионат и добавлять этапы может только администратор!"


@championship_actions_router.message(Command("my_championships"))
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def send_my_championships(
        message: Message,
        championship_repository: Depends[ChampionshipRepository],
        championship_crud_service: Depends[CRUDService[Championship]]
) -> None:
    my_championships = await championship_repository.get_by_user_id(message.from_user.id)
    if not my_championships:
        await message.answer("""Вы пока не создали ни один чемпионат, 
            вы можете это сделать с помощью команды /create_championship
        """)
    else:
        for my_championship in my_championships:
            championship, files = await championship_crud_service.read(my_championship.id)
            photo = next((file for file in files if file.type == FileType.PHOTO), None)
            keyboard = admin_championship_actions_kb(
                championship_id=championship.id,
                is_active=championship.is_active
            )
            text = CHAMPIONSHIP_TEMPLATE.format(
                title=championship.title,
                description=championship.description,
                stages_count=championship.stages_count
            )
            if photo:
                await message.answer_photo(
                    photo=BufferedInputFile(file=photo.data, filename=photo.file_name),
                    caption=text,
                    reply_markup=keyboard
                )
            else:
                await message.answer(text=text, reply_markup=keyboard)


@championship_actions_router.callback_query(
    AdminChampionshipActionCallback.filter(F.action == AdminChampionshipAction.DELETE)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def delete_championship(
        call: CallbackQuery,
        callback_data: AdminChampionshipActionCallback,
        championship_crud_service: Depends[CRUDService[Championship]]
) -> None:
    try:
        await call.answer()
        is_deleted = await championship_crud_service.delete(callback_data.id)
        if is_deleted:
            logger.info(f"Championship {callback_data.id} deleted successfully.")
            await call.message.edit_text(text="✅ Чемпионат успешно удалён...")
        else:
            await call.message.answer("❌ Чемпионат не был удалён...")
    except (DeletionError, RemovingFileError) as e:
        logger.error(f"Error occurred: {e}")
        await call.message.answer("⚠️ Ошибка при удалении чемпионата!")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        await call.message.answer("⚠️ Произошла ошибка, приносим свои извинения...")


@championship_actions_router.callback_query(
    AdminChampionshipActionCallback.filter(F.action == AdminChampionshipAction.TOGGLE_ACTIVATION)
)
@role_required(Role.ADMIN, error_message=ADMIN_REQUIRED_MESSAGE)
async def toggle_championship_activation(
        call: CallbackQuery,
        callback_data: AdminChampionshipActionCallback,
        championship_repository: Depends[ChampionshipRepository]
) -> None:
    try:
        await call.answer()
        championship = await championship_repository.read(callback_data.id)
        is_active = not championship.is_active
        updated_championship = await championship_repository.update(callback_data.id, is_active=is_active)
        await call.message.edit_reply_markup(
            reply_markup=admin_championship_actions_kb(
                championship_id=updated_championship.id,
                is_active=updated_championship.is_active
            )
        )
    except UpdateError as e:
        logger.error(f"Error occurred: {e}")
        await call.message.answer("⚠️ Ошибка при обновлении чемпионата!")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        await call.message.answer("⚠️ Произошла ошибка, приносим свои извинения...")
