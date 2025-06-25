__all__ = (
    "router"
)

from aiogram import Router

from .start import start_router
from .judges import judges_router
from .championships import championships_router

router = Router()

router.include_routers(
    start_router,
    judges_router,
    championships_router
)
