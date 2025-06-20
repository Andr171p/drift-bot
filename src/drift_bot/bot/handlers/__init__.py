__all__ = (
    "router"
)

from aiogram import Router

from .start import start_router
from .events import events_router
from .judges import judges_router

router = Router()

router.include_routers(
    start_router,
    events_router,
    judges_router
)
