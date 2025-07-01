import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ...states import PilotForm
from ...enums import PilotStageAction
from ...callbacks import PilotStageActionCallback
from ...decorators import role_required, show_progress_bar, check_participant_registration

from src.drift_bot.core.enums import Role
from src.drift_bot.core.base import ParticipantRepository

logger = logging.getLogger(name=__name__)

registration_form_router = Router(name=__name__)

PILOT_REQUIRED_MESSAGE = "⛔ Этот функционал доступен только для пилотов!"


@registration_form_router.callback_query(
    PilotStageActionCallback.filter(F.action == PilotStageAction.REGISTRATION)
)
@role_required(Role.PILOT, error_message=PILOT_REQUIRED_MESSAGE)
@check_participant_registration(Role.PILOT)
async def send_pilot_registration_form(call: CallbackQuery, state: FSMContext) -> ...:
    ...
