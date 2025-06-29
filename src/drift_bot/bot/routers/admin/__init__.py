__all__ = ("admin_router",)

from aiogram import Router

from .stage_form import stage_form_router
from .stage_actions import stage_actions_router
from .championship_form import championship_form_router
from .championship_actions import championship_actions_router

admin_router = Router()

admin_router.include_routers(
    stage_form_router,
    stage_actions_router,
    championship_form_router,
    championship_actions_router,
)
