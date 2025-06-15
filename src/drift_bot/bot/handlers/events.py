from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from dishka.integrations.aiogram import FromDishka as Depends

from ...core.services import EventService

from ...constants import FIRST_PAGE, LIMIT
from ...templates import EVENT_TEMPLATE


events_router = Router()


@events_router.message(Command("events"))
async def get_events(message: Message, event_service: Depends[EventService]) -> None:
    for event in event_service.get_events(page=FIRST_PAGE, limit=LIMIT):
        if event.image is not None:
            await message.answer_photo(
                photo=event.image,
                caption=EVENT_TEMPLATE.format(**event.model_dump())
            )
        await message.answer(text=EVENT_TEMPLATE.format(**event.model_dump()))


@events_router.message(Command("last-event"))
async def get_last_event(message: Message, event_service: Depends[EventService]) -> None:
    event = await event_service.get_last_event()
    if event.image:
        await message.answer_photo(
            photo=event.image,
            caption=EVENT_TEMPLATE.format(**event.model_dump())
        )
    await message.answer(text=EVENT_TEMPLATE.format(**event.model_dump()))


@events_router.message(Command("create-event"))
async def send_event_creation_form(message: Message) -> None:
    ...
