__all__ = ("stages_router",)

from aiogram import Router

from .form import stage_form_router
from .menu import stage_menu_router
from .admin_actions import stage_admin_actions_router

stages_router = Router()

stages_router.include_routers(
    stage_form_router,
    stage_menu_router,
    stage_admin_actions_router
)
