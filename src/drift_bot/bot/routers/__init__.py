__all__ = ("router",)

from aiogram import Router

from .start import start_router
from .admin import admin_router
from .judjes import judges_router
from .championships import championships_router

router = Router()

router.include_routers(
    start_router,
    championships_router,
    admin_router,
    judges_router
)
