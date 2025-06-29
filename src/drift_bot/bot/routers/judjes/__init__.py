__all__ = ("judges_router",)

from aiogram import Router

from .registration_form import registration_form_router

judges_router = Router()

judges_router.include_routers(
    registration_form_router,
)
