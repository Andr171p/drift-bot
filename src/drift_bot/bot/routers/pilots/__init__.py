__all__ = ("pilots_router",)

from aiogram import Router

from .registration_form import registration_form_router

pilots_router = Router()

pilots_router.include_routers(
    registration_form_router
)
