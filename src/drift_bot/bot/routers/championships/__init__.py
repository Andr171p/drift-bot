__all__ = ("championships_router",)

from aiogram import Router

from .form import championship_form_router
from .menu import championship_menu_router
from .admin_actions import championship_admin_actions_router

championships_router = Router()

championships_router.include_routers(
    championship_form_router,
    championship_menu_router,
    championship_admin_actions_router
)
