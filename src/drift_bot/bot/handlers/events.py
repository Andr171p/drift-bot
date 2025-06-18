from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode

from dishka.integrations.aiogram import FromDishka as Depends

from ..states import EventForm
from ..enums import Confirmation, AdminEventAction
from ..callbacks import ConfirmCallback, AdminEventCallback
from ..keyboards import confirm_event_creation_kb, admin_event_actions_kb

from ...core.domain import Event
from ...core.services import EventService
from ...templates import EVENT_TEMPLATE, PILOT_TEMPLATE


events_router = Router(name=__name__)


@events_router.message(Command("create_event"))
async def send_event_form(message: Message, state: FSMContext) -> None:
    await state.set_state(EventForm.title)
    await message.answer("Введите название мероприятия: ")


@events_router.message(EventForm.title)
async def enter_event_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(EventForm.description)
    await message.answer("Добавьте описание (или нажмите /skip): ")


@events_router.message(EventForm.description)
async def enter_event_description(message: Message, state: FSMContext) -> None:
    if message.text.lower() != "/skip":
        await state.update_data(description=message.text)
    await state.set_state(EventForm.photo_id)
    await message.answer("Загрузите фото (в формате png, jpg, jpeg): ")


@events_router.message(EventForm.photo_id, F.photo)
async def enter_event_photo(message: Message, state: FSMContext) -> None:
    photo = message.photo[-1]
    photo_id = photo.file_id
    await state.update_data(photo_id=photo_id)
    await state.set_state(EventForm.location)
    await message.answer("Укажите место проведения: ")


@events_router.message(EventForm.location)
async def enter_event_location(message: Message, state: FSMContext) -> None:
    await state.update_data(location=message.text)
    await state.set_state(EventForm.map_link)
    await message.answer("Добавьте ссылку на карту (Google Maps, Яндекс.карты, 2Gis): ")


@events_router.message(EventForm.map_link)
async def enter_event_map_link(message: Message, state: FSMContext) -> None:
    await state.update_data(map_link=message.text)
    await state.set_state(EventForm.date)
    await message.answer("Укажите дату и время мероприятия (в формате Число.Месяц.Год Часы.Минуты): ")


@events_router.message(EventForm.date)
async def enter_event_date(message: Message, state: FSMContext) -> None:
    date = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
    await state.update_data(date=date)
    data = await state.get_data()
    text = EVENT_TEMPLATE.format(
        title=data["title"],
        description=data["description"],
        location=data["location"],
        map_link=data["map_link"],
        date=data["date"].strftime('%d.%m.%Y %H:%M')
    )
    await message.answer_photo(
        photo=data["photo_id"],
        caption=text,
        parse_mode=ParseMode.HTML,
    )
    await message.answer(
        text="Подтвердите создание мероприятия (Да/нет): ",
        reply_markup=confirm_event_creation_kb()
    )


@events_router.callback_query(ConfirmCallback.filter(F.confirmation == Confirmation.NO))
async def cancel_event_creation(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("❌ Создание отменено.")


@events_router.callback_query(ConfirmCallback.filter(F.confirmation == Confirmation.YES))
async def create_event(
        call: CallbackQuery,
        state: FSMContext,
        event_service: Depends[EventService]
) -> None:
    data = await state.get_data()
    event = Event(
        title=data["title"],
        description=data["description"],
        location=data["location"],
        map_link=data["map_link"],
        date=data["date"]
    )
    photo_file = await call.bot.get_file(file_id=data["photo_id"])
    photo_data = await call.bot.download(file=photo_file)
    photo_format = photo_file.file_path.split(".")[-1].lower()
    await event_service.create_event(event, photo_data=photo_data.read(), photo_format=photo_format)
    await call.message.answer("✅ Мероприятие создано!")


@events_router.message(Command("last_event"))
async def send_last_event(message: Message, event_service: Depends[EventService]) -> None:
    event = await event_service.get_last_event()
    text = EVENT_TEMPLATE.format(
        title=event.title,
        description=event.description,
        location=event.location,
        map_link=event.map_link,
        date=event.map_link
    )
    await message.answer_photo(
        photo=BufferedInputFile(file=event.photo_data, filename=f"{event.title}.jpg"),
        caption=text,
        reply_markup=admin_event_actions_kb(event_id=event.id, active=event.active)
    )


@events_router.callback_query(AdminEventCallback.filter(F.action == AdminEventAction.PILOTS_LIST))
async def send_event_pilots(
        call: CallbackQuery,
        callback_data: AdminEventCallback,
        event_service: Depends[EventService]
) -> None:
    has_pilots = False
    async for pilot in event_service.get_pilots(callback_data.event_id):
        has_pilots = True
        text = PILOT_TEMPLATE.format(
            full_name=pilot.full_name,
            age=pilot.age,
            description=pilot.description,
            car=pilot.car,
            created_at=pilot.created_at
        )
        await call.message.answer_photo(
            photo=BufferedInputFile(file=pilot.photo_data, filename=f"{pilot.full_name}.jpg"),
            caption=text
        )
    if not has_pilots:
        await call.message.answer("🚫 На это мероприятие не зарегистрировано ни одного пилота.")


@events_router.callback_query(
    AdminEventCallback.filter(F.action == AdminEventAction.TOGGLE_REGISTRATION)
)
async def toggle_registration(
        call: CallbackQuery,
        callback_data: AdminEventCallback,
        event_service: Depends[EventService]
) -> None:
    await event_service.toggle_registration(callback_data.event_id)
    event = await event_service.get_event(callback_data.event_id)
    text = EVENT_TEMPLATE.format(
        title=event.title,
        description=event.description,
        location=event.location,
        map_link=event.map_link,
        date=event.map_link
    )
    await call.message.answer_photo(
        photo=BufferedInputFile(file=event.photo_data, filename=f"{event.title}.jpg"),
        caption=text,
        reply_markup=admin_event_actions_kb(event_id=event.id, active=event.active)
    )

