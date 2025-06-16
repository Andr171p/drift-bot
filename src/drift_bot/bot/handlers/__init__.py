__all__ = (
    "router"
)

from aiogram import Router

from .events import events_router

router = Router()
router.include_routers(
    events_router,
)
